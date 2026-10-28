"""Loan eligibility and EMI calculator for a bank loan desk."""

import os
import json
import base64
import secrets
import smtplib
import http.client
from email.message import EmailMessage
from datetime import datetime

# Global loan book
applications = {}
MAX_FOIR = 0.5
BUREAU_HOST = "api.creditbureau.example"


def calculate_emi(principal, annual_rate, years):
    """Return the monthly instalment (EMI) for a loan."""
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def check_eligibility(age, income, credit_score, existing_emi, loan_type):
    """Return True if the applicant qualifies for the given loan type."""
    if loan_type not in ("home", "car", "personal"):
        return False
    if age < 21 or age > 60 or income <= 0:
        return False
    if risk_band(credit_score) == "INVALID":
        return False
    return existing_emi / income <= MAX_FOIR


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Return the largest principal whose EMI fits the FOIR limit."""
    available = income * MAX_FOIR - existing_emi
    if available <= 0:
        return 0
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return available * n
    return available * (1 - (1 + r) ** -n) / r


def amortisation_schedule(principal, annual_rate, years):
    """Return (month, interest, balance) rows for the whole loan term."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance = balance - (emi - interest)
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows


def application_id():
    """Return a random application id such as LN-12345678."""
    return "LN-" + str(10000000 + secrets.randbelow(90000000))


def save_application(name, amount, file="loans.json"):
    """Record an application, persist the loan book and return its id."""
    app_id = application_id()
    while app_id in applications:
        app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now()),
    }
    with open(file, "w", encoding="utf-8") as f:
        json.dump(applications, f)
    return app_id


def load_applications(file="loans.json"):
    """Replace the in-memory loan book with the one stored in file."""
    with open(file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    applications.clear()
    applications.update(loaded)


def upload_to_bureau(report_path, user=None, password=None):
    """Upload a report to the credit bureau over HTTPS; return HTTP status."""
    # Credentials come from the environment, never from source code.
    user = user or os.environ["BUREAU_USER"]
    password = password or os.environ["BUREAU_PASSWORD"]
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    with open(report_path, "rb") as report:
        body = report.read()
    conn = http.client.HTTPSConnection(BUREAU_HOST, timeout=30)
    try:
        conn.request(
            "PUT",
            "/upload/" + os.path.basename(report_path),
            body,
            {"Authorization": "Basic " + token},
        )
        return conn.getresponse().status
    finally:
        conn.close()


def notify_applicant(email, status):
    """E-mail the applicant about the status of their application."""
    msg = EmailMessage()
    msg["Subject"] = "Loan " + status
    msg["To"] = email
    msg["From"] = "loans@bank.example"
    msg.set_content("Your loan application status: " + status)
    with smtplib.SMTP("localhost") as smtp:
        smtp.send_message(msg)


def interest_saved(principal, annual_rate, years, prepayment):
    """Return the total interest saved by prepaying part of the principal."""
    original = calculate_emi(principal, annual_rate, years) * years * 12
    reduced = (
        calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    )
    return original - reduced


def risk_band(credit_score):
    """Map a credit score to a risk band."""
    if credit_score > 900:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    if credit_score >= 300:
        return "VERY HIGH"
    return "INVALID"


def main():
    """Run a short demo of the calculator."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 0.09, 5))
    print(
        "Eligible (score 760, income 15000, EMIs 12000):",
        check_eligibility(35, 15000, 760, 12000, "personal"),
    )
    print(
        "Eligible (unknown loan type 'crypto'):",
        check_eligibility(30, 80000, 650, 0, "crypto"),
    )
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 0.09, 5))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print(
        "Interest saved by prepaying 50000:",
        interest_saved(500000, 0.09, 5, 50000),
    )
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")


if __name__ == "__main__":
    main()
