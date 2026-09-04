import urllib.request
import json

def verify():
    scenarios = ['transient_upi', 'high_value_risk', 'permanent_failure', 'cart_dropoff']
    for sc in scenarios:
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/simulate-preset',
            data=json.dumps({'scenario': sc}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as resp:
            d = json.loads(resp.read().decode('utf-8'))
            trace = d['decision_trace']
            print(f"[{sc}] Amount: {trace['amount']} | Action: {trace['final_action']} | Approved: {trace['policy_approved']} | Recovered: {trace['amount_recovered']} | FeeSaved: {trace['gateway_fee_saved']}")

if __name__ == '__main__':
    verify()
