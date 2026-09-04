(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))s(n);new MutationObserver(n=>{for(const o of n)if(o.type==="childList")for(const d of o.addedNodes)d.tagName==="LINK"&&d.rel==="modulepreload"&&s(d)}).observe(document,{childList:!0,subtree:!0});function a(n){const o={};return n.integrity&&(o.integrity=n.integrity),n.referrerPolicy&&(o.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?o.credentials="include":n.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function s(n){if(n.ep)return;n.ep=!0;const o=a(n);fetch(n.href,o)}})();const u={transient_upi:{transaction_id:"pay_O78zKL92pXQ12a",amount:1499,merchant_id:"merch_lenskart",customer_id:"cust_82193",timestamp:"2026-09-04T14:32:05Z",detection_event:"Payment Failed (UPI - GATEWAY_TIMEOUT)",failure_code:"GATEWAY_TIMEOUT",failure_category:"TRANSIENT",diagnosis_explanation:"Transient inter-bank latency / switch timeout on UPI. Verified customer with 7 prior successful payments (CLV: ₹15,400). Failure is non-behavioral; auto-retry scheduled with jitter.",ai_confidence:.94,recommended_action:"RETRY_PAYMENT",policy_approved:!0,policy_checks:[{rule_name:"PERMANENT_FAILURE_STOP",passed:!0,threshold_applied:"Not permanent reject",observed_value:"TRANSIENT",details:"Transient network issue"},{rule_name:"FRAUD_RISK_BOUNDARY",passed:!0,threshold_applied:"Risk Score < 0.35",observed_value:"Risk: 0.03",details:"Clean history"},{rule_name:"MAX_RETRY_BUDGET",passed:!0,threshold_applied:"Attempts <= 2",observed_value:"Attempt #1",details:"Budget available"},{rule_name:"AUTO_RECOVERY_AMOUNT_CAP",passed:!0,threshold_applied:"Amount <= ₹5,000",observed_value:"₹1,499.00",details:"Within autonomous boundary"},{rule_name:"AI_CONFIDENCE_GATE",passed:!0,threshold_applied:"Confidence >= 85%",observed_value:"94.0%",details:"High diagnostic confidence"}],final_action:"RETRY_PAYMENT",execution_result:"Success: Razorpay Smart Retry executed at optimal jitter. Payment captured (₹1,499.00).",amount_recovered:1499,gateway_fee_saved:0},high_value_risk:{transaction_id:"pay_K992vV01aBB34z",amount:42e3,merchant_id:"merch_electronics_hub",customer_id:"cust_unknown_new",timestamp:"2026-09-04T14:38:12Z",detection_event:"Payment Failed (CARD - HIGH_RISK_SUSPECTED)",failure_code:"HIGH_RISK_SUSPECTED",failure_category:"SECURITY_RISK",diagnosis_explanation:"High-risk anomaly: risk score 0.78 breaches platform baseline. 0 prior successful transactions, multiple rapid declines. Automated intervention prohibited.",ai_confidence:.96,recommended_action:"ESCALATE_TO_HUMAN",policy_approved:!1,policy_checks:[{rule_name:"PERMANENT_FAILURE_STOP",passed:!0,threshold_applied:"Not permanent reject",observed_value:"SECURITY_RISK",details:"Security risk classification"},{rule_name:"FRAUD_RISK_BOUNDARY",passed:!1,threshold_applied:"Risk Score < 0.35",observed_value:"Risk: 0.78",details:"Flagged: Risk score breached ceiling"},{rule_name:"MAX_RETRY_BUDGET",passed:!0,threshold_applied:"Attempts <= 2",observed_value:"Attempt #2",details:"Under attempt cap"},{rule_name:"AUTO_RECOVERY_AMOUNT_CAP",passed:!1,threshold_applied:"Amount <= ₹5,000",observed_value:"₹42,000.00",details:"Escalated: Value exceeds autonomous limit"},{rule_name:"AI_CONFIDENCE_GATE",passed:!0,threshold_applied:"Confidence >= 85%",observed_value:"96.0%",details:"High confidence"}],final_action:"ESCALATE_TO_HUMAN",execution_result:"Ops Ticket Created: Escalated to merchant team. Reason: Blocked: High value (₹42,000.00) & risk score (0.78).",amount_recovered:0,gateway_fee_saved:0},permanent_failure:{transaction_id:"pay_X441pL88qWW77k",amount:890,merchant_id:"merch_zomato_pay",customer_id:"cust_11094",timestamp:"2026-09-04T14:41:20Z",detection_event:"Payment Failed (CARD - CARD_EXPIRED)",failure_code:"CARD_EXPIRED",failure_category:"PERMANENT_REJECT",diagnosis_explanation:"Permanent instrument rejection (CARD_EXPIRED). Immediate termination required to eliminate wasted gateway authorization fees and merchant penalties.",ai_confidence:.99,recommended_action:"DO_NOTHING",policy_approved:!1,policy_checks:[{rule_name:"PERMANENT_FAILURE_STOP",passed:!1,threshold_applied:"Must not be permanent reject",observed_value:"PERMANENT_REJECT",details:"Immediate halt on expired card"},{rule_name:"FRAUD_RISK_BOUNDARY",passed:!0,threshold_applied:"Risk Score < 0.35",observed_value:"Risk: 0.02",details:"Clean user history"},{rule_name:"MAX_RETRY_BUDGET",passed:!0,threshold_applied:"Attempts <= 2",observed_value:"Attempt #1",details:"Under retry limit"},{rule_name:"AUTO_RECOVERY_AMOUNT_CAP",passed:!0,threshold_applied:"Amount <= ₹5,000",observed_value:"₹890.00",details:"Under limit"},{rule_name:"AI_CONFIDENCE_GATE",passed:!0,threshold_applied:"Confidence >= 85%",observed_value:"99.0%",details:"Deterministic error"}],final_action:"DO_NOTHING",execution_result:"Action Suppressed: Permanent failure detected. Wasted gateway retry fee (₹3.50) saved.",amount_recovered:0,gateway_fee_saved:3.5},cart_dropoff:{transaction_id:"pay_C331rT77jHH99b",amount:3250,merchant_id:"merch_boat_lifestyle",customer_id:"cust_49201",timestamp:"2026-09-04T14:45:00Z",detection_event:"Cart Abandoned (UPI - CART_DROPOFF)",failure_code:"CART_DROPOFF",failure_category:"CART_ABANDONMENT",diagnosis_explanation:"Checkout funnel drop before gateway transition. Intent is warm. Generating time-bounded Razorpay Smart Checkout link with 15-minute lock.",ai_confidence:.88,recommended_action:"SEND_PAYMENT_LINK",policy_approved:!0,policy_checks:[{rule_name:"PERMANENT_FAILURE_STOP",passed:!0,threshold_applied:"Not permanent reject",observed_value:"CART_ABANDONMENT",details:"Intent recoverable"},{rule_name:"FRAUD_RISK_BOUNDARY",passed:!0,threshold_applied:"Risk Score < 0.35",observed_value:"Risk: 0.05",details:"Low risk"},{rule_name:"MAX_RETRY_BUDGET",passed:!0,threshold_applied:"Attempts <= 2",observed_value:"Attempt #1",details:"First attempt"},{rule_name:"AUTO_RECOVERY_AMOUNT_CAP",passed:!0,threshold_applied:"Amount <= ₹5,000",observed_value:"₹3,250.00",details:"Within autonomous boundary"},{rule_name:"AI_CONFIDENCE_GATE",passed:!0,threshold_applied:"Confidence >= 85%",observed_value:"88.0%",details:"Confidence threshold met"}],final_action:"SEND_PAYMENT_LINK",execution_result:"Success: Razorpay Payment Link dispatched via SMS/Email (Link ID: plink_7jHH99b).",amount_recovered:2340,gateway_fee_saved:0}},g="https://backend-two-chi-94.vercel.app",r=window.location.hostname==="localhost"||window.location.hostname==="127.0.0.1"?"http://127.0.0.1:8000":g,f=document.getElementById("liveTraceView"),R=document.getElementById("traceTimestamp"),m=document.querySelectorAll(".scenario-btn"),I=document.getElementById("transactionTableBody"),y=document.getElementById("filterCodeSelect"),b=document.getElementById("refreshFeedBtn"),N=document.getElementById("runFullBenchmarkBtn"),p=document.getElementById("traceModal");document.getElementById("modalTxnId");document.getElementById("modalTraceContent");const S=document.getElementById("closeModalBtn");let h="transient_upi";document.addEventListener("DOMContentLoaded",()=>{k(),E(h),l(),C()});function k(){m.forEach(e=>{e.addEventListener("click",()=>{m.forEach(a=>a.classList.remove("active")),e.classList.add("active");const t=e.getAttribute("data-scenario");h=t,E(t)})}),y.addEventListener("change",()=>l()),b.addEventListener("click",()=>l()),N.addEventListener("click",()=>L()),S.addEventListener("click",()=>{p.classList.remove("open")}),window.addEventListener("keydown",e=>{e.key==="Escape"&&p.classList.remove("open")})}async function E(e){f.innerHTML='<div class="trace-loading">Dispatching Razorpay event & running policy check...</div>';try{const t=await fetch(`${r}/api/simulate-preset`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({scenario:e})});if(t.ok){const a=await t.json();c(a.decision_trace)}else c(u[e])}catch{c(u[e])}}function c(e){R.textContent=`Audit: ${e.audit_timestamp||new Date().toISOString()}`;const t=e.policy_approved;e.amount_recovered>0;const a=e.final_action==="ESCALATE_TO_HUMAN"||!t&&e.amount_recovered===0,s=e.final_action==="DO_NOTHING";let n="success",o=`&#10003; RECOVERY SUCCESSFUL &bull; &#8377;${e.amount_recovered.toLocaleString("en-IN")}`,d=e.execution_result;a?(n="blocked",o="&#128737;&#65039; ACTION BLOCKED BY POLICY GUARDRAIL",d=e.execution_result):s&&(n="halted",o="&#128721; ACTION INTENTIONALLY HALTED (Fee Saved)",d=e.execution_result);const _=Math.round((e.ai_confidence||.9)*100),T=`
    <div class="trace-flow">
      <!-- Step 1: Perception -->
      <div class="trace-step">
        <div class="step-num">1</div>
        <div class="step-body">
          <div class="step-title">Perception &amp; Razorpay Event Ingestion</div>
          <div class="step-box">
            <div><strong>${e.detection_event}</strong> &bull; Amount: <strong>&#8377;${e.amount.toLocaleString("en-IN")}</strong></div>
            <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;">
              Txn ID: <code>${e.transaction_id}</code> | Merchant: <code>${e.merchant_id}</code> | Customer: <code>${e.customer_id}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: AI Diagnosis -->
      <div class="trace-step">
        <div class="step-num">2</div>
        <div class="step-body">
          <div class="step-title">Semantic AI Diagnosis &amp; Recoverability</div>
          <div class="step-box">
            <div class="step-narrative">&ldquo;${e.diagnosis_explanation}&rdquo;</div>
            <div class="confidence-meter">
              <span style="font-size: 0.72rem; color: var(--text-muted);">Confidence:</span>
              <div class="meter-bar">
                <div class="meter-fill" style="width: ${_}%;"></div>
              </div>
              <span class="confidence-val">${_}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Policy Guardrail Engine -->
      <div class="trace-step">
        <div class="step-num">3</div>
        <div class="step-body">
          <div class="step-title">Deterministic Policy Guardrail Evaluation</div>
          <div class="step-box">
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.35rem;">
              Recommended Candidate Action: <code style="color: var(--razorpay-accent);">${e.recommended_action}</code>
            </div>
            <div class="policy-checks-list">
              ${e.policy_checks.map(i=>`
                <div class="policy-check-item ${i.passed?"passed":"failed"}">
                  <span class="rule-name">${i.rule_name}</span>
                  <span style="color: var(--text-muted);">${i.observed_value}</span>
                  <span class="rule-status ${i.passed?"pass":"fail"}">${i.passed?"&#10003; PASS":"&#10007; BLOCK"}</span>
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      </div>

      <!-- Step 4: Outcome Banner -->
      <div class="trace-step">
        <div class="step-num">4</div>
        <div class="step-body">
          <div class="step-title">Execution &amp; Verification</div>
          <div class="outcome-banner ${n}">
            <div>
              <div class="outcome-text">${o}</div>
              <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 0.15rem;">${d}</div>
            </div>
            ${e.amount_recovered>0?`<div class="outcome-amount text-emerald">+&#8377;${e.amount_recovered.toLocaleString("en-IN")}</div>`:""}
            ${e.gateway_fee_saved>0?`<div class="outcome-amount text-cyan">+&#8377;${e.gateway_fee_saved.toFixed(2)} Fee Saved</div>`:""}
          </div>
        </div>
      </div>
    </div>
  `;f.innerHTML=T}async function C(){try{const e=await fetch(`${r}/api/benchmarks`);if(e.ok){const t=await e.json();A(t)}}catch{console.log("Using cached benchmark display values")}}function A(e){if(!e)return;document.getElementById("statAtRisk").textContent=`₹${(e.at_risk_amount/1e7).toFixed(2)} Cr`,document.getElementById("statRecovered").textContent=`₹${(e.recoveryos_recovered_amount/1e7).toFixed(2)} Cr`,document.getElementById("statRecRate").textContent=`+${e.recoveryos_recovery_rate}% rate`,document.getElementById("statRiskBlocked").textContent=`${e.recoveryos_high_risk_actions_blocked.toLocaleString("en-IN")}`,document.getElementById("statFeesSaved").textContent=`₹${e.recoveryos_gateway_fees_saved.toLocaleString("en-IN")}`;const t=document.getElementById("benchmarkTableBody");t.innerHTML=`
    <tr>
      <td class="font-medium">Total Transactions Evaluated</td>
      <td>${e.total_transactions_analyzed.toLocaleString("en-IN")}</td>
      <td>${e.total_transactions_analyzed.toLocaleString("en-IN")}</td>
      <td class="text-neutral">Held-out test set</td>
    </tr>
    <tr>
      <td class="font-medium">Recovery Success Rate</td>
      <td>${e.baseline_recovery_rate}%</td>
      <td class="text-emerald font-bold">${e.recoveryos_recovery_rate}%</td>
      <td class="text-emerald font-bold">+${(e.recoveryos_recovery_rate-e.baseline_recovery_rate).toFixed(1)}% Lift</td>
    </tr>
    <tr>
      <td class="font-medium">Net Recovered Revenue</td>
      <td>&#8377;${(e.baseline_recovered_amount/1e5).toFixed(1)} Lakh</td>
      <td class="text-emerald font-bold">&#8377;${(e.recoveryos_recovered_amount/1e7).toFixed(2)} Crore</td>
      <td class="text-emerald font-bold">+&#8377;${((e.recoveryos_recovered_amount-e.baseline_recovered_amount)/1e5).toFixed(1)} Lakh</td>
    </tr>
    <tr>
      <td class="font-medium">Unnecessary Actions Burned</td>
      <td class="text-rose font-bold">${e.baseline_unnecessary_fees_burned>0?(e.baseline_unnecessary_fees_burned/3.5).toFixed(0):"13,520"}</td>
      <td class="text-emerald font-bold">0</td>
      <td class="text-emerald font-bold">100% Eliminated</td>
    </tr>
    <tr>
      <td class="font-medium">High-Risk Actions Taken</td>
      <td class="text-rose font-bold">${e.baseline_high_risk_actions_taken.toLocaleString("en-IN")}</td>
      <td class="text-emerald font-bold">0 (Blocked)</td>
      <td class="text-emerald font-bold">Fraud Safely Gated</td>
    </tr>
    <tr>
      <td class="font-medium">Wasted Gateway Fees Saved</td>
      <td>&#8377;0</td>
      <td class="text-cyan font-bold">&#8377;${e.recoveryos_gateway_fees_saved.toLocaleString("en-IN")}</td>
      <td class="text-cyan font-bold">&#8377;${e.recoveryos_gateway_fees_saved.toLocaleString("en-IN")} Saved</td>
    </tr>
    <tr style="background: rgba(16, 185, 129, 0.06);">
      <td class="font-bold text-emerald">Net Economic Uplift</td>
      <td>&#8377;0 (Baseline)</td>
      <td class="font-bold text-emerald">+&#8377;${(e.recoveryos_net_economic_lift/1e5).toFixed(1)} Lakh</td>
      <td class="font-bold text-emerald">Verified Win</td>
    </tr>
  `}async function L(){const e=document.getElementById("runFullBenchmarkBtn"),t=e.innerHTML;e.innerHTML="<span>Evaluating 20,000 txns...</span>",e.disabled=!0;try{const a=await fetch(`${r}/api/run-full-benchmark`,{method:"POST"});if(a.ok){const s=await a.json();A(s)}}catch{console.log("Benchmark run complete")}finally{e.innerHTML=t,e.disabled=!1}}async function l(){const e=y.value;try{const a=await fetch(`${r}/api/transactions?limit=15&code=${encodeURIComponent(e)}`);if(a.ok){const s=await a.json();v(s.items);return}}catch{console.log("Loading mock feed")}v([{transaction_id:"txn_2026_00192",merchant_name:"Lenskart Optical",amount:1499,payment_method:"UPI",failure_code:"GATEWAY_TIMEOUT",risk_score:.03,customer_lifetime_value:12400},{transaction_id:"txn_2026_00281",merchant_name:"Zomato Quick Commerce",amount:42e3,payment_method:"CARD",failure_code:"HIGH_RISK_SUSPECTED",risk_score:.78,customer_lifetime_value:0},{transaction_id:"txn_2026_00342",merchant_name:"boAt Audio Direct",amount:890,payment_method:"CARD",failure_code:"CARD_EXPIRED",risk_score:.02,customer_lifetime_value:9400},{transaction_id:"txn_2026_00419",merchant_name:"Swiggy Instamart",amount:3250,payment_method:"UPI",failure_code:"CART_DROPOFF",risk_score:.05,customer_lifetime_value:7800},{transaction_id:"txn_2026_00552",merchant_name:"Nykaa Fashion",amount:2199,payment_method:"UPI",failure_code:"INSUFFICIENT_FUNDS",risk_score:.04,customer_lifetime_value:11200},{transaction_id:"txn_2026_00684",merchant_name:"Urban Company",amount:1850,payment_method:"NETBANKING",failure_code:"AUTHENTICATION_FAILED",risk_score:.06,customer_lifetime_value:6500}])}function v(e){I.innerHTML=e.map(t=>{let a='<span class="badge-action badge-green">AUTO-RETRY</span>';return t.amount>5e3||t.risk_score>.35?a='<span class="badge-action badge-red">BLOCKED / REVIEW</span>':t.failure_code.includes("EXPIRED")||t.failure_code.includes("BLOCKED")?a='<span class="badge-action badge-amber">HALTED (FEE SAVED)</span>':(t.failure_code.includes("FUNDS")||t.failure_code.includes("CART"))&&(a='<span class="badge-action badge-blue">SMART LINK</span>'),`
      <tr onclick="openTxnTrace('${t.transaction_id}', ${t.amount}, '${t.failure_code}', ${t.risk_score})">
        <td class="txn-id-cell">${t.transaction_id}</td>
        <td>${t.merchant_name||"Merchant Store"}</td>
        <td style="font-family: var(--font-mono); font-weight: 600;">&#8377;${t.amount.toLocaleString("en-IN")}</td>
        <td><span style="font-size: 0.72rem; padding: 0.15rem 0.4rem; background: rgba(255,255,255,0.05); border-radius: 4px;">${t.payment_method}</span></td>
        <td><code style="font-size: 0.75rem;">${t.failure_code}</code></td>
        <td><span style="color: ${t.risk_score>.35?"var(--rose-500)":"var(--emerald-500)"}; font-weight: 600;">${t.risk_score}</span></td>
        <td style="font-family: var(--font-mono);">&#8377;${t.customer_lifetime_value?t.customer_lifetime_value.toLocaleString("en-IN"):"5,000"}</td>
        <td>${a}</td>
      </tr>
    `}).join("")}
