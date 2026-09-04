# RecoveryOS Failure Recovery & Chaos Engineering Report

This document records the **10 verified failure cases and defensive mitigations** engineered and tested into RecoveryOS for the Razorpay AI Buildathon 2026. Every scenario is backed by automated tests in `backend/tests/test_chaos_and_safety.py`.

---

## 1. Duplicate Webhook Event / Replay Ingestion
- **Problem**: Payment gateway webhooks can be delivered multiple times due to network blips or retry delivery policies. A naive system would re-dispatch recovery workflows, double charging or spamming the customer.
- **Why It Happened**: Gateway at-least-once delivery semantics coupled with stateless HTTP webhook handlers.
- **Defensive Fix**: Implemented an in-memory event idempotency cache (`PROCESSED_WEBHOOK_EVENTS`) in `backend/app/api/routes_razorpay.py`. If an event ID is re-submitted, the system returns an `ignored_duplicate` status and aborts execution.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_01_duplicate_webhook_idempotency`

---

## 2. Already-Captured Payment Event
- **Problem**: In out-of-order webhook delivery, a `payment.failed` webhook might arrive *after* an alternate payment attempt for the same invoice was already marked `captured`.
- **Why It Happened**: Asynchronous queuing across payment switches and network race conditions.
- **Defensive Fix**: Webhook ingestion inspects the event type and payment status. If marked `payment.captured` or `status == "captured"`, the system immediately suppresses recovery (`Action: DO_NOTHING`).
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_02_already_captured_payment_safety`

---

## 3. Rogue or Hallucinatory AI Output Bypassing Policy
- **Problem**: If an LLM or probabilistic agent hallucinates and recommends `RETRY_PAYMENT` on a ₹45,000 transaction with high fraud risk, an unconstrained autonomous agent would cause financial loss.
- **Why It Happened**: Probabilistic models lack deterministic financial guarantees.
- **Defensive Fix**: Strict Separation of Concerns. The AI Diagnostic layer produces an *advisory recommendation* only. The Deterministic Policy Engine (`backend/app/core/policy_engine.py`) independently evaluates hard invariants. Even when the AI forces `RETRY_PAYMENT`, the Policy Engine blocks execution and forces `ESCALATE_TO_HUMAN`.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_03_ai_cannot_override_policy_engine`

---

## 4. High-Risk / Fraudulent Transaction Automation
- **Problem**: Attempting automated retries on stolen cards, anomalous IP velocities, or suspicious devices causes chargeback fines and merchant disputes.
- **Why It Happened**: Standard retry logic only looks at HTTP failure codes rather than telemetry risk indicators.
- **Defensive Fix**: Deterministic `FRAUD_RISK_BOUNDARY` rule. Any transaction with `risk_score > 0.35` is halted immediately and quarantined for human ops review.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_04_high_risk_transaction_blocked`

---

## 5. Low-Confidence AI Diagnostic Output
- **Problem**: When a failure code is ambiguous or payment switch telemetry is degraded, an AI model might output a low-confidence guess (e.g., 55% confidence). Automatically executing money movement on guesses is unsafe.
- **Why It Happened**: Model uncertainty in edge-case or multi-factor failure states.
- **Defensive Fix**: Enforced `AI_CONFIDENCE_GATE` invariant. If AI confidence is below 85% (`MIN_AI_CONFIDENCE = 0.85`), automated execution is blocked and routed to ops.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_05_low_confidence_ai_gated`

---

## 6. High-Value Transaction Autonomous Over-Execution
- **Problem**: High-ticket purchases (e.g., ₹42,000 consumer electronics) should not be automatically re-triggered without merchant or human review.
- **Why It Happened**: Flat retry logic treating a ₹99 order and a ₹1,00,000 order identically.
- **Defensive Fix**: Hard ceiling `MAX_AUTO_RECOVERY_AMOUNT = 5000.0`. Orders > ₹5,000.00 require human escalation.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_06_amount_limit_exceeded`

---

## 7. Infinite Retry Loop & Customer Fatigue
- **Problem**: Firing repeated retries against failing bank switches leads to user annoyance, card blocklisting, and wasted merchant authorization fees.
- **Why It Happened**: Missing transaction lifecycle state and unbounded retry budgets.
- **Defensive Fix**: Enforced `MAX_RETRY_BUDGET = 2`. Any attempt $> 2$ triggers automatic stopping rules.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_07_retry_budget_exhaustion`

---

## 8. Fee Burning on Permanent Instrument Failures
- **Problem**: Retrying expired cards (`CARD_EXPIRED`), non-existent VPAs, or closed accounts guarantees failure while incurring payment gateway fees (estimated ₹3.50/call).
- **Why It Happened**: Inability to differentiate transient bank latency from permanent account termination.
- **Defensive Fix**: Semantic classification mapping permanent decline codes to `PERMANENT_FAILURE_STOP`. Execution is immediately halted (`DO_NOTHING`), saving the merchant fees.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_08_permanent_failure_stop_rule`

---

## 9. Scenario 4 Amount Inconsistency
- **Problem**: Initial mock trace in Scenario 4 displayed ₹3,250 as the original cart value, but reported ₹2,340 as recovered without clear deterministic reasoning.
- **Why It Happened**: An outdated 72% collection discount factor remained in early simulation code.
- **Defensive Fix**: Replaced heuristic discounting with exact invoice amount recovery (`amount_recovered = txn.amount`) across both backend agent execution and frontend fallback presets.
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_09_scenario_4_consistent_amount`

---

## 10. Benchmark Metric Inconsistency & Non-Determinism
- **Problem**: Re-running benchmarks with random seeds produced varying metrics, eroding judge trust.
- **Why It Happened**: Unseeded PRNG and ambiguous test split labeling.
- **Defensive Fix**: Fixed PRNG seed to `20260904` in `synthetic_generator.py`. Benchmarks deterministically evaluate the exact 5,000 held-out test split (`txns[-5000:]`).
- **Automated Test Proving Fix**: `TestChaosAndSafety.test_10_benchmark_determinism_and_reproducibility`

---

## How to Run the Verification Suite
To execute all 15 policy, chaos, and safety unit tests:
```bash
python -m unittest discover -s backend/tests -v
```
Output:
```
Ran 15 tests in 0.005s — OK (15/15 Passed)
```
