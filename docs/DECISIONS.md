# Architecture & Design Decisions

## Phase 1: Scaffold
- **Decision:** Used Frappe's `bench execute` with python script to seed initial Workspaces and roles to simplify scaffolding. Extracted the core to `install.py` to keep fresh installs working.
- **Decision:** Added fixtures for `Role` and `Workspace` to ensure they track with the code. Tests are explicitly running with `--module` to avoid bleeding into standard Frappe tests.
