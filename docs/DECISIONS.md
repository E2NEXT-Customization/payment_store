# Architecture & Design Decisions

## Strict Pivot (Section 3 rule applied)
- **Decision:** Removed all micro-DocTypes (Reconciliation, Watchlist, Overrides, Ledger) and fully embraced the 6-DocType limit. Frappe GL Entries act as the sole ledger. Watchlist/Overrides are handled via compliance fields natively in the Deal and Settings.

## Phase 1 & 2: Scaffold, Settings, Rates & Cashbox
- **Decision:** Used a unified setup script to structure the exact 6 allowed DocTypes (and their native child tables).
- **Decision:** `Cashbox` relies on `locked_until` (set by closing) to prevent backdated entries, effectively functioning as a "Session" boundary without creating a separate DocType.

## Phase 3: Exchange Deal, WAC, and JE Posting
- **Decision:** Implemented Weighted Average Cost (WAC) logic directly in the `Exchange Deal` controller. WAC is stored in `Payment Store Settings` per currency and updated via a strict `FOR UPDATE` lock to guarantee atomicity.
- **Decision:** Multi-currency Journal Entries are posted synchronously `on_submit` and reversed perfectly `on_cancel` restoring the exact `wac_before` snapshot.
