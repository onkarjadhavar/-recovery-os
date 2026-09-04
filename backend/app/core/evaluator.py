"""
Benchmark & Comparative Evaluation Engine for RecoveryOS

Evaluates synthetic payment transactions against a Naive Baseline (blind retries)
vs RecoveryOS (AI-diagnosed, policy-guarded selective recovery).
"""
from typing import List, Dict, Any
from .agent import RecoveryAgent
from .config import settings
from ..models.schemas import (
    TransactionEvent,
    FailureCategory,
    RecoveryAction,
    BatchBenchmarkResult
)

class BenchmarkEvaluator:
    """
    Simulates real comparative economics on held-out transactions.
    """

    @classmethod
    def run_benchmark(cls, transactions: List[Dict[str, Any]]) -> BatchBenchmarkResult:
        total_txns = len(transactions)
        total_at_risk = 0.0

        # Naive Baseline Trackers
        base_attempts = 0
        base_successes = 0
        base_recovered_amount = 0.0
        base_unnecessary_fees = 0.0
        base_high_risk_actions = 0

        # RecoveryOS Trackers
        ros_recoverable_identified = 0
        ros_attempts_gated = 0
        ros_successes = 0
        ros_recovered_amount = 0.0
        ros_prevented_actions = 0
        ros_fees_saved = 0.0
        ros_high_risk_blocked = 0

        for item in transactions:
            txn = TransactionEvent.from_dict(item) if hasattr(TransactionEvent, "from_dict") else TransactionEvent(**item)
            total_at_risk += txn.amount

            # -----------------------------------------------------------------
            # 1. NAIVE BASELINE SIMULATION (Retry everything indiscriminately)
            # -----------------------------------------------------------------
            base_attempts += 1
            is_permanent = txn.failure_code in ["CARD_EXPIRED", "ACCOUNT_CLOSED_OR_BLOCKED", "INVALID_VPA_ADDRESS"]
            is_high_risk = txn.risk_score >= settings.FRAUD_RISK_CUTOFF

            if is_high_risk:
                base_high_risk_actions += 1

            if is_permanent:
                # Guaranteed failure -> Burns gateway authorization fee
                base_unnecessary_fees += settings.ESTIMATED_RETRY_FEE_BURN
            elif is_high_risk:
                # High risk retried -> Leads to chargebacks/loss
                base_unnecessary_fees += settings.ESTIMATED_RETRY_FEE_BURN
            else:
                # Naive retry success probability
                if txn.failure_code in ["GATEWAY_TIMEOUT", "BAD_REQUEST_PAYMENT_TIMED_OUT", "UPI_COLLECT_TIMEOUT"]:
                    if txn.attempt_number == 1:
                        base_successes += 1
                        base_recovered_amount += txn.amount
                    else:
                        base_unnecessary_fees += settings.ESTIMATED_RETRY_FEE_BURN
                elif txn.failure_code in ["INSUFFICIENT_FUNDS", "AUTHENTICATION_FAILED"]:
                    # Naive retry without alternate link or nudge has very poor success (~14%)
                    if (hash(txn.transaction_id) % 100) < 14:
                        base_successes += 1
                        base_recovered_amount += txn.amount
                    else:
                        base_unnecessary_fees += settings.ESTIMATED_RETRY_FEE_BURN

            # -----------------------------------------------------------------
            # 2. RECOVERYOS EVALUATION (AI Diagnosis + Deterministic Policy)
            # -----------------------------------------------------------------
            trace = RecoveryAgent.process_event(txn)

            if trace.final_action == RecoveryAction.DO_NOTHING:
                ros_prevented_actions += 1
                ros_fees_saved += trace.gateway_fee_saved
                if is_high_risk:
                    ros_high_risk_blocked += 1

            elif trace.final_action == RecoveryAction.ESCALATE_TO_HUMAN:
                if is_high_risk:
                    ros_high_risk_blocked += 1
                # Escalated cases are safeguarded against accidental auto-charge

            elif trace.final_action in [RecoveryAction.RETRY_PAYMENT, RecoveryAction.SEND_PAYMENT_LINK, RecoveryAction.SEND_WHATSAPP_NUDGE]:
                ros_recoverable_identified += 1
                ros_attempts_gated += 1
                if trace.amount_recovered > 0:
                    ros_successes += 1
                    ros_recovered_amount += trace.amount_recovered

        base_rec_rate = (base_recovered_amount / total_at_risk * 100) if total_at_risk > 0 else 0.0
        ros_rec_rate = (ros_recovered_amount / total_at_risk * 100) if total_at_risk > 0 else 0.0
        net_economic_lift = (ros_recovered_amount + ros_fees_saved) - (base_recovered_amount - base_unnecessary_fees)

        return BatchBenchmarkResult(
            total_transactions_analyzed=total_txns,
            at_risk_amount=round(total_at_risk, 2),
            
            baseline_recovery_attempts=base_attempts,
            baseline_successful_recoveries=base_successes,
            baseline_recovered_amount=round(base_recovered_amount, 2),
            baseline_recovery_rate=round(base_rec_rate, 2),
            baseline_unnecessary_fees_burned=round(base_unnecessary_fees, 2),
            baseline_high_risk_actions_taken=base_high_risk_actions,
            
            recoveryos_recoverable_identified=ros_recoverable_identified,
            recoveryos_attempts_gated=ros_attempts_gated,
            recoveryos_successful_recoveries=ros_successes,
            recoveryos_recovered_amount=round(ros_recovered_amount, 2),
            recoveryos_recovery_rate=round(ros_rec_rate, 2),
            recoveryos_unnecessary_actions_prevented=ros_prevented_actions,
            recoveryos_gateway_fees_saved=round(ros_fees_saved, 2),
            recoveryos_high_risk_actions_blocked=ros_high_risk_blocked,
            recoveryos_net_economic_lift=round(net_economic_lift, 2)
        )
