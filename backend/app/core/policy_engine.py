"""
Deterministic Policy Engine & Guardrails for RecoveryOS

Enforces strict financial boundaries and stopping rules.
The LLM/AI layer NEVER bypasses these rules.
"""
from typing import Tuple, List
from .config import settings
from ..models.schemas import (
    TransactionEvent,
    RecoveryAction,
    FailureCategory,
    PolicyCheckResult
)

class PolicyEngine:
    """
    Guarantees bounded, audited financial operations:
    1. Hard Amount Caps (<= INR 5,000 for autonomous recovery)
    2. Retry Budget Limits (<= 2 attempts to stop payment churn)
    3. Fraud Risk Ceilings (risk < 0.35)
    4. Diagnostic Confidence Gates (confidence >= 85%)
    5. Permanent Failure Stopping Rules (no retries on invalid accounts)
    """

    @staticmethod
    def evaluate(
        txn: TransactionEvent,
        failure_category: FailureCategory,
        ai_confidence: float,
        proposed_action: RecoveryAction
    ) -> Tuple[bool, RecoveryAction, List[PolicyCheckResult], str]:
        """
        Evaluates the proposed AI action against all hard policies.
        Returns:
            (is_approved, final_action, check_results, enforcement_reason)
        """
        checks: List[PolicyCheckResult] = []
        all_passed = True
        enforcement_reason = "All deterministic safety policies satisfied."
        final_action = proposed_action

        # Check 1: Stop on Permanent Failure
        is_permanent = (failure_category == FailureCategory.PERMANENT_REJECT)
        checks.append(PolicyCheckResult(
            rule_name="PERMANENT_FAILURE_STOP",
            passed=not is_permanent,
            threshold_applied="Failure must not be permanent account/credential termination",
            observed_value=f"Category: {failure_category.value}",
            details="Immediate halt: retrying permanent errors causes gateway fines and merchant penalties."
        ))
        if is_permanent:
            all_passed = False
            final_action = RecoveryAction.DO_NOTHING
            enforcement_reason = "Halted: Permanent failure detected (e.g., closed account or expired instrument)."

        # Check 2: Risk Boundary (Fraud / High-Risk Prevention)
        risk_passed = txn.risk_score < settings.FRAUD_RISK_CUTOFF
        checks.append(PolicyCheckResult(
            rule_name="FRAUD_RISK_BOUNDARY",
            passed=risk_passed,
            threshold_applied=f"Risk Score < {settings.FRAUD_RISK_CUTOFF:.2f}",
            observed_value=f"Risk Score: {txn.risk_score:.2f}",
            details="Prohibits automatic recovery on transactions showing anomalous or abusive vectors."
        ))
        if not risk_passed:
            all_passed = False
            final_action = RecoveryAction.DO_NOTHING if txn.risk_score > 0.6 else RecoveryAction.ESCALATE_TO_HUMAN
            enforcement_reason = f"Blocked: Transaction risk ({txn.risk_score:.2f}) breached the safety threshold ({settings.FRAUD_RISK_CUTOFF:.2f})."

        # Check 3: Retry Budget / Customer Fatigue Cap
        retry_passed = txn.attempt_number <= settings.MAX_RETRY_ATTEMPTS
        checks.append(PolicyCheckResult(
            rule_name="MAX_RETRY_BUDGET",
            passed=retry_passed,
            threshold_applied=f"Attempts <= {settings.MAX_RETRY_ATTEMPTS}",
            observed_value=f"Attempt #{txn.attempt_number}",
            details="Stops repeat churn and customer harassment after maximum permitted automated retries."
        ))
        if not retry_passed and final_action == RecoveryAction.RETRY_PAYMENT:
            all_passed = False
            final_action = RecoveryAction.ESCALATE_TO_HUMAN
            enforcement_reason = f"Budget exhausted: Attempt #{txn.attempt_number} exceeds max allowed ({settings.MAX_RETRY_ATTEMPTS}). Escalating to human ops."

        # Check 4: Autonomous Amount Ceiling
        amount_passed = txn.amount <= settings.MAX_AUTO_RECOVERY_AMOUNT
        checks.append(PolicyCheckResult(
            rule_name="AUTO_RECOVERY_AMOUNT_CAP",
            passed=amount_passed,
            threshold_applied=f"Amount <= ₹{settings.MAX_AUTO_RECOVERY_AMOUNT:,.2f}",
            observed_value=f"₹{txn.amount:,.2f}",
            details="High monetary exposures mandate human supervisor sign-off before initiating payment calls."
        ))
        if not amount_passed and final_action in [RecoveryAction.RETRY_PAYMENT, RecoveryAction.SEND_PAYMENT_LINK]:
            all_passed = False
            final_action = RecoveryAction.ESCALATE_TO_HUMAN
            enforcement_reason = f"Escalated: High value (₹{txn.amount:,.2f}) exceeds autonomous limit (₹{settings.MAX_AUTO_RECOVERY_AMOUNT:,.2f}). Requires supervisor review."

        # Check 5: AI Diagnostic Confidence Floor
        confidence_passed = ai_confidence >= settings.MIN_AI_CONFIDENCE
        checks.append(PolicyCheckResult(
            rule_name="AI_CONFIDENCE_GATE",
            passed=confidence_passed,
            threshold_applied=f"Confidence >= {settings.MIN_AI_CONFIDENCE * 100:.0f}%",
            observed_value=f"{ai_confidence * 100:.1f}%",
            details="Ambiguous diagnostic signals must not trigger automated recovery actions."
        ))
        if not confidence_passed and all_passed:
            all_passed = False
            final_action = RecoveryAction.ESCALATE_TO_HUMAN
            enforcement_reason = f"Gated: Diagnostic confidence ({ai_confidence * 100:.1f}%) below minimum required ({settings.MIN_AI_CONFIDENCE * 100:.0f}%)."

        return all_passed, final_action, checks, enforcement_reason
