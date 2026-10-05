# Architecture & Design Decisions

## Phase 1: Scaffold
- **Decision:** Used Frappe's `bench execute` with python script to seed initial Workspaces and roles to simplify scaffolding. Extracted the core to `install.py` to keep fresh installs working.
- **Decision:** Added fixtures for `Role` and `Workspace` to ensure they track with the code. Tests are explicitly running with `--module` to avoid bleeding into standard Frappe tests.
## Phase 3: Ledger, WAC & Exchange Deal
- **Decision:** Segregated WAC (Weighted Average Cost) and posting logic into the `accounting/` directory (`wac.py`, `posting.py`) to keep the `Exchange Deal` controller lightweight and easily testable.
- **Decision:** Leveraged Frappe's unique property on `idempotency_key` in `Cashbox Ledger Entry` and `Exchange Deal` to enforce idempotency at the database layer.
