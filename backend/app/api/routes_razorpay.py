"""
Razorpay Webhook Handling & Event Simulation for RecoveryOS

Supports real HMAC-SHA256 signature verification according to Razorpay specifications,
as well as synthetic webhook event dispatching for demonstrations.
"""
import hmac
import hashlib
import json
from typing import Dict, Any, Tuple
from ..core.config import settings
from ..core.agent import RecoveryAgent
from ..models.schemas import TransactionEvent, DecisionTrace

class RazorpayWebhookHandler:
    """
    Handles inbound Razorpay webhook events (e.g. payment.failed, order.paid).
    """

    @staticmethod
    def verify_webhook_signature(body_bytes: bytes, received_signature: str, secret: str = None) -> bool:
        """
        Verifies HMAC-SHA256 signature from Razorpay.
        Header: X-Razorpay-Signature
        """
        secret_key = secret or settings.RAZORPAY_WEBHOOK_SECRET
        expected_signature = hmac.new(
            secret_key.encode("utf-8"),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, received_signature)

    @staticmethod
    def parse_and_process_event(webhook_payload: Dict[str, Any]) -> DecisionTrace:
        """
        Extracts payment event from standard Razorpay webhook structure
        and executes RecoveryOS agentic decision loop.
        """
        event_type = webhook_payload.get("event", "payment.failed")
        payload = webhook_payload.get("payload", {})
        payment_entity = payload.get("payment", {}).get("entity", {})

        # Extract fields from standard Razorpay payload
        txn_id = payment_entity.get("id", f"pay_sim_{hash(json.dumps(webhook_payload)) % 1000000}")
        amount_paisa = payment_entity.get("amount", 149900)  # Amount in paise
        amount_inr = round(amount_paisa / 100.0, 2)
        
        error_code = payment_entity.get("error_code", "GATEWAY_TIMEOUT")
        error_description = payment_entity.get("error_description", "Payment timeout during bank settlement")
        method = payment_entity.get("method", "upi").upper()
        
        notes = payment_entity.get("notes", {})
        customer_id = payment_entity.get("customer_id") or notes.get("customer_id", "cust_live_demo")
        merchant_id = notes.get("merchant_id", "merch_demo_store")

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

        return RecoveryAgent.process_event(txn)

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
