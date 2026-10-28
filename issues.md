# Lab 5 - Issues found and fixed (loan_calculator.py)

Reports: `reports/before/` (original code) and `reports/after/` (final code).
Pylint 5.17/10 -> 10.00/10, Bandit 8 findings -> 0, Flake8 ~20 findings -> 0.

Line numbers refer to the **original** file.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| FTP used for uploads (B402, B321) | Security (High) | 3, 68 | `ftplib` sends credentials and report data in clear text. | Replaced with an HTTPS `PUT` via `http.client.HTTPSConnection`. |
| `marshal` for storing/loading applications (B302) | Security (Medium) | 4, 56, 64 | `marshal.loads` on a file can execute/crash on crafted data and the format is Python-version specific. | Store the loan book as JSON (`json.dump` / `json.load`). |
| Hardcoded password (B107) | Security (Low) | 67 | `password="Bureau#2024"` default argument leaks a credential in source control. | Defaults are `None`; credentials read from `BUREAU_USER` / `BUREAU_PASSWORD` environment variables. |
| `subprocess` calling `mail` (B404, B603, B607) | Security (Low) | 6, 74 | Partial executable path and shell-out with user-supplied e-mail address. | Use `smtplib` + `EmailMessage`; no subprocess. |
| `random` for application IDs (B311) | Security (Low) | 51 | Predictable PRNG for identifiers. | `secrets.randbelow`, plus a uniqueness check against existing IDs. |
| Files not closed / no encoding (R1732) | Bug | 55-57, 62-65, 70 | Resource leaks if an exception occurs between `open` and `close`. | `with open(..., encoding="utf-8")`. |
| Mutable default argument (W0102) | Bug | 20 | `history=[]` is shared across calls and grows forever; it was never used. | Parameter removed. |
| `global` statement (W0603) | Design | 62 | `load_applications` rebinds a module global. | `clear()` + `update()` on the existing dict. |
| Builtin `sum` shadowed, unused loop var (W0622, W0612) | Quality | 34, 36 | Local named `sum` hides the builtin. | Renamed to `total` / replaced with `_`; function later rewritten (see logic bugs). |
| Non snake_case names, missing docstrings (C0103, C0114, C0116) | Style | 14-93 | camelCase function names; no module/function docstrings. | Renamed all functions, added docstrings. |
| Unused import `math`, empty f-string (F401, F541 / W0611, W1309) | Style | 2, 104 | Dead import and f-string without placeholders. | Removed. |
| PEP 8 layout (E302, E305, E501) | Style | many | Missing blank lines, lines > 79 chars. | Reformatted to 79 columns. |
| `main()` runs on import | Bug | 106 | Importing the module runs the demo and writes files. | `if __name__ == "__main__":` guard. |
| Rate unit mismatch in demo | Logic bug (not tool-detectable) | 94 | `calculate_emi(500000, 9, 5)` passes 9 instead of 0.09 -> EMI 375000 (that is 75% of principal per month). | Pass `0.09`; also handle 0% rate (division by zero). |
| Eligibility short-circuit | Logic bug | 25-26 | `credit_score > 750 or income > 25000` returned True before the FOIR and loan-type checks, so "crypto" loans and 80% FOIR were approved; `income == 0` would divide by zero. | Validate loan type, age, income and FOIR first; invalid scores rejected. |
| Max loan ignores interest | Logic bug | 33-38 | Just summed monthly capacity (900000 for 5 yrs) and never used `annual_rate`. | Present value of an annuity: `available * (1 - (1+r)^-n) / r`. |
| Risk band accepts score 950 | Logic bug | 81-90 | Credit scores are 300-900, but 950 returned "LOW". | Scores above 900 return "INVALID". |
| Application ID collisions | Logic bug | 50-54 | Random id could overwrite an existing application. | Regenerate while the id already exists. |
