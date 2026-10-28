# Lab 5 - Reflection Report

## 1. Which tool was the most useful for this program, and why?

Bandit was the most useful tool for security. It found three dangerous risks:
- The code used FTP to transfer data. FTP sends passwords in clear text.
- The code used `marshal` to read data files. `marshal` can parse unsafe data.
- The code stored a hardcoded password in a function definition.

Pylint was the most useful tool for code quality. It raised the score from 5.17 to 10.00:
- It found a mutable default list argument (`history=[]`).
- It found open file handles that the code did not close.
- It found unnecessary use of the `global` statement.

Flake8 helped with style. It ensured that all lines follow PEP 8 rules.

## 2. Did any of the tools produce a false positive? How did you decide?

Bandit reported low-severity warnings for `subprocess` and `random`.
These warnings were not critical bugs in this script:
- The script used `random` only to make display IDs.
- The script called `subprocess` with a list, not with `shell=True`.

However, we did not ignore these warnings. We replaced the functions:
- We used `secrets.randbelow` to make random IDs.
- We used `smtplib` to send emails directly without external processes.

This step removed the security risk completely.
Rule: If a fix is simple and clean, fix the code. Do not suppress warnings without a valid technical reason.

## 3. What problems did the tools NOT catch?

Static analysis tools check code syntax and style. They do not check business logic or math.
The tools did not catch these five errors:

1. **Wrong interest rate in demo:**
   The demo passed `9` instead of `0.09` for a 9% rate. This caused an EMI of 375,000 on a 500,000 loan.

2. **Incorrect eligibility logic:**
   The function returned `True` early if income was above 25,000. It approved invalid loans like "crypto". It also ignored the debt ratio check.

3. **Wrong loan calculation:**
   The function `max_loan_amount` ignored the interest rate. It added monthly payments without interest formulas.

4. **Invalid credit score accepted:**
   The function `risk_band` accepted a score of 950. Valid credit bureau scores stop at 900.

5. **Duplicate application IDs:**
   The code did not check if a generated ID already existed in the dictionary.

You must write unit tests to find these logic bugs. Static analysis cannot replace testing.

## 4. How would you use static analysis in a real project?

Use static analysis tools in every project pipeline:

1. **Pre-commit hooks:**
   Run Flake8 before every commit. This keeps code formatting clean.

2. **Continuous Integration (CI):**
   Run Bandit and Pylint on every pull request.
   - Fail the build if Bandit finds High or Medium security issues.
   - Fail the build if the Pylint score falls below 9.0.

3. **Team standards:**
   Define project rules in a shared config file (`.pylintrc`).
   If you must ignore a rule, write an inline comment and explain why.
