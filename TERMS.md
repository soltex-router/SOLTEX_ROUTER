## 1. Non-Custodial Architecture
SOLTEX Router is a **non-custodial intent-routing protocol**. 
- We **never** hold, custody, or have access to your private keys.
- Deposited funds are held in a secure Treasury wallet (backed by automated cold-storage sweeps), credited to your API key as off-chain lamports.
- You retain full sovereignty over your signing keys at all times.

## 2. Gas Abstraction Risks
By using SOLTEX, you acknowledge:
- **Server Solvency Risk**: Gas sponsorship depends on the server's hot wallet balance. In extreme network congestion, transactions may be delayed or dropped.
- **Credit != On-chain SOL**: Your `balance_lamports` is an off-chain credit. It represents our obligation to sponsor gas, not a 1:1 redeemable token.
- **No SLA Guarantee**: We target 99.9% uptime but provide no contractual SLA during beta.

## 3. MEV Protection (Best-Effort)
- Transactions are aggressively routed via **Global Jito Block Engine** nodes to utilize private mempools.
- To guarantee high execution rates, we employ a "Double-Tap" architecture that may fallback to public RPCs if Jito routing fails.
- This **significantly reduces** but does **not mathematically eliminate** sandwich attack vectors. Malicious validators or public mempool exposure during fallback may still observe flow.

## 4. Upstream Protocol Risk
- Jupiter Aggregator routes and Oracles (Price APIs) are third-party infrastructure.
- We are not liable for slippage, failed swaps, or oracle manipulation on upstream protocols.
- **Spam Penalty**: Intentionally failing transactions incurs a 10,000 lamports penalty to protect network integrity.

## 5. Key Revocation & Fund Recovery
- You may revoke your API key at any time via the dashboard.
- Remaining credits are **non-refundable to on-chain SOL** after revocation (service credit model).
- Orphaned deposits (no valid API key in Memo) are held for 90 days, then donated to protocol treasury.

## 6. Limitation of Liability
TO THE MAXIMUM EXTENT PERMITTED BY LAW, SOLTEX LABS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING FROM USE OF THIS PROTOCOL.

---
Contact: soltex_router@protonmail.com
