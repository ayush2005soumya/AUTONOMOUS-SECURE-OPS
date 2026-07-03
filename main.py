# # main.py
# import sys
# from vector_db import LightweightVectorDB
# from guardrails import run_guardrails, classify_intent
# from agents import reasoning_agent_audit, acting_agent_remediate

# if __name__ == "__main__":
#     target_file = "main.tf"
    
#     print("📚 Initializing Local Vector Database...")
#     vector_db = LightweightVectorDB()
#     try:
#         with open("rnm_security_policies.txt", "r") as f:
#             vector_db.add_document(f.read())
#     except FileNotFoundError:
#         print("Error: Policy file not found.")
#         sys.exit(1)

#     with open(target_file, "r") as f:
#         current_code = f.read()

#     # 1. Alignment & Security Checks
#     classify_intent(current_code)
#     run_guardrails(current_code)
    
#     # 2. RAG Retrieval 
#     retrieved_policy = vector_db.search("What are the security rules for AWS S3 buckets?")
    
#     # 3. Reasoning 
#     audit_report = reasoning_agent_audit(current_code, retrieved_policy)
    
#     if audit_report.get("is_secure"):
#         print("✅ Pipeline Passed: Infrastructure is secure.")
#         sys.exit(0)
        
#     print(f"\n🚨 VULNERABILITY DETECTED: {audit_report.get('vulnerability_found')}")
#     print(f"📋 POLICY-ALIGNED FIX PLAN: {audit_report.get('fix_plan')}\n")
    
#     # 4. Acting
#     secure_code = acting_agent_remediate(current_code, audit_report.get("fix_plan"))
    
#     # 5. Tool Calling (Save File)
#     with open(target_file, 'w') as file:
#         file.write(secure_code)
    
#     print("✅ Auto-Remediation Complete: File rewritten entirely by local open-source AI.")

# main.py
import sys
import os
import requests  # Ensure you run 'pip install requests'
from vector_db import LightweightVectorDB
from guardrails import run_guardrails, classify_intent
from agents import reasoning_agent_audit

def send_power_automate_alert(audit_report, target_file, author_email="dev@rnm-alliance.com"):
    print(f"📡 Sending Alert to Power Automate for {author_email}...")
    
    # This URL will be generated inside the Power Automate Portal
    WEBHOOK_URL = os.environ.get("POWER_AUTOMATE_WEBHOOK_URL", "YOUR_POWER_AUTOMATE_HTTP_URL_HERE")
    
    if WEBHOOK_URL == "YOUR_POWER_AUTOMATE_HTTP_URL_HERE":
        print("⚠️ Warning: Power Automate Webhook URL not configured. Skipping alert.")
        return

    payload = {
        "fileName": target_file,
        "developerEmail": author_email,
        "vulnerability": audit_report.get('vulnerability_found', 'Unknown vulnerability'),
        "fixPlan": audit_report.get('fix_plan', 'No fix plan provided')
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})
        if response.status_code in [200, 202]:
            print("✅ Alert successfully dispatched to Power Automate gateway.")
        else:
            print(f"⚠️ Warning: Power Automate returned status code {response.status_code}")
    except Exception as e:
        print(f"🚨 Failed to contact Power Automate cloud endpoint: {e}")

if __name__ == "__main__":
    # Dynamically handle files passed by Jenkins, default to main.tf
    target_file = sys.argv[1] if len(sys.argv) > 1 else "main.tf"
    
    print(f"🔍 Starting Autonomous Scan on target infrastructure file: {target_file}")
    print("📚 Initializing Local Vector Database...")
    vector_db = LightweightVectorDB()
    try:
        with open("rnm_security_policies.txt", "r") as f:
            vector_db.add_document(f.read())
    except FileNotFoundError:
        print("Error: Policy specification file 'rnm_security_policies.txt' not found.")
        sys.exit(1)

    try:
        with open(target_file, "r") as f:
            current_code = f.read()
    except FileNotFoundError:
        print(f"Error: Target file '{target_file}' not found.")
        sys.exit(1)

    # 1. Alignment & Security Checks
    classify_intent(current_code)
    run_guardrails(current_code)
    
    # 2. RAG Retrieval 
    retrieved_policy = vector_db.search("What are the security rules for AWS S3 buckets?")
    
    # 3. Reasoning 
    audit_report = reasoning_agent_audit(current_code, retrieved_policy)
    
    if audit_report.get("is_secure"):
        print("✅ Pipeline Passed: Infrastructure is secure and policy-aligned.")
        sys.exit(0)
        
    print(f"\n🚨 VULNERABILITY DETECTED: {audit_report.get('vulnerability_found')}")
    print(f"📋 POLICY-ALIGNED FIX PLAN: {audit_report.get('fix_plan')}\n")
    
    # 4. Outbound Notification System
    send_power_automate_alert(audit_report, target_file)
    
    print("⏸️ Pipeline Blocked: Awaiting Human-in-the-Loop clearance via MS Teams.")
    # Critical: Returning exit code 1 forces Jenkins Job 1 to FAIL, blocking deployment.
    sys.exit(1)