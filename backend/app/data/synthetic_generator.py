"""
Synthetic Transaction Dataset Generator for RecoveryOS

Generates 20,000 realistic e-commerce and fintech payment failure events
spanning UPI, Credit/Debit Cards, NetBanking, and Wallets in the Indian payment ecosystem.
"""
import json
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

FAILURE_PROFILES = [
    # (failure_code, failure_reason, payment_methods, base_prob, default_amount_range)
    ("GATEWAY_TIMEOUT", "Bank switch timeout during NPCI settlement", ["UPI", "NETBANKING"], 0.28, (299, 4500)),
    ("BAD_REQUEST_PAYMENT_TIMED_OUT", "User session expired waiting for gateway ack", ["UPI", "CARD"], 0.16, (499, 3500)),
    ("UPI_COLLECT_TIMEOUT", "Customer did not approve UPI collect request on mobile app within 8 mins", ["UPI"], 0.14, (199, 2999)),
    ("INSUFFICIENT_FUNDS", "Account balance insufficient for authorization", ["UPI", "CARD"], 0.12, (800, 8500)),
    ("AUTHENTICATION_FAILED", "Incorrect OTP entered or 3DS verification dismissed", ["CARD", "NETBANKING"], 0.10, (1200, 12000)),
    ("CART_DROPOFF", "Customer abandoned checkout screen before final redirection", ["UPI", "CARD", "WALLET"], 0.08, (500, 4500)),
    ("CARD_EXPIRED", "Card expiration date is in the past", ["CARD"], 0.04, (350, 6000)),
    ("ACCOUNT_CLOSED_OR_BLOCKED", "Beneficiary or customer VPA frozen by issuer", ["UPI", "NETBANKING"], 0.03, (500, 7500)),
    ("HIGH_RISK_SUSPECTED", "Abnormal IP velocity and device mismatch flagged by risk radar", ["CARD"], 0.03, (8000, 45000)),
    ("SUSPECTED_CARD_TESTING", "Repeated micro-transactions from spoofed proxy network", ["CARD"], 0.02, (100, 1200)),
]

MERCHANTS = [
    ("merch_lenskart_prod", "Lenskart Optical"),
    ("merch_zomato_pay", "Zomato Quick Commerce"),
    ("merch_swiggy_instamart", "Swiggy Instamart"),
    ("merch_boat_lifestyle", "boAt Audio Direct"),
    ("merch_nykaa_retail", "Nykaa Fashion"),
    ("merch_urban_company", "Urban Company Services"),
]

def generate_synthetic_transactions(count: int = 20000, output_path: str = None) -> List[Dict[str, Any]]:
    """
    Generates realistic payment failure events with customer tenure, risk scores, and failure types.
    """
    random.seed(20260904)  # Deterministic seed (2026-09-04) for scientific reproducibility and held-out evaluation
    transactions = []
    base_time = datetime(2026, 9, 1, 0, 0, 0)

    # Weights for failure profiles
    weights = [p[3] for p in FAILURE_PROFILES]

    for i in range(1, count + 1):
        profile = random.choices(FAILURE_PROFILES, weights=weights, k=1)[0]
        f_code, f_reason, valid_methods, _, amt_range = profile

        merchant_id, merchant_name = random.choice(MERCHANTS)
        method = random.choice(valid_methods)
        amount = round(random.uniform(amt_range[0], amt_range[1]), 2)

        # Synthetic customer generation with tenure & history
        cust_id = f"cust_{random.randint(10000, 85000)}"
        is_loyal = random.random() < 0.45

        if is_loyal:
            prev_success = random.randint(2, 18)
            prev_failures = random.randint(0, 1)
            clv = round(prev_success * random.uniform(800, 3500), 2)
            risk = round(random.uniform(0.01, 0.12), 3)
            attempt = random.choice([1, 1, 1, 2])
        else:
            prev_success = random.choice([0, 0, 1])
            prev_failures = random.randint(0, 3)
            clv = round(prev_success * random.uniform(400, 1500), 2)
            risk = round(random.uniform(0.08, 0.42), 3)
            attempt = random.choice([1, 1, 2, 3])

        # Overrides for security profiles
        if "RISK" in f_code or "TESTING" in f_code:
            risk = round(random.uniform(0.65, 0.98), 3)
            prev_success = 0
            prev_failures = random.randint(2, 6)

        # Random timestamp over the past 4 days
        random_secs = random.randint(0, 4 * 86400)
        txn_time = base_time + timedelta(seconds=random_secs)

        txn = {
            "transaction_id": f"txn_2026_{i:06d}",
            "merchant_id": merchant_id,
            "merchant_name": merchant_name,
            "customer_id": cust_id,
            "amount": amount,
            "payment_method": method,
            "failure_code": f_code,
            "failure_reason": f_reason,
            "attempt_number": attempt,
            "customer_previous_successes": prev_success,
            "customer_previous_failures": prev_failures,
            "customer_lifetime_value": clv,
            "risk_score": risk,
            "timestamp": txn_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        transactions.append(txn)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2)
        print(f"Successfully generated {count} synthetic transactions at {output_path}")

    return transactions

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "transactions.json")
    generate_synthetic_transactions(20000, out_file)
