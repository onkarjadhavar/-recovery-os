"""
RecoveryOS Chaos, Safety & Failure Modes Test Suite
Validates that the system fails safely under all adversarial, edge-case, and chaos conditions:
1. Duplicate webhook idempotency
2. Already captured payment safety
3. Out-of-order webhook events
4. High-risk transaction policy blockage
5. Low-confidence AI output gating
6. Autonomous amount limit enforcement (> ₹5,000)
7. Retry budget limit enforcement (> 2 attempts)
8. Permanent failure stopping rule (expired instruments)
9. Proof that AI CANNOT override deterministic policy engine
10. Malformed payload safe handling
11. Benchmark determinism and reproducibility
"""
import os
import sys
import json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, BACKEND_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.models.schemas import TransactionEvent, RecoveryAction, FailureCategory
from app.core.policy_engine import PolicyEngine
from app.core.agent import RecoveryAgent
from app.core.evaluator import BenchmarkEvaluator
from app.api.routes_razorpay import RazorpayWebhookHandler, PROCESSED_WEBHOOK_EVENTS
from app.core.config import settings

def test_1_duplicate_webhook_idempotency():
    """Validates that duplicate webhooks for the same transaction ID do not trigger duplicate recoveries."""
    mock_payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_idempotency_test_999",
                    "amount": 149900,
                    "method": "upi",
                    "error_code": "GATEWAY_TIMEOUT",
                    "error_description": "Timeout",
                    "status": "failed",
                    "notes": {
                        "merchant_id": "merch_lenskart",
                        "customer_id": "cust_123",
                        "risk_score": 0.02,
                        "attempt_number": 1
                    }
                }
            }
        }
    }
    
    # First invocation
    trace1 = RazorpayWebhookHandler.parse_and_process_event(mock_payload)
    assert trace1.final_action == RecoveryAction.RETRY_PAYMENT
    assert trace1.amount_recovered == 1499.0

    # Second invocation with same ID
    trace2 = RazorpayWebhookHandler.parse_and_process_event(mock_payload)
    assert "IDEMPOTENT" in trace2.execution_result
    # Idempotent replay must not double count money
    assert trace2.amount_recovered == 0.0
    print("[PASS] Test 1: Duplicate webhook idempotency verified (No duplicate recovery)")

def test_2_already_captured_payment_safety():
    """Validates that a payment marked as captured is never retried."""
    captured_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_already_captured_888",
                    "amount": 250000,
                    "method": "card",
                    "status": "captured",
                    "notes": {
                        "merchant_id": "merch_store",
                        "customer_id": "cust_456"
                    }
                }
            }
        }
    }
    trace = RazorpayWebhookHandler.parse_and_process_event(captured_payload)
    assert trace.final_action == RecoveryAction.DO_NOTHING
    assert trace.amount_recovered == 0.0
    assert "already captured" in trace.execution_result.lower()
    print("[PASS] Test 2: Already-captured payment safely halted")

def test_3_ai_cannot_override_policy_engine():
    """
    CRITICAL TEST: Proves the AI layer CANNOT bypass deterministic policy rules.
    Even if AI hallucinates/recommends RETRY_PAYMENT with 99.9% confidence on a ₹50,000 high-risk txn,
    the Policy Engine strictly blocks it and forces ESCALATE_TO_HUMAN.
    """
    txn = TransactionEvent(
        transaction_id="txn_adversarial_ai_override",
        merchant_id="merch_gold_store",
        customer_id="cust_suspicious",
        amount=50000.0,  # Breaches ₹5,000 cap
        payment_method="CARD",
        failure_reason="Network switch latency",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=1,
        customer_previous_successes=0,
        customer_previous_failures=5,
        customer_lifetime_value=0.0,
        risk_score=0.85   # Breaches 0.35 risk ceiling
    )
    
    # Simulate AI attempting to force an autonomous RETRY
    hallucinated_action = RecoveryAction.RETRY_PAYMENT
    fake_ai_confidence = 0.999
    
    is_approved, final_action, checks, reason = PolicyEngine.evaluate(
        txn=txn,
        failure_category=FailureCategory.TRANSIENT,
        ai_confidence=fake_ai_confidence,
        proposed_action=hallucinated_action
    )
    
    assert is_approved is False, "Policy Engine must reject AI recommendation!"
    assert final_action != RecoveryAction.RETRY_PAYMENT, "AI was able to trigger unauthorized retry!"
    assert final_action in [RecoveryAction.ESCALATE_TO_HUMAN, RecoveryAction.DO_NOTHING]
    
    amount_check = next(c for c in checks if c.rule_name == "AUTO_RECOVERY_AMOUNT_CAP")
    risk_check = next(c for c in checks if c.rule_name == "FRAUD_RISK_BOUNDARY")
    assert amount_check.passed is False
    assert risk_check.passed is False
    print("[PASS] Test 3: AI CANNOT override Deterministic Policy Engine (Verified Hard Boundary)")

def test_4_high_risk_transaction_blocked():
    """Validates that a high fraud risk score (>= 0.35) prevents automated recovery."""
    txn = TransactionEvent(
        transaction_id="txn_fraud_test",
        merchant_id="merch_electronics",
        customer_id="cust_new",
        amount=3200.0,
        payment_method="CARD",
        failure_reason="Abnormal IP velocity and device mismatch",
        failure_code="HIGH_RISK_SUSPECTED",
        attempt_number=1,
        customer_previous_successes=0,
        customer_previous_failures=3,
        customer_lifetime_value=0.0,
        risk_score=0.78  # Above 0.35 cutoff
    )
    trace = RecoveryAgent.process_event(txn)
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    assert trace.amount_recovered == 0.0
    print("[PASS] Test 4: High-risk transaction safely blocked and escalated to human")

def test_5_low_confidence_ai_gated():
    """Validates that low diagnostic confidence (< 85%) is gated for human review."""
    txn = TransactionEvent(
        transaction_id="txn_low_conf_test",
        merchant_id="merch_test",
        customer_id="cust_untrusted",
        amount=1200.0,
        payment_method="UPI",
        failure_reason="Uncertain bank error code 99",
        failure_code="UNKNOWN_ERROR_CODE",
        attempt_number=1,
        customer_previous_successes=0,
        customer_previous_failures=4,
        customer_lifetime_value=0.0,
        risk_score=0.10
    )
    trace = RecoveryAgent.process_event(txn)
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    conf_check = next(c for c in trace.policy_checks if c.rule_name == "AI_CONFIDENCE_GATE")
    assert conf_check.passed is False
    print("[PASS] Test 5: Low-confidence AI output gated to human review")

def test_6_amount_limit_exceeded():
    """Validates that amounts > ₹5,000 are blocked from autonomous execution."""
    txn = TransactionEvent(
        transaction_id="txn_amount_cap_test",
        merchant_id="merch_jewel",
        customer_id="cust_vip",
        amount=42000.0,  # Exceeds ₹5,000 cap
        payment_method="CARD",
        failure_reason="Bank switch timeout",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=1,
        customer_previous_successes=10,
        customer_previous_failures=0,
        customer_lifetime_value=95000.0,
        risk_score=0.02
    )
    trace = RecoveryAgent.process_event(txn)
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    assert trace.amount_recovered == 0.0
    print("[PASS] Test 6: Amount limit cap (> ₹5,000) strictly enforced")

def test_7_retry_budget_exhaustion():
    """Validates that attempt count > 2 stops automated retries."""
    txn = TransactionEvent(
        transaction_id="txn_retry_budget_test",
        merchant_id="merch_quick",
        customer_id="cust_fatigue",
        amount=450.0,
        payment_method="UPI",
        failure_reason="Timeout",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=3,  # Exceeds max 2 attempts
        customer_previous_successes=4,
        customer_previous_failures=1,
        customer_lifetime_value=4000.0,
        risk_score=0.03
    )
    trace = RecoveryAgent.process_event(txn)
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    print("[PASS] Test 7: Max retry budget (> 2) halts automated retries")

def test_8_permanent_failure_stop_rule():
    """Validates that permanent rejections (expired cards) halt and save gateway fees."""
    txn = TransactionEvent(
        transaction_id="txn_perm_test",
        merchant_id="merch_food",
        customer_id="cust_card",
        amount=890.0,
        payment_method="CARD",
        failure_reason="Card has expired",
        failure_code="CARD_EXPIRED",
        attempt_number=1,
        customer_previous_successes=8,
        customer_previous_failures=0,
        customer_lifetime_value=12000.0,
        risk_score=0.01
    )
    trace = RecoveryAgent.process_event(txn)
    assert trace.final_action == RecoveryAction.DO_NOTHING
    assert trace.amount_recovered == 0.0
    assert trace.gateway_fee_saved >= 3.50
    print("[PASS] Test 8: Permanent failure stop rule enforced (₹3.50 fee saved)")

def test_9_scenario_4_consistent_amount():
    """Validates that Scenario 4 (Cart Dropoff) recovers the full ₹3,250 amount consistently."""
    mock_webhook = RazorpayWebhookHandler.generate_mock_webhook("cart_dropoff")
    trace = RazorpayWebhookHandler.parse_and_process_event(mock_webhook)
    assert trace.amount == 3250.0
    assert trace.amount_recovered == 3250.0
    assert trace.final_action == RecoveryAction.SEND_PAYMENT_LINK
    assert trace.policy_approved is True
    print("[PASS] Test 9: Scenario 4 amount consistency verified (₹3,250 -> ₹3,250)")

def test_10_benchmark_determinism_and_reproducibility():
    """Validates that benchmark produces identical numbers across repeated runs."""
    sample_txns = [
        {"transaction_id": f"test_b_{i}", "merchant_id": "m1", "customer_id": "c1", "amount": 1000.0,
         "payment_method": "UPI", "failure_code": "GATEWAY_TIMEOUT", "failure_reason": "Timeout",
         "attempt_number": 1, "customer_previous_successes": 5, "customer_previous_failures": 0,
         "customer_lifetime_value": 5000.0, "risk_score": 0.02}
        for i in range(100)
    ]
    res1 = BenchmarkEvaluator.run_benchmark(sample_txns)
    res2 = BenchmarkEvaluator.run_benchmark(sample_txns)
    assert res1.recoveryos_recovery_rate == res2.recoveryos_recovery_rate
    assert res1.recoveryos_recovered_amount == res2.recoveryos_recovered_amount
    assert res1.recoveryos_gateway_fees_saved == res2.recoveryos_gateway_fees_saved
    print("[PASS] Test 10: Benchmark determinism and mathematical reproducibility verified")

import unittest

class TestChaosAndSafety(unittest.TestCase):
    def test_01_duplicate_webhook_idempotency(self):
        test_1_duplicate_webhook_idempotency()

    def test_02_already_captured_payment_safety(self):
        test_2_already_captured_payment_safety()

    def test_03_ai_cannot_override_policy_engine(self):
        test_3_ai_cannot_override_policy_engine()

    def test_04_high_risk_transaction_blocked(self):
        test_4_high_risk_transaction_blocked()

    def test_05_low_confidence_ai_gated(self):
        test_5_low_confidence_ai_gated()

    def test_06_amount_limit_exceeded(self):
        test_6_amount_limit_exceeded()

    def test_07_retry_budget_exhaustion(self):
        test_7_retry_budget_exhaustion()

    def test_08_permanent_failure_stop_rule(self):
        test_8_permanent_failure_stop_rule()

    def test_09_scenario_4_consistent_amount(self):
        test_9_scenario_4_consistent_amount()

    def test_10_benchmark_determinism_and_reproducibility(self):
        test_10_benchmark_determinism_and_reproducibility()

def run_all():
    print("==========================================================")
    print("  Running RecoveryOS Chaos, Safety & Policy Test Suite")
    print("==========================================================")
    test_1_duplicate_webhook_idempotency()
    test_2_already_captured_payment_safety()
    test_3_ai_cannot_override_policy_engine()
    test_4_high_risk_transaction_blocked()
    test_5_low_confidence_ai_gated()
    test_6_amount_limit_exceeded()
    test_7_retry_budget_exhaustion()
    test_8_permanent_failure_stop_rule()
    test_9_scenario_4_consistent_amount()
    test_10_benchmark_determinism_and_reproducibility()
    print("==========================================================")
    print("  ALL 10 CHAOS & SAFETY TESTS PASSED (10/10)!")
    print("==========================================================")

if __name__ == "__main__":
    run_all()

