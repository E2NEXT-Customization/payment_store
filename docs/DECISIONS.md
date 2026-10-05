# Architecture & Design Decisions

## Phase 1: Scaffold
- **Decision:** Used Frappe's `bench execute` with python script to seed initial Workspaces and roles to simplify scaffolding. Extracted the core to `install.py` to keep fresh installs working.
- **Decision:** Added fixtures for `Role` and `Workspace` to ensure they track with the code. Tests are explicitly running with `--module` to avoid bleeding into standard Frappe tests.
## Phase 3: Ledger, WAC & Exchange Deal
- **Decision:** Segregated WAC (Weighted Average Cost) and posting logic into the `accounting/` directory (`wac.py`, `posting.py`) to keep the `Exchange Deal` controller lightweight and easily testable.
- **Decision:** Leveraged Frappe's unique property on `idempotency_key` in `Cashbox Ledger Entry` and `Exchange Deal` to enforce idempotency at the database layer.

## Phase 4: Cashbox Transaction & Customer Accounts
- **Decision:** Injected a Custom Field `ps_currency_accounts` (Customer Currency Account child table) into the standard `Customer` DocType instead of creating a separate parallel DocType. This keeps the UX unified and avoids duplication.
- **Decision:** Added `Cashbox Transaction` with logic to support two-step transfers (via `transfer_status` and `incoming_transfer_reference`) built into the schema.

## Phase 5: Desks & Workspace UI
- **Decision:** Scaffolded all required desk Pages natively in Frappe and linked them to `Payment Store Manager` and `Payment Store Cashier` roles.
- **Decision:** Extracted common desk component logic into a central reusable library `ps_desk_core.js` injected globally via `hooks.py`, ensuring consistent RTL, mobile-first design across all desks.
