"""
Data Schemas and Models for RecoveryOS
Works with Pydantic if available, or gracefully falls back to standard dataclasses
so it runs instantly on any Python installation with zero pip dependencies.
"""
import json
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict, field

class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    FINANCIAL_LIMIT = "FINANCIAL_LIMIT"
    AUTH_ERROR = "AUTH_ERROR"
    PERMANENT_REJECT = "PERMANENT_REJECT"
    SECURITY_RISK = "SECURITY_RISK"
    CART_ABANDONMENT = "CART_ABANDONMENT"

class RecoveryAction(str, Enum):
    RETRY_PAYMENT = "RETRY_PAYMENT"
    SEND_PAYMENT_LINK = "SEND_PAYMENT_LINK"
    SEND_WHATSAPP_NUDGE = "SEND_WHATSAPP_NUDGE"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    DO_NOTHING = "DO_NOTHING"

try:
    from pydantic import BaseModel, ConfigDict

    class PolicyCheckResult(BaseModel):
        rule_name: str
        passed: bool
        threshold_applied: str
        observed_value: str
        details: str

    class DecisionTrace(BaseModel):
        transaction_id: str
        amount: float
        merchant_id: str
        customer_id: str
        timestamp: str
        detection_event: str
        failure_code: str
        failure_category: FailureCategory
        diagnosis_explanation: str
        ai_confidence: float
        recommended_action: RecoveryAction
        policy_approved: bool
        policy_checks: List[PolicyCheckResult]
        final_action: RecoveryAction
        execution_result: str
        amount_recovered: float
        gateway_fee_saved: float
        audit_timestamp: str

    class TransactionEvent(BaseModel):
        model_config = ConfigDict(extra="ignore")
        transaction_id: str
        merchant_id: str
        customer_id: str
        amount: float
        payment_method: str
        failure_reason: str
        failure_code: str
        merchant_name: Optional[str] = None
        attempt_number: int = 1
        customer_previous_successes: int = 0
        customer_previous_failures: int = 0
        customer_lifetime_value: float = 0.0
        risk_score: float = 0.05
        timestamp: Optional[str] = None

    class BatchBenchmarkResult(BaseModel):
        total_transactions_analyzed: int
        at_risk_amount: float
        baseline_recovery_attempts: int
        baseline_successful_recoveries: int
        baseline_recovered_amount: float
        baseline_recovery_rate: float
        baseline_unnecessary_fees_burned: float
        baseline_high_risk_actions_taken: int
        recoveryos_recoverable_identified: int
        recoveryos_attempts_gated: int
        recoveryos_successful_recoveries: int
        recoveryos_recovered_amount: float
        recoveryos_recovery_rate: float
        recoveryos_unnecessary_actions_prevented: int
        recoveryos_gateway_fees_saved: float
        recoveryos_high_risk_actions_blocked: int
        recoveryos_net_economic_lift: float

except ImportError:
    # Standard library fallback
    class BaseDataModel:
        def model_dump(self) -> Dict[str, Any]:
            def serialize(v):
                if isinstance(v, Enum):
                    return v.value
                elif isinstance(v, list):
                    return [serialize(x) for x in v]
                elif hasattr(v, "model_dump"):
                    return v.model_dump()
                return v
            res = asdict(self)
            return {k: serialize(val) for k, val in res.items()}

        def model_dump_json(self) -> str:
            return json.dumps(self.model_dump())

    @dataclass
    class PolicyCheckResult(BaseDataModel):
        rule_name: str
        passed: bool
        threshold_applied: str
        observed_value: str
        details: str

    @dataclass
    class DecisionTrace(BaseDataModel):
        transaction_id: str
        amount: float
        merchant_id: str
        customer_id: str
        timestamp: str
        detection_event: str
        failure_code: str
        failure_category: FailureCategory
        diagnosis_explanation: str
        ai_confidence: float
        recommended_action: RecoveryAction
        policy_approved: bool
        policy_checks: List[PolicyCheckResult]
        final_action: RecoveryAction
        execution_result: str
        amount_recovered: float
        gateway_fee_saved: float
        audit_timestamp: str

    @dataclass
    class TransactionEvent(BaseDataModel):
        transaction_id: str
        merchant_id: str
        customer_id: str
        amount: float
        payment_method: str
        failure_reason: str
        failure_code: str
        merchant_name: Optional[str] = None
        attempt_number: int = 1
        customer_previous_successes: int = 0
        customer_previous_failures: int = 0
        customer_lifetime_value: float = 0.0
        risk_score: float = 0.05
        timestamp: Optional[str] = None

        @classmethod
        def from_dict(cls, d: Dict[str, Any]):
            # Filter keys to allowed dataclass fields
            valid_keys = {
                "transaction_id", "merchant_id", "customer_id", "amount",
                "payment_method", "failure_reason", "failure_code", "merchant_name",
                "attempt_number", "customer_previous_successes", "customer_previous_failures",
                "customer_lifetime_value", "risk_score", "timestamp"
            }
            filtered = {k: v for k, v in d.items() if k in valid_keys}
            return cls(**filtered)

    @dataclass
    class BatchBenchmarkResult(BaseDataModel):
        total_transactions_analyzed: int
        at_risk_amount: float
        baseline_recovery_attempts: int
        baseline_successful_recoveries: int
        baseline_recovered_amount: float
        baseline_recovery_rate: float
        baseline_unnecessary_fees_burned: float
        baseline_high_risk_actions_taken: int
        recoveryos_recoverable_identified: int
        recoveryos_attempts_gated: int
        recoveryos_successful_recoveries: int
        recoveryos_recovered_amount: float
        recoveryos_recovery_rate: float
        recoveryos_unnecessary_actions_prevented: int
        recoveryos_gateway_fees_saved: float
        recoveryos_high_risk_actions_blocked: int
        recoveryos_net_economic_lift: float
