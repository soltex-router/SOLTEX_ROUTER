# SOLTEX Router Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install solders requests
pip install soltex-router
```

### 2. Get API Key

1. Visit [soltex-router.com](https://soltex-router.com)
2. Connect Phantom Wallet
3. Click **"Issue API Key"**
4. Copy your `SOLTEX_xxxxxxxx` key

>⚠️ IMPORTANT NOTE: Your agent's wallet needs 0 SOL - SOLTEX automatically sponsors all gas fees and ATA rent. Your wallet only needs to hold the tokens you want to swap (e.g., 10 USDC).
How Auto-Funding Works: If your bot wallet has less than 0.005 SOL, SOLTEX automatically deposits 0.005 SOL to cover transaction costs. This funding remains in your wallet until depleted. SOLTEX will not send additional SOL until your balance drops below the 0.005 SOL threshold again.

### 3. First Swap

```python
import logging
from solders.keypair import Keypair
from soltex_router import AgentRouter

logging.basicConfig(level=logging.INFO)

# Your agent's wallet (0 SOL is fine!)
bot_wallet = Keypair.from_base58_string("YOUR_PRIVATE_KEY_BASE58")

router = AgentRouter(
    api_key="SOLTEX_your_api_key",
    payer=bot_wallet,
    rpc_url="https://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_KEY",
    server_url="https://api.soltex-router.com"
)

# Swap 10 USDC → SOL
result = router.swap(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount=10_000_000,   # 10 USDC (6 decimals)
    slippage_bps=100     # 1% slippage
)

if result["success"]:
    print(f"✅ Swap confirmed: {result['tx_hash']}")
    print(f"Explorer: https://solscan.io/tx/{result['tx_hash']}")
else:
    print(f"❌ Failed: {result['error']}")
```

---

## Swap Examples

### SOL → USDC

```python
result = router.swap(
    input_mint="So11111111111111111111111111111111111111112",  # SOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=1_000_000_000,  # 1 SOL (9 decimals)
    slippage_bps=50        # 0.5%
)
```

### USDC → SOL

```python
result = router.swap(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount=100_000_000,  # 100 USDC
    slippage_bps=100
)
```

### Token → Token (USDC → WETH)

```python
result = router.swap(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",  # WETH
    amount=500_000_000,  # 500 USDC
    slippage_bps=150     # 1.5%
)
```

### Snipe a New Token (High Slippage)

```python
result = router.swap(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="NEW_TOKEN_MINT_ADDRESS",
    amount=100_000_000,  # 0.1 SOL
    slippage_bps=500     # 5% for volatile launches
)
```

---

## Token Mint Reference

| Token | Mint Address | Decimals |
|---|---|---|
| SOL | `So11111111111111111111111111111111111111112` | 9 |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 |
| WETH | `7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs` | 8 |
| WBTC | `3NZ9JMVBmGAqocyB2xER4FzA3b3arXB3F1vH4p7o8wD9` | 8 |

**Amount formula**: `amount = display_value × 10^decimals`

Example: 1.5 USDC = `1_500_000` (1.5 × 10⁶)

---

## Transfers (Non-Swap)

### Send SOL

```python
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams

ix = transfer(
    TransferParams(
        from_pubkey=bot_wallet.pubkey(),
        to_pubkey=Pubkey.from_string("RECIPIENT_WALLET"),
        lamports=1_000_000_000  # 1 SOL
    )
)

result = router.send(instructions=[ix])
```

### Send SPL Token (USDC)

```python
import struct
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

def spl_transfer(from_ata, to_ata, owner, amount):
    return Instruction(
        TOKEN_PROGRAM_ID,
        [
            AccountMeta(from_ata, False, True),
            AccountMeta(to_ata, False, True),
            AccountMeta(owner, True, False),
        ],
        struct.pack("<BQ", 3, amount)  # 3 = Transfer discriminator
    )

# Find ATA addresses first (use spl-token package or explorer)
ix = spl_transfer(
    from_ata=Pubkey.from_string("YOUR_USDC_ATA"),
    to_ata=Pubkey.from_string("RECIPIENT_USDC_ATA"),
    owner=bot_wallet.pubkey(),
    amount=10_000_000  # 10 USDC
)

result = router.send(instructions=[ix])
```

---

## Custom Instructions

Any Solana program interaction works:

```python
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey

ix = Instruction(
    program_id=Pubkey.from_string("YOUR_PROGRAM_ID"),
    accounts=[
        AccountMeta(bot_wallet.pubkey(), True, True),
        AccountMeta(Pubkey.from_string("SOME_ACCOUNT"), False, True),
    ],
    data=b"\x01\x02\x03\x04"  # Program-specific instruction data
)

result = router.send(instructions=[ix])
```

**Constraints:**
- Max 10 instructions per transaction
- Fee payer must be your wallet or server wallet
- Whitelisted programs: System, Token, ATA, ComputeBudget, Jupiter, Memo

---

## Pricing

### Architecture: Dual-Wallet System

| Wallet | Role | Billing |
|---|---|---|
| **Dashboard Wallet** | API key owner, credit deposits | ✅ Costs deducted here |
| **Bot Wallet** | Executes swaps, signs transactions | ✅ Gas sponsored here |

One API key can operate multiple bots. All costs are billed to the dashboard wallet's credits.

### Jupiter Swap (`router.swap`)

| Component | Cost |
|---|---|
| Server Gas Cost | 15,000 lamports (fixed) |
| Jito Tip | Market rate (dynamic, 100k-500k lamports typical) |
| Service Margin | 20% |

**Formula**: `cost = (jito_tip + 15,000) × 1.20`

**Typical**: 138,000 - 618,000 lamports per swap (0.000138 - 0.000618 SOL)

### Custom Transaction (`router.send`)

| Component | Cost |
|---|---|
| Base Fee | 5,000 lamports (fixed) |
| Priority Fee | Market rate (dynamic) |
| Jito Tip | Market rate (if included) |
| Service Margin | 20% |

**Formula**: `cost = (jito_tip + priority_fee + 5,000) × 1.20`

### Check Balance

```bash
curl "https://api.soltex-router.com/api/balance?api_key=YOUR_KEY"
# Response: {"balance_lamports": 5000000}
```

---

## Security

- ✅ **Non-custodial**: Private keys never leave your machine
- ✅ **Co-Signer Drain Protection**: Server validates all instructions
- ✅ **Rate Limiting**: 15 requests per 60 seconds per wallet
- ✅ **Program Whitelisting**: Only approved programs execute
- ⚠️ **Keep API keys secret**: Treat them like passwords

---

## Automatic Retry

The SDK automatically retries up to 3 times for:
- Blockhash expiration (immediate retry)
- Rate limiting (exponential backoff: 1s, 2s, 4s)

You can customize: `AgentRouter(..., max_retries=5)`

---

## Error Messages

| Error | Meaning |
|---|---|
| `Blockhash expired` | Blockhash outdated, SDK retries automatically |
| `Rate limited` | Too many requests, SDK waits and retries |
| `Server 401` | Invalid API key |
| `Server 402` | Insufficient credits |
| `Server 429` | Rate limit exceeded |
| `Server 500` | Server-side failure |

```python
result = router.swap(...)

if result["success"]:
    tx_hash = result["tx_hash"]
else:
    error = result["error"]
    if "rate limit" in error.lower():
        time.sleep(60)
    elif "insufficient" in error.lower():
        print("Need to deposit credits")
```

---

## FAQ

**Q: Do I need SOL in my wallet?**
A: No. Server sponsors gas. However, receiving a NEW token type may require ~0.002 SOL for ATA rent.

**Q: What if Jito is down?**
A: Automatic fallback to standard RPC. MEV protection is best-effort.

**Q: Can I use this for arbitrage bots?**
A: Yes. Typical latency: 500-800ms.

**Q: What happens if my swap fails on-chain?**
A: Credits are refunded automatically within 10 minutes (minus 10k lamport spam penalty).

**Q: Can I revoke my API key?**
A: Yes. Dashboard → "Revoke Key". Remaining credits are non-refundable.

---

## Support

- Email: soltex_router@protonmail.com
- Status: https://soltex-router.com/health

---

**© SOLTEX ROUTER**
