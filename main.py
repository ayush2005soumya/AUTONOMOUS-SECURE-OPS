import sys
import os
import requests  
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
    
    # FIX 2: Extract specific fields from the dictionary for clean HTML formatting
    vuln_found = audit_report.get('vulnerability_found', 'Unknown vulnerability detected.')
    fix_plan = audit_report.get('fix_plan', 'No remediation plan provided.')
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2 style="color: #d9534f;">⚠️ Pipeline Blocked by Autonomous AI Agent</h2>
            <p>The DevSecOps agent has detected a strict policy violation in the latest commit.</p>
            
            <h3 style="color: #d9534f; margin-bottom: 5px;">Vulnerability Found:</h3>
            <div style="background-color: #fdf0f0; padding: 15px; border-left: 5px solid #d9534f; margin-bottom: 20px;">
                <p style="margin: 0; font-family: monospace;">{vuln_found}</p>
            </div>
            
            <h3 style="color: #5bc0de; margin-bottom: 5px;">AI Remediation Plan:</h3>
            <div style="background-color: #f4f8fa; padding: 15px; border-left: 5px solid #5bc0de; margin-bottom: 20px;">
                <p style="margin: 0; font-family: monospace;">{fix_plan}</p>
            </div>
            
            <p>Please review your Jenkins dashboard to <strong>Authorize</strong> or <strong>Reject</strong> this deployment.</p>
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
    # FIX 1: Make the vector search dynamic by embedding the first 1000 characters of the target code
    search_context = f"Find security rules related to this infrastructure code: {current_code[:1000]}"
    retrieved_policy = vector_db.search(search_context)
    
    # 3. Reasoning 
    audit_report = reasoning_agent_audit(current_code, retrieved_policy)
    
    if audit_report.get("is_secure"):
        print("✅ Pipeline Passed: Infrastructure is secure and policy-aligned.")
        sys.exit(0)
        
    print(f"\n🚨 VULNERABILITY DETECTED: {audit_report.get('vulnerability_found')}")
    print(f"📋 POLICY-ALIGNED FIX PLAN: {audit_report.get('fix_plan')}\n")
    
    # 4. Outbound Notification System
    send_email_alert(audit_report)
    
    # Save the fix plan to disk for remediate.py to use later
    with open("fix_plan_cache.txt", "w") as plan_file:
        plan_file.write(audit_report.get('fix_plan'))
    
    print("⏸️ Pipeline Blocked: Awaiting Human-in-the-Loop clearance.")
    sys.exit(1)