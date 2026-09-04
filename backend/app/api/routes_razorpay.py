"""
Razorpay Webhook Handling & Event Simulation for RecoveryOS

Supports real HMAC-SHA256 signature verification according to Razorpay specifications,
as well as synthetic webhook event dispatching for demonstrations.
"""
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from ..core.config import settings
from ..core.agent import RecoveryAgent
from ..models.schemas import (
    TransactionEvent,
    DecisionTrace,
    FailureCategory,
    RecoveryAction
)

# In-memory idempotency cache to prevent duplicate recovery executions
PROCESSED_WEBHOOK_EVENTS: Dict[str, DecisionTrace] = {}

class RazorpayWebhookHandler:
    """
    Handles inbound Razorpay webhook events (e.g. payment.failed, order.paid).
    Enforces idempotency, signature verification, and safe event handling.
    """

    @staticmethod
    def verify_webhook_signature(body_bytes: bytes, received_signature: str, secret: str = None) -> bool:
        """
        Verifies HMAC-SHA256 signature from Razorpay.
        Header: X-Razorpay-Signature
        """
        if not received_signature:
            return False
        secret_key = secret or settings.RAZORPAY_WEBHOOK_SECRET
        expected_signature = hmac.new(
            secret_key.encode("utf-8"),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, received_signature)

    @classmethod
    def parse_and_process_event(cls, webhook_payload: Dict[str, Any]) -> DecisionTrace:
        """
        Extracts payment event from standard Razorpay webhook structure,
        enforces idempotency & already-captured checks, and executes RecoveryOS loop.
        """
        event_type = webhook_payload.get("event", "payment.failed")
        payload = webhook_payload.get("payload", {})
        payment_entity = payload.get("payment", {}).get("entity", {})

        # Extract fields from standard Razorpay payload
        txn_id = payment_entity.get("id", f"pay_sim_{hash(json.dumps(webhook_payload, sort_keys=True)) % 1000000}")
        
        # Idempotency Check: Prevent duplicate processing of the same transaction event
        if txn_id in PROCESSED_WEBHOOK_EVENTS:
            existing = PROCESSED_WEBHOOK_EVENTS[txn_id]
            # Return idempotent replay trace
            return DecisionTrace(
                transaction_id=existing.transaction_id,
                amount=existing.amount,
                merchant_id=existing.merchant_id,
                customer_id=existing.customer_id,
                timestamp=existing.timestamp,
                detection_event=f"[IDEMPOTENT] {existing.detection_event}",
                failure_code=existing.failure_code,
                failure_category=existing.failure_category,
                diagnosis_explanation=f"Idempotency Guard: Event {txn_id} previously processed. Duplicate recovery suppressed.",
                ai_confidence=existing.ai_confidence,
                recommended_action=existing.recommended_action,
                policy_approved=existing.policy_approved,
                policy_checks=existing.policy_checks,
                final_action=existing.final_action,
                execution_result=f"IDEMPOTENT REPLAY: {existing.execution_result} (No duplicate action fired)",
                amount_recovered=0.0,
                gateway_fee_saved=existing.gateway_fee_saved,
                audit_timestamp=existing.audit_timestamp
            )

        amount_paisa = payment_entity.get("amount", 149900)  # Amount in paise
        amount_inr = round(amount_paisa / 100.0, 2)
        
        error_code = payment_entity.get("error_code", "GATEWAY_TIMEOUT")
        error_description = payment_entity.get("error_description", "Payment timeout during bank settlement")
        method = payment_entity.get("method", "upi").upper()
        status = payment_entity.get("status", "failed")
        
        notes = payment_entity.get("notes", {})
        customer_id = payment_entity.get("customer_id") or notes.get("customer_id", "cust_live_demo")
        merchant_id = notes.get("merchant_id", "merch_demo_store")

        # Check: If payment is already captured, do NOT run recovery
        if event_type in ["payment.captured", "order.paid"] or status == "captured":
            trace = DecisionTrace(
                transaction_id=txn_id,
                amount=amount_inr,
                merchant_id=merchant_id,
                customer_id=customer_id,
                timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                detection_event=f"Payment Event ({method} - {event_type})",
                failure_code="ALREADY_CAPTURED",
                failure_category=FailureCategory.PERMANENT_REJECT,
                diagnosis_explanation="Payment is already successfully captured. Automated recovery halted.",
                ai_confidence=1.0,
                recommended_action=RecoveryAction.DO_NOTHING,
                policy_approved=False,
                policy_checks=[],
                final_action=RecoveryAction.DO_NOTHING,
                execution_result="Action Suppressed: Payment already captured. Duplicate money movement prevented.",
                amount_recovered=0.0,
                gateway_fee_saved=settings.ESTIMATED_RETRY_FEE_BURN,
                audit_timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            PROCESSED_WEBHOOK_EVENTS[txn_id] = trace
            return trace

        txn = TransactionEvent(
            transaction_id=txn_id,
            merchant_id=merchant_id,
            customer_id=customer_id,
            amount=amount_inr,
            payment_method=method,
            failure_reason=error_description,
            failure_code=error_code,
            attempt_number=notes.get("attempt_number", 1),
            customer_previous_successes=notes.get("customer_previous_successes", 5),
            customer_previous_failures=notes.get("customer_previous_failures", 0),
            customer_lifetime_value=notes.get("customer_lifetime_value", 12500.0),
            risk_score=notes.get("risk_score", 0.04)
        )

        trace = RecoveryAgent.process_event(txn)
        PROCESSED_WEBHOOK_EVENTS[txn_id] = trace
        return trace

    @classmethod
    def generate_mock_webhook(cls, scenario_key: str) -> Dict[str, Any]:
        """
        Generates genuine Razorpay-formatted webhook payloads for quick testing.
        """
        scenarios = {
            "transient_upi": {
                "event": "payment.failed",
                "entity": "event",
                "contains": ["payment"],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_O78zKL92pXQ12a",
                            "amount": 149900,
                            "currency": "INR",
                            "status": "failed",
                            "method": "upi",
                            "error_code": "GATEWAY_TIMEOUT",
                            "error_description": "Bank switch timeout during NPCI settlement",
                            "error_source": "gateway",
                            "error_step": "payment_authorization",
                            "notes": {
                                "merchant_id": "merch_lenskart",
                                "customer_id": "cust_82193",
                                "customer_previous_successes": 7,
                                "customer_previous_failures": 0,
                                "customer_lifetime_value": 15400.0,
                                "risk_score": 0.03,
                                "attempt_number": 1
                            }
                        }
                    }
                }
            },
            "high_value_risk": {
                "event": "payment.failed",
                "entity": "event",
                "contains": ["payment"],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_K992vV01aBB34z",
                            "amount": 4200000,  # ₹42,000
                            "currency": "INR",
                            "status": "failed",
                            "method": "card",
                            "error_code": "HIGH_RISK_SUSPECTED",
                            "error_description": "Anomalous transaction frequency from flagged IP range",
                            "error_source": "internal",
                            "error_step": "risk_check",
                            "notes": {
                                "merchant_id": "merch_electronics_hub",
                                "customer_id": "cust_unknown_new",
                                "customer_previous_successes": 0,
                                "customer_previous_failures": 3,
                                "customer_lifetime_value": 0.0,
                                "risk_score": 0.78,
                                "attempt_number": 2
                            }
                        }
                    }
                }
            },
            "permanent_failure": {
                "event": "payment.failed",
                "entity": "event",
                "contains": ["payment"],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_X441pL88qWW77k",
                            "amount": 89000,  # ₹890
                            "currency": "INR",
                            "status": "failed",
                            "method": "card",
                            "error_code": "CARD_EXPIRED",
                            "error_description": "The card has expired and cannot be charged",
                            "error_source": "bank",
                            "error_step": "card_validation",
                            "notes": {
                                "merchant_id": "merch_zomato_pay",
                                "customer_id": "cust_11094",
                                "customer_previous_successes": 12,
                                "customer_previous_failures": 1,
                                "customer_lifetime_value": 9400.0,
                                "risk_score": 0.02,
                                "attempt_number": 1
                            }
                        }
                    }
                }
            },
            "cart_dropoff": {
                "event": "payment.failed",
                "entity": "event",
                "contains": ["payment"],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_C331rT77jHH99b",
                            "amount": 325000,  # ₹3,250
                            "currency": "INR",
                            "status": "failed",
                            "method": "upi",
                            "error_code": "CART_DROPOFF",
                            "error_description": "Customer exited checkout at UPI QR screen",
                            "error_source": "customer",
                            "error_step": "intent_capture",
                            "notes": {
                                "merchant_id": "merch_boat_lifestyle",
                                "customer_id": "cust_49201",
                                "customer_previous_successes": 3,
                                "customer_previous_failures": 0,
                                "customer_lifetime_value": 7800.0,
                                "risk_score": 0.05,
                                "attempt_number": 1
                            }
                        }
                    }
                }
            }
        }
        return scenarios.get(scenario_key, scenarios["transient_upi"])
