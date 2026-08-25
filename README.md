# SOLTEX_ROUTER Agent SDK
**Fund one treasury. Run 10,000 autonomous agents.**

Solana's first zero-gas, MEV-protected intent router for AI Agents.

Stop manually funding hundreds of bot wallets with SOL dust. `soltex router` is a meta-routing SDK that completely abstracts gas fees and Jito tips, allowing your AI agents to execute swaps with 0.0000 SOL balance.

##The current service is incomplete, please wait until the service officially launches

## ⚡ Why SOLTEX Router?

### ❌ The Old Way (Painful)
Managing 50 AI trading bots meant funding 50 separate Keypairs with SOL, calculating dynamic priority fees, guessing Jito tip percentiles, and handling RPC rate limits.

### ✅ The SOLTEX Way (Intent-Centric)
Deposit SOL into a single Treasury Dashboard. Your agents just sign the intent locally. The SOLTEX Backend sponsors the transaction, auto-injects the 75th-percentile priority fee, routes through Jito Block Engine, and broadcasts it.

## 🔥 Core Features
- ⛽ **Absolute Gas Abstraction:** Bots can operate with completely empty wallets.
- 🛡️ **Default MEV Protection:** 100% of transactions are routed via Jito Block Engine. Zero sandwich attacks.
- 🔀 **Jupiter API Native:** Built-in wrapper for optimal swap routes and instant execution.
- 🔒 **Trustless Architecture:** Your agent's private key never leaves the local environment. We only receive a locally `partial_signed` payload.

## 📦 Installation

```bash
pip install soltex-router
```

## 🚀 1-Minute Quick Start
Look how incredibly simple it is to swap tokens without worrying about gas fees. 

> ⚠️ IMPORTANT NOTE: Your agent's wallet needs 0 SOL - SOLTEX automatically sponsors all gas fees and ATA rent. Your wallet only needs to hold the tokens you want to swap (e.g., 10 USDC).
> How Auto-Funding Works:
> If your bot wallet has less than 0.005 SOL, SOLTEX automatically deposits 0.005 SOL to cover transaction costs. This funding remains in your wallet until depleted. SOLTEX will not send additional SOL until your balance drops below the 0.005 SOL threshold again.


> ⚠️ First Swap Behavior:
> If your wallet starts with 0 SOL, the first swap may be dropped (not executed) while SOLTEX deposits the 0.005 SOL. Subsequent swaps will succeed normally. This is a one-time initialization cost.

```python
import logging
from solders.keypair import Keypair
from soltex_router import AgentRouter

logging.basicConfig(level=logging.INFO)

# 1. Load your AI agent's wallet
# (Ensure this wallet holds the USDC you want to swap. 0 SOL is perfectly fine!)
# but receiving a BRAND NEW token type may require ~0.002 SOL for ATA creation rent!)
PRIVATE_KEY_BASE58 = "your_agent_private_key"
bot_wallet = Keypair.from_base58_string(PRIVATE_KEY_BASE58)
print(f"Agent Wallet: {bot_wallet.pubkey()}")

# 2. Connect to SOLTEX
router = AgentRouter(
    api_key="SOLTEX_your_actual_api_key",  # Issued via SOLTEX Dashboard (https://soltex-router.com/)
    payer=bot_wallet,
    rpc_url="https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY",
    server_url="https://api.soltex-router.com"
)

def main():
    # 3. Execute Swap via Jupiter (Zero SOL required for gas or tips!)
    print("\nSwapping 10 USDC → SOL...")
    result = router.swap(
        input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", # USDC
        output_mint="So11111111111111111111111111111111111111112", # SOL
        amount=10_000_000, # 10 USDC
        slippage_bps=100   # 1% slippage
    )

    if result["success"]:
        print(f"\n✅ Gasless Swap Confirmed!")
        print(f"TX Hash: {result['tx_hash']}")
        print(f"Explorer: https://solscan.io/tx/{result['tx_hash']}")
    else:
        print(f"\n❌ Swap failed: {result['error']}")

if __name__ == "__main__":
    main()
```

🔒 Security & ToS
By using this SDK, you agree to the SOLTEX Terms of Service.
Open Source: This client SDK is 100% transparent. Inspect the code to verify that keys remain strictly on your machine.

## ⚖️ Legal & Compliance
- [Terms of Service](./TERMS.md)

## More information
- [Detailed Guide](./guide.md)

**Disclaimer**: This software is provided "AS IS". Use at your own risk. 
Not financial advice. Not a custodial service.

website: https://soltex-router.com/
contact: soltex_router@protonmail.com
