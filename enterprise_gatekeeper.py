import os
import sys
import json
import math
import re  # 🛠️ Added for robust JSON extraction
import ollama

# --- 1. CONFIGURATION & MODEL ROUTING ---
# Your exact localized open-source model setup
EMBEDDING_MODEL = "nomic-embed-text"
ACTING_MODEL = "mistral"    
REASONING_MODEL = "llama3" 

# --- 2. VECTOR DATABASE & RAG (In-Memory) ---
class LightweightVectorDB:
    def __init__(self):
        self.documents = []

    def add_document(self, text):
        """Generates an embedding for the text and stores it using Ollama."""
        response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
        embedding = response["embedding"]
        self.documents.append({"text": text, "embedding": embedding})

    def cosine_similarity(self, v1, v2):
        """Core algorithmic math to find vector distance."""
        dot_product = sum(x * y for x, y in zip(v1, v2))
        mag1 = math.sqrt(sum(x * x for x in v1))
        mag2 = math.sqrt(sum(x * x for x in v2))
        return dot_product / (mag1 * mag2) if mag1 and mag2 else 0.0

    def search(self, query, top_k=1):
        """Embeds the query and returns the most relevant company policy."""
        if not self.documents: return "No policies loaded."
        
        response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=query)
        query_embedding = response["embedding"]
        
        scored_docs = []
        for doc in self.documents:
            score = self.cosine_similarity(query_embedding, doc["embedding"])
            scored_docs.append((score, doc["text"]))
        
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return scored_docs[0][1]

# --- 3. GUARDRAILS & INTENT CLASSIFICATION ---
def run_guardrails(tf_code):
    """Hardcoded structural checks to prevent catastrophic actions."""
    print("🛡️ Running pre-flight guardrails...")
    forbidden_commands = ["destroy", "null_resource", "local-exec rm -rf"]
    for word in forbidden_commands:
        if word in tf_code:
            print(f"🚨 GUARDRAIL BLOCKED: Code contains forbidden action '{word}'.")
            sys.exit(1)
    print("   Guardrails passed.")

def classify_intent(tf_code):
    """Uses Mistral to ensure the request is actually DevOps related."""
    print("🕵️ Fast Agent: Classifying Intent...")
    prompt = f"Does the following text look like valid infrastructure code (Terraform)? Answer only 'YES' or 'NO'.\n{tf_code}"
    
    response = ollama.chat(model=ACTING_MODEL, messages=[
        {"role": "user", "content": prompt}
    ])
    
    if "YES" not in response['message']['content'].upper():
        print("🚨 INTENT REJECTED: Input does not appear to be valid Terraform code.")
        sys.exit(1)
    print("   Intent valid. Proceeding to audit.")

# --- 4. REASONING AGENT (The Brain with RAG) ---
def reasoning_agent_audit(tf_code, policy_context):
    print("🧠 Local Reasoning Agent: Analyzing code against strict RNM company policies...")
    prompt = f"""
    You are a Lead DevSecOps Auditor. 
    Analyze this code against the provided RNM Company Policy.
    
    COMPANY POLICY CONTEXT: 
    {policy_context}
    
    Return a JSON object matching this exact schema:
    {{
        "is_secure": false,
        "vulnerability_found": "[Issue description]",
        "fix_plan": "[Exact instructions for the Acting Agent based on the policy]"
    }}
    
    Code to analyze:
    {tf_code}
    """
    
    # Force Llama3 to structurally output strict JSON format natively
    response = ollama.chat(
        model=REASONING_MODEL, 
        messages=[{"role": "user", "content": prompt}],
        format="json" 
    )
    
    raw_content = response['message']['content'].strip()
    
    # Regular expression fallback to extract exactly the JSON block if text slips in
    try:
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        else:
            return json.loads(raw_content)
            
    except json.JSONDecodeError:
        print(f"🚨 FAILED TO PARSE Llama3 RESPONSE AS JSON. Raw response was:\n{raw_content}")
        sys.exit(1)

# --- 5. ACTING AGENT (The Hands) ---
def acting_agent_remediate(tf_code, fix_plan):
    print("🦾 Local Acting Agent: Writing secure code based on the plan...")
    prompt = f"""
    You are an Infrastructure Engineer. Apply this fix plan to the code.
    Fix Plan: {fix_plan}
    
    Return ONLY the raw, completely rewritten Terraform code. No markdown formatting.
    Code:
    {tf_code}
    """
    
    response = ollama.chat(model=ACTING_MODEL, messages=[
        {"role": "user", "content": prompt}
    ])
    
    return response['message']['content'].replace('```hcl', '').replace('```terraform', '').replace('```', '').strip()

# --- 6. MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    target_file = "main.tf"
    
    print("📚 Initializing Local Vector Database...")
    vector_db = LightweightVectorDB()
    try:
        with open("rnm_security_policies.txt", "r") as f:
            vector_db.add_document(f.read())
    except FileNotFoundError:
        print("Error: Policy file not found.")
        sys.exit(1)

    with open(target_file, "r") as f:
        current_code = f.read()

    # 1. Alignment & Security Checks
    classify_intent(current_code)
    run_guardrails(current_code)
    
    # 2. RAG Retrieval 
    retrieved_policy = vector_db.search("What are the security rules for AWS S3 buckets?")
    
    # 3. Reasoning (Llama3)
    audit_report = reasoning_agent_audit(current_code, retrieved_policy)
    
    if audit_report.get("is_secure"):
        print("✅ Pipeline Passed: Infrastructure is secure.")
        sys.exit(0)
        
    print(f"\n🚨 VULNERABILITY DETECTED: {audit_report.get('vulnerability_found')}")
    print(f"📋 POLICY-ALIGNED FIX PLAN: {audit_report.get('fix_plan')}\n")
    
    # 4. Acting (Mistral)
    secure_code = acting_agent_remediate(current_code, audit_report.get("fix_plan"))
    
    # 5. Tool Calling (Save File)
    with open(target_file, 'w') as file:
        file.write(secure_code)
    
    print("✅ Auto-Remediation Complete: File rewritten entirely by local open-source AI.")
