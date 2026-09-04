"""
AI Recovery Agent & Orchestrator for RecoveryOS

Performs perception, semantic diagnosis, recoverability estimation,
policy gating, and safe tool execution with full audit traces.
"""
import time
from datetime import datetime
from typing import Dict, Any, Tuple
from .config import settings
from .policy_engine import PolicyEngine
from ..models.schemas import (
    TransactionEvent,
    FailureCategory,
    RecoveryAction,
    DecisionTrace
)

class RecoveryAgent:
    """
    Autonomous Agent that diagnoses payment failures and orchestrates
    safe, policy-bounded recovery actions.
    """

    # Mapping common Razorpay & Indian banking error codes to categories
    ERROR_CODE_MAP = {
        "GATEWAY_TIMEOUT": (FailureCategory.TRANSIENT, 0.94, RecoveryAction.RETRY_PAYMENT),
        "BAD_REQUEST_PAYMENT_TIMED_OUT": (FailureCategory.TRANSIENT, 0.92, RecoveryAction.RETRY_PAYMENT),
        "UPI_COLLECT_TIMEOUT": (FailureCategory.TRANSIENT, 0.91, RecoveryAction.RETRY_PAYMENT),
        "BANK_SERVER_UNAVAILABLE": (FailureCategory.TRANSIENT, 0.89, RecoveryAction.RETRY_PAYMENT),
        "NETWORK_ERROR": (FailureCategory.TRANSIENT, 0.93, RecoveryAction.RETRY_PAYMENT),
        
        "INSUFFICIENT_FUNDS": (FailureCategory.FINANCIAL_LIMIT, 0.86, RecoveryAction.SEND_PAYMENT_LINK),
        "CARD_LIMIT_EXCEEDED": (FailureCategory.FINANCIAL_LIMIT, 0.88, RecoveryAction.SEND_PAYMENT_LINK),
        "DAILY_TRANSACTION_LIMIT_REACHED": (FailureCategory.FINANCIAL_LIMIT, 0.87, RecoveryAction.SEND_PAYMENT_LINK),
        
        "AUTHENTICATION_FAILED": (FailureCategory.AUTH_ERROR, 0.86, RecoveryAction.SEND_WHATSAPP_NUDGE),
        "OTP_EXPIRED": (FailureCategory.AUTH_ERROR, 0.90, RecoveryAction.SEND_WHATSAPP_NUDGE),
        "3DS_VERIFICATION_FAILED": (FailureCategory.AUTH_ERROR, 0.84, RecoveryAction.SEND_PAYMENT_LINK),
        
        "CART_DROPOFF": (FailureCategory.CART_ABANDONMENT, 0.88, RecoveryAction.SEND_PAYMENT_LINK),
        "CHECKOUT_UNFINISHED": (FailureCategory.CART_ABANDONMENT, 0.87, RecoveryAction.SEND_PAYMENT_LINK),
        
        "CARD_EXPIRED": (FailureCategory.PERMANENT_REJECT, 0.99, RecoveryAction.DO_NOTHING),
        "ACCOUNT_CLOSED_OR_BLOCKED": (FailureCategory.PERMANENT_REJECT, 0.99, RecoveryAction.DO_NOTHING),
        "INVALID_VPA_ADDRESS": (FailureCategory.PERMANENT_REJECT, 0.99, RecoveryAction.DO_NOTHING),
        
        "HIGH_RISK_SUSPECTED": (FailureCategory.SECURITY_RISK, 0.96, RecoveryAction.ESCALATE_TO_HUMAN),
        "VELOCITY_CHECK_FAILED": (FailureCategory.SECURITY_RISK, 0.95, RecoveryAction.ESCALATE_TO_HUMAN),
        "SUSPECTED_CARD_TESTING": (FailureCategory.SECURITY_RISK, 0.98, RecoveryAction.DO_NOTHING),
    }

    @classmethod
    def diagnose(cls, txn: TransactionEvent) -> Tuple[FailureCategory, float, RecoveryAction, str]:
        """
        Diagnoses payment failure based on failure code, customer tenure, and risk signals.
        """
        code = txn.failure_code.upper().strip()
        matched = cls.ERROR_CODE_MAP.get(code)
        
        if matched:
            category, base_conf, candidate_action = matched
        else:
            # Fallback heuristic based on failure reason keywords
            reason_lower = txn.failure_reason.lower()
            if any(k in reason_lower for k in ["timeout", "server", "bank down", "switch", "retry"]):
                category = FailureCategory.TRANSIENT
                base_conf = 0.88
                candidate_action = RecoveryAction.RETRY_PAYMENT
            elif any(k in reason_lower for k in ["insufficient", "balance", "limit", "funds"]):
                category = FailureCategory.FINANCIAL_LIMIT
                base_conf = 0.86
                candidate_action = RecoveryAction.SEND_PAYMENT_LINK
            elif any(k in reason_lower for k in ["otp", "pin", "auth", "3ds", "password"]):
                category = FailureCategory.AUTH_ERROR
                base_conf = 0.85
                candidate_action = RecoveryAction.SEND_WHATSAPP_NUDGE
            elif any(k in reason_lower for k in ["fraud", "suspicious", "stolen", "block", "risk"]):
                category = FailureCategory.SECURITY_RISK
                base_conf = 0.92
                candidate_action = RecoveryAction.ESCALATE_TO_HUMAN
            elif any(k in reason_lower for k in ["expired", "invalid", "closed", "nonexistent"]):
                category = FailureCategory.PERMANENT_REJECT
                base_conf = 0.98
                candidate_action = RecoveryAction.DO_NOTHING
            else:
                category = FailureCategory.TRANSIENT
                base_conf = 0.75
                candidate_action = RecoveryAction.RETRY_PAYMENT

        # Context adjustment: Customer tenure & trust boost
        confidence = base_conf
        if txn.customer_previous_successes >= 3 and txn.customer_previous_failures == 0:
            confidence = min(0.98, confidence + 0.05)
        elif txn.customer_previous_failures >= 3:
            confidence = max(0.60, confidence - 0.12)

        # Generate natural language diagnostic reasoning
        explanation = cls._generate_explanation(txn, category, confidence, candidate_action)
        return category, round(confidence, 3), candidate_action, explanation

    @classmethod
    def _generate_explanation(
        cls,
        txn: TransactionEvent,
        category: FailureCategory,
        confidence: float,
        action: RecoveryAction
    ) -> str:
        """
        Synthesizes human-readable AI diagnostic narrative.
        """
        history_summary = (
            f"Verified customer with {txn.customer_previous_successes} prior successful payments (CLV: ₹{txn.customer_lifetime_value:,.0f})."
            if txn.customer_previous_successes > 0
            else "New customer with zero transaction history."
        )

        if category == FailureCategory.TRANSIENT:
            return (
                f"Transient inter-bank latency / switch timeout on {txn.payment_method}. "
                f"{history_summary} Failure is non-behavioral; auto-retry scheduled with jitter."
            )
        elif category == FailureCategory.FINANCIAL_LIMIT:
            return (
                f"Instrument limits or temporary funds deficit encountered. "
                f"{history_summary} Re-triggering standard charge will likely fail again. "
                f"Generating alternate multi-rail payment link (UPI/Card/EMI)."
            )
        elif category == FailureCategory.AUTH_ERROR:
            return (
                f"User-side authentication drop (OTP timeout or 3DS dismiss). "
                f"{history_summary} High commercial intent preserved. Contextual WhatsApp nudge recommended."
            )
        elif category == FailureCategory.PERMANENT_REJECT:
            return (
                f"Permanent instrument rejection ({txn.failure_code}). "
                f"Immediate termination required to eliminate wasted gateway authorization fees and merchant penalties."
            )
        elif category == FailureCategory.SECURITY_RISK:
            return (
                f"High-risk anomaly: risk score {txn.risk_score:.2f} exceeds platform baseline. "
                f"Immediate automated intervention prohibited. Routing to fraud ops sentinel."
            )
        elif category == FailureCategory.CART_ABANDONMENT:
            return (
                f"Checkout funnel drop before gateway transition. Intent is warm. "
                f"Generating time-bounded Razorpay Smart Checkout link with 15-minute lock."
            )
        return f"Standard diagnosis: {category.value} with confidence {confidence * 100:.1f}%."

    @classmethod
    def process_event(cls, txn: TransactionEvent) -> DecisionTrace:
        """
        Executes the end-to-end agentic recovery loop:
        Perception -> Diagnosis -> Candidate Action -> Policy Evaluation -> Execution -> Verification
        """
        timestamp_str = txn.timestamp or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Perception & Semantic Diagnosis
        category, confidence, candidate_action, explanation = cls.diagnose(txn)

        # 2. Policy Guardrail Gating
        is_approved, final_action, policy_checks, enforcement_reason = PolicyEngine.evaluate(
            txn=txn,
            failure_category=category,
            ai_confidence=confidence,
            proposed_action=candidate_action
        )

        # 3. Action Execution & Outcome Simulation
        amount_recovered = 0.0
        fee_saved = 0.0
        execution_result = ""

        if final_action == RecoveryAction.DO_NOTHING:
            fee_saved = settings.ESTIMATED_RETRY_FEE_BURN
            execution_result = f"Action Suppressed: {enforcement_reason}. Wasted gateway retry fee (₹{fee_saved:.2f}) saved."
            
        elif final_action == RecoveryAction.ESCALATE_TO_HUMAN:
            execution_result = f"Ops Ticket Created: Escalated to merchant team. Reason: {enforcement_reason}."
            
        elif final_action == RecoveryAction.RETRY_PAYMENT:
            # Deterministic outcome: high confidence + transient + low attempts succeeds
            if category == FailureCategory.TRANSIENT and txn.attempt_number <= 2 and txn.risk_score < 0.20:
                amount_recovered = txn.amount
                execution_result = f"Success: Razorpay Smart Retry executed at optimal jitter. Payment captured (₹{amount_recovered:,.2f})."
            else:
                execution_result = "Retry executed; secondary bank response pending."

        elif final_action == RecoveryAction.SEND_PAYMENT_LINK:
            amount_recovered = txn.amount * 0.72  # Simulated 72% conversion on smart links
            execution_result = f"Success: Razorpay Payment Link dispatched via SMS/Email (Link ID: plink_{txn.transaction_id[-8:]})."

        elif final_action == RecoveryAction.SEND_WHATSAPP_NUDGE:
            amount_recovered = txn.amount * 0.68  # Simulated 68% conversion on contextual WhatsApp nudges
            execution_result = f"Success: WhatsApp 1-click recovery message sent to customer {txn.customer_id[-6:]}."

        return DecisionTrace(
            transaction_id=txn.transaction_id,
            amount=txn.amount,
            merchant_id=txn.merchant_id,
            customer_id=txn.customer_id,
            timestamp=timestamp_str,
            detection_event=f"Payment Failed ({txn.payment_method} - {txn.failure_code})",
            failure_code=txn.failure_code,
            failure_category=category,
            diagnosis_explanation=explanation,
            ai_confidence=confidence,
            recommended_action=candidate_action,
            policy_approved=is_approved,
            policy_checks=policy_checks,
            final_action=final_action,
            execution_result=execution_result,
            amount_recovered=round(amount_recovered, 2),
            gateway_fee_saved=round(fee_saved, 2),
            audit_timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
