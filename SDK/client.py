"""
solana-agent-router | Client SDK v0.3.0
Copyright (c) 2026 SOLTEX Labs. MIT License.

⚠️ BY USING THIS SDK, YOU AGREE TO THE TERMS IN TERMS.md
- Non-custodial: Your keys never leave your machine
- Best-effort MEV protection via Jito Block Engine
- Gas sponsorship is a service credit, not a deposit account
"""
import time, logging, base64
from typing import Optional, List
import requests
import uuid
import base58

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction, VersionedTransaction
from solders.message import Message
from solders.instruction import Instruction
from solders.signature import Signature
from solders.compute_budget import set_compute_unit_price
from solders.system_program import TransferParams, transfer
from solders.hash import Hash

logger = logging.getLogger("solana-agent-router-sdk")

class BlockhashExpiredError(Exception): pass
class RateLimitError(Exception): pass
class RouterError(Exception): pass

class AgentRouter:
    def __init__(self, api_key, payer: Keypair, rpc_url, server_url, max_retries=3):
        self.api_key = api_key
        self.payer = payer
        self.rpc_url = rpc_url
        self.server_url = server_url.rstrip("/")
        self.max_retries = max_retries

    def swap(self, input_mint, output_mint, amount, slippage_bps=50):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                blockhash = self._get_recent_blockhash()
                resp = requests.post(
                    f"{self.server_url}/api/v1/build-swap",
                    json={
                        "inputMint": input_mint,
                        "outputMint": output_mint,
                        "amount": amount,
                        "slippageBps": slippage_bps,
                        "user_wallet": str(self.payer.pubkey()),
                        "recent_blockhash": str(blockhash),
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                tx_b58 = data["tx_bytes"]
                request_id = data["request_id"]
                tx_bytes = base58.b58decode(tx_b58)
                vtx = VersionedTransaction.from_bytes(tx_bytes)
                msg = vtx.message

                payer_str = str(self.payer.pubkey())
                signer_idx = None
                for i in range(msg.header.num_required_signatures):
                    if str(msg.account_keys[i]) == payer_str:
                        signer_idx = i
                        break
                if signer_idx is None:
                    raise RuntimeError("Payer not in signers")

                num_sigs = tx_bytes[0]
                if signer_idx >= num_sigs:
                    raise RuntimeError(f"Edge case detected: signer_idx ({signer_idx}) >= num_sigs ({num_sigs})")

                num_sigs = tx_bytes[0]
                msg_start = 1 + (num_sigs * 64)
                msg_bytes = tx_bytes[msg_start:]

                user_sig = self.payer.sign_message(msg_bytes)

                sig_start = 1 + (signer_idx * 64)
                sig_end = sig_start + 64
                new_tx_bytes = tx_bytes[:sig_start] + bytes(user_sig) + tx_bytes[sig_end:]

                print(f"[CLIENT] Signatures injected directly! req_id: {request_id[:16]}...")

                result = self._post_route(new_tx_bytes, request_id)
                if result.get("status") == "confirmed":
                    logger.info("Swap confirmed: %s (method=%s)", result["tx_hash"], result.get("method"))
                    return {"success": True, "tx_hash": result["tx_hash"]}
                last_error = result.get("error")

            except BlockhashExpiredError:
                logger.warning("Attempt %d: blockhash expired", attempt + 1)
                last_error = "Blockhash expired"
                continue
            except RateLimitError:
                wait = 2 ** attempt
                logger.warning("Attempt %d: rate limited, wait %ds", attempt + 1, wait)
                time.sleep(wait)
                last_error = "Rate limited"
                continue
            except requests.exceptions.HTTPError as e:
                last_error = str(e)
                logger.error("Attempt %d: HTTP error: %s", attempt + 1, e)
                break
            except Exception as e:
                last_error = str(e)
                logger.error("Attempt %d: error: %s", attempt + 1, e)
                break

        return {"success": False, "error": last_error or "Max retries"}

    def send(self, instructions: List[Instruction], additional_signers=None):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                params = self._get_params()
                request_id = uuid.uuid4().hex
                tx = self._build_transaction(instructions, params, additional_signers)
                result = self._post_route(bytes(tx), request_id)
                if result.get("status") == "confirmed":
                    return {"success": True, "tx_hash": result["tx_hash"]}
                last_error = result.get("error")
            except BlockhashExpiredError:
                last_error = "Blockhash expired"
                continue
            except RateLimitError:
                time.sleep(2 ** attempt)
                last_error = "Rate limited"
                continue
            except Exception as e:
                last_error = str(e)
                break
        return {"success": False, "error": last_error or "Max retries"}

    def _build_transaction(self, instructions, params, additional_signers=None):
        fee_payer = Pubkey.from_string(params["fee_payer"])
        tip_addr = Pubkey.from_string(params["jito_tip_address"])

        tip_ix = transfer(TransferParams(
            from_pubkey=fee_payer, to_pubkey=tip_addr,
            lamports=params["jito_tip_lamports"]
        ))
        priority_ix = set_compute_unit_price(params["priority_fee_lamports"])

        all_ixs = [tip_ix, priority_ix] + instructions
        blockhash = self._get_recent_blockhash()
        msg = Message.new_with_blockhash(all_ixs, fee_payer, blockhash)
        msg_bytes = bytes(msg)

        all_signers = [self.payer] + (additional_signers or [])
        signer_map = {str(kp.pubkey()): kp for kp in all_signers}

        signatures = []
        for pubkey in msg.account_keys[:msg.header.num_required_signatures]:
            pk_str = str(pubkey)
            if pk_str in signer_map:
                signatures.append(signer_map[pk_str].sign_message(msg_bytes))
            else:
                signatures.append(Signature.default())

        return Transaction.populate(msg, signatures)

    def _get_params(self):
        resp = requests.get(
            f"{self.server_url}/api/v1/params",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def _post_route(self, tx_bytes, request_id):
        resp = requests.post(
            f"{self.server_url}/api/v1/route",
            json={
                "signed_tx": base64.b64encode(tx_bytes).decode(),
                "api_key": self.api_key,
                "request_id": request_id,
            },
            timeout=65,
        )
        if resp.status_code == 408:
            raise BlockhashExpiredError("blockhash expired")
        if resp.status_code == 429:
            raise RateLimitError("rate limit")
        if resp.status_code != 200:
            raise RouterError(f"Server {resp.status_code}: {resp.text}")
        return resp.json()

    def _get_recent_blockhash(self):
        resp = requests.post(self.rpc_url, json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getLatestBlockhash",
            "params": [{"commitment": "confirmed"}]
        }, timeout=10)
        resp.raise_for_status()
        return Hash.from_string(resp.json()["result"]["value"]["blockhash"])
