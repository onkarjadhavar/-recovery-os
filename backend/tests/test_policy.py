"""
Unit Tests for RecoveryOS Policy Guardrails & Agent Decisions
"""
import sys
import os

# Add backend directory to sys.path
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
from app.core.config import settings

def test_transient_happy_path():
    """Validates that a low-risk, transient failure within amount limit is approved for auto-recovery."""
    txn = TransactionEvent(
        transaction_id="txn_test_001",
        merchant_id="merch_lenskart",
        customer_id="cust_9921",
        amount=1499.0,
        payment_method="UPI",
        failure_reason="Bank switch timeout during NPCI settlement",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=1,
        customer_previous_successes=6,
        customer_previous_failures=0,
        customer_lifetime_value=12400.0,
        risk_score=0.03
    )
    trace = RecoveryAgent.process_event(txn)
    
    assert trace.policy_approved is True
    assert trace.failure_category == FailureCategory.TRANSIENT
    assert trace.final_action == RecoveryAction.RETRY_PAYMENT
    assert trace.amount_recovered == 1499.0
    print("[PASS] test_transient_happy_path")

def test_high_amount_escalation_guardrail():
    """Validates that a transaction exceeding INR 5,000 is blocked from autonomous execution."""
    txn = TransactionEvent(
        transaction_id="txn_test_002",
        merchant_id="merch_electronics",
        customer_id="cust_8812",
        amount=42000.0,  # Exceeds MAX_AUTO_RECOVERY_AMOUNT (5000)
        payment_method="CARD",
        failure_reason="Bank switch timeout",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=1,
        customer_previous_successes=2,
        customer_previous_failures=0,
        customer_lifetime_value=50000.0,
        risk_score=0.04
    )
    trace = RecoveryAgent.process_event(txn)
    
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    assert trace.amount_recovered == 0.0
    # Verify policy checks recorded the failure
    amount_check = next(c for c in trace.policy_checks if c.rule_name == "AUTO_RECOVERY_AMOUNT_CAP")
    assert amount_check.passed is False
    print("[PASS] test_high_amount_escalation_guardrail")

def test_fraud_risk_boundary_guardrail():
    """Validates that high risk scores are blocked and never auto-recovered."""
    txn = TransactionEvent(
        transaction_id="txn_test_003",
        merchant_id="merch_luxury",
        customer_id="cust_flagged",
        amount=2800.0,
        payment_method="CARD",
        failure_reason="Abnormal IP velocity and device mismatch",
        failure_code="HIGH_RISK_SUSPECTED",
        attempt_number=1,
        customer_previous_successes=0,
        customer_previous_failures=4,
        customer_lifetime_value=0.0,
        risk_score=0.82  # Above FRAUD_RISK_CUTOFF (0.35)
    )
    trace = RecoveryAgent.process_event(txn)
    
    assert trace.policy_approved is False
    assert trace.final_action in [RecoveryAction.ESCALATE_TO_HUMAN, RecoveryAction.DO_NOTHING]
    assert trace.amount_recovered == 0.0
    risk_check = next(c for c in trace.policy_checks if c.rule_name == "FRAUD_RISK_BOUNDARY")
    assert risk_check.passed is False
    print("[PASS] test_fraud_risk_boundary_guardrail")

def test_permanent_failure_stop_rule():
    """Validates that permanent errors (e.g. expired cards) are halted to save merchant fees."""
    txn = TransactionEvent(
        transaction_id="txn_test_004",
        merchant_id="merch_zomato",
        customer_id="cust_3311",
        amount=890.0,
        payment_method="CARD",
        failure_reason="Card expired",
        failure_code="CARD_EXPIRED",
        attempt_number=1,
        customer_previous_successes=10,
        customer_previous_failures=0,
        customer_lifetime_value=12000.0,
        risk_score=0.02
    )
    trace = RecoveryAgent.process_event(txn)
    
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.DO_NOTHING
    assert trace.gateway_fee_saved > 0.0
    perm_check = next(c for c in trace.policy_checks if c.rule_name == "PERMANENT_FAILURE_STOP")
    assert perm_check.passed is False
    print("[PASS] test_permanent_failure_stop_rule")

def test_retry_budget_exhaustion():
    """Validates that retry budget (>2) halts automatic gateway retries."""
    txn = TransactionEvent(
        transaction_id="txn_test_005",
        merchant_id="merch_swiggy",
        customer_id="cust_4455",
        amount=650.0,
        payment_method="UPI",
        failure_reason="Bank switch timeout",
        failure_code="GATEWAY_TIMEOUT",
        attempt_number=3,  # Exceeds MAX_RETRY_ATTEMPTS (2)
        customer_previous_successes=5,
        customer_previous_failures=2,
        customer_lifetime_value=4500.0,
        risk_score=0.04
    )
    trace = RecoveryAgent.process_event(txn)
    
    assert trace.policy_approved is False
    assert trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN
    retry_check = next(c for c in trace.policy_checks if c.rule_name == "MAX_RETRY_BUDGET")
    assert retry_check.passed is False
    print("[PASS] test_retry_budget_exhaustion")

import unittest

class TestPolicyGuardrails(unittest.TestCase):
    def test_01_transient_happy_path(self):
        test_transient_happy_path()

    def test_02_high_amount_escalation_guardrail(self):
        test_high_amount_escalation_guardrail()

    def test_03_fraud_risk_boundary_guardrail(self):
        test_fraud_risk_boundary_guardrail()

    def test_04_permanent_failure_stop_rule(self):
        test_permanent_failure_stop_rule()

    def test_05_retry_budget_exhaustion(self):
        test_retry_budget_exhaustion()

if __name__ == "__main__":
    print("Running RecoveryOS Guardrail Tests...")
    test_transient_happy_path()
    test_high_amount_escalation_guardrail()
    test_fraud_risk_boundary_guardrail()
    test_permanent_failure_stop_rule()
    test_retry_budget_exhaustion()
    print("\nALL POLICY GUARDRAIL TESTS PASSED SUCCESSFULLY! (5/5)")

