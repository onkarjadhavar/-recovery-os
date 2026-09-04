# 5-Minute Video Presentation Script
### RecoveryOS — Autonomous AI Revenue Recovery Decision Engine
**Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026**

---

### [0:00 – 0:30] — The Hook & Problem Statement
* **Visual:** Speaker on camera / Screen displaying standard payment failure screen ("Payment Failed").
* **Audio:**
  > "Every failed payment isn’t just lost revenue—it’s a critical business decision. Today, 15 to 25 percent of all digital transactions in India fail. 
  > But the industry standard response is crude: **naive retrying**. 
  > Platforms blindly retry every failure, spamming customers with SMS links, burning lakhs in gateway authorization fees on expired cards, and even retrying high-risk transactions that trigger catastrophic chargebacks.
  > We built **RecoveryOS**: an autonomous recovery decision and policy engine that determines *if, how, and when* recovery should be attempted before any tool fires."

---

### [0:30 – 1:15] — Architecture & AI Judgment
* **Visual:** Switch to Architecture Diagram in README or Dashboard.
* **Audio:**
  > "Razorpay explicitly evaluates AI Judgment. We deliberately do NOT let LLMs calculate money or enforce safety boundaries.
  > Instead, RecoveryOS uses a two-layer architecture:
  > First, a **Semantic AI Perception Layer** analyzes failure codes, inter-bank latency signals, customer lifetime value, and historical success rates to categorize failures and recommend recovery interventions.
  > Second, an un-bypassable **Deterministic Policy Engine** enforces strict financial invariants:
  > An autonomous recovery ceiling of 5,000 rupees, a hard cap of 2 retry attempts, a fraud risk ceiling of 0.35, and mandatory stopping rules for permanent failures."

---

### [1:15 – 2:15] — Demo 1: The Money Moment (Instant Recovery)
* **Visual:** Dashboard screen. Click **Scenario 1: Transient UPI Timeout**.
* **Audio:**
  > "Let's see this live. Here is a merchant event from a loyal customer with seven prior successful orders and an order value of 1,499 rupees.
  > The payment failed due to a bank switch timeout on UPI.
  > Notice what RecoveryOS does:
  > Step 1: It ingests the Razorpay webhook.
  > Step 2: The AI diagnoses this as non-behavioral inter-bank latency with 94% confidence.
  > Step 3: It passes through our Policy Engine—all 5 checks pass: amount under 5,000 rupees, low risk, within attempt budget.
  > Step 4: The system executes a jittered smart retry—and captures the payment.
  > **1,499 rupees recovered.**"

---

### [2:15 – 3:15] — Demo 2: The Safety Moment (Blocked Action)
* **Visual:** Click **Scenario 2: High-Value Risk Breach**.
* **Audio:**
  > "Now, here is what sets RecoveryOS apart: **knowing when NOT to act**.
  > An order for 42,000 rupees comes in with an anomalous IP address and a risk score of 0.78.
  > A naive dunning bot might attempt recovery.
  > But watch our Policy Engine:
  > The Fraud Risk Boundary **fails**.
  > The Autonomous Amount Cap **fails**.
  > The action is **immediately blocked**. No automated charge occurs. Instead, it creates an audited operational ticket for human supervisor review.
  > This is true defense-in-depth."

---

### [3:15 – 3:55] — Demo 3: The Cost Saver (Stopping Rules)
* **Visual:** Click **Scenario 3: Expired Instrument**.
* **Audio:**
  > "Next, look at Scenario 3: an 890 rupee transaction fails with `CARD_EXPIRED`.
  > Standard payment systems retry this two or three times, burning 3.50 rupees in gateway fees every time.
  > RecoveryOS recognizes this as a permanent instrument termination.
  > The Policy Engine enforces the **Permanent Failure Stopping Rule** and intentionally halts action.
  > That unnecessary fee is saved—directly protecting merchant margins."

---

### [3:55 – 4:35] — Real 20,000 Transaction Benchmark Results
* **Visual:** Scroll to the **Held-Out Benchmark Evaluation** table on the dashboard.
* **Audio:**
  > "We didn't just test 4 mock transactions. We evaluated RecoveryOS against a Naive Retry baseline on **20,000 held-out synthetic transactions**.
  > The results speak for themselves:
  > Our recovery rate reached **66.8%**, compared to 32.4% for the baseline—a **34.4% lift**.
  > Over **74 Lakh rupees in additional revenue was recovered**.
  > Over 1,000 high-risk actions were stopped dead in their tracks.
  > And over 36,000 rupees in wasted gateway authorization fees were eliminated."

---

### [4:35 – 5:00] — Conclusion & Submission Wrap-Up
* **Visual:** Dashboard full view or Speaker.
* **Audio:**
  > "RecoveryOS transforms revenue recovery from blunt, aggressive retrying into an audited, bounded, and intelligent decision science.
  > It is fully compatible with Razorpay webhooks, production-tested with unit test suites, and designed for immediate impact.
  > Thank you for reviewing RecoveryOS for the Razorpay AI Buildathon 2026."
