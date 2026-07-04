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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(audit_report):
    sender_email = os.environ.get("EMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not sender_email or not app_password:
        print("⚠️ Email credentials missing from environment. Skipping alert.")
        return
        
    print("📡 Sending Human-in-the-Loop Alert via Email...")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = sender_email  # Sending the alert directly to yourself
    msg['Subject'] = "🚨 AI DevSecOps Alert: Pipeline Blocked"
    
    # Creates a highly professional HTML template for the email
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2 style="color: #d9534f;">⚠️ Pipeline Blocked by Autonomous AI Agent</h2>
            <p>The DevSecOps agent has detected a strict policy violation in the latest commit.</p>
            <div style="background-color: #f4f4f4; padding: 15px; border-left: 5px solid #d9534f; margin-bottom: 20px;">
                <pre style="white-space: pre-wrap; font-family: monospace;">{audit_report}</pre>
            </div>
            <p>Please review your Jenkins dashboard to Authorize or Reject this deployment.</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print("📧 Email Alert Sent Successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

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
    # Swap the old Power Automate call for the new Email call
    # 4. Outbound Notification System
    send_email_alert(audit_report)
    
    # NEW: Save the fix plan to disk for remediate.py to use later
    with open("fix_plan_cache.txt", "w") as plan_file:
        plan_file.write(audit_report.get('fix_plan'))
    
    print("⏸️ Pipeline Blocked: Awaiting Human-in-the-Loop clearance.")
    sys.exit(1)