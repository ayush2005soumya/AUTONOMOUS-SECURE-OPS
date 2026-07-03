import json
import re
import sys
from openai import OpenAI
from config import ACTING_MODEL, REASONING_MODEL, OPENROUTER_API_KEY

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def reasoning_agent_audit(tf_code, policy_context):
    print("🧠 Cloud Reasoning Agent: Analyzing code against strict RNM company policies...")
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
    
    # Inside reasoning_agent_audit...
    response = client.chat.completions.create(
        model=REASONING_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 🛠️ DEFENSIVE CHECK
    if not hasattr(response, 'choices') or not response.choices or response.choices[0].message.content is None:
        print("🚨 API ERROR: Reasoning agent failed to return a response.")
        sys.exit(1)
        
    raw_content = response.choices[0].message.content.strip()
    
    try:
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        else:
            return json.loads(raw_content)
            
    except json.JSONDecodeError:
        print(f"🚨 FAILED TO PARSE RESPONSE AS JSON. Raw response was:\n{raw_content}")
        sys.exit(1)

def acting_agent_remediate(tf_code, fix_plan):
    print("🦾 Cloud Acting Agent: Writing secure code based on the plan...")
    prompt = f"""
    You are an Infrastructure Engineer. Apply this fix plan to the code.
    Fix Plan: {fix_plan}
    
    Return ONLY the raw, completely rewritten Terraform code. No markdown formatting.
    Code:
    {tf_code}
    """
    
    # Inside acting_agent_remediate...
    response = client.chat.completions.create(
        model=ACTING_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 🛠️ DEFENSIVE CHECK
    if not hasattr(response, 'choices') or not response.choices or response.choices[0].message.content is None:
        print("🚨 API ERROR: Acting agent failed to return a response.")
        sys.exit(1)
        
    return response.choices[0].message.content.replace('```hcl', '').replace('```terraform', '').replace('```', '').strip()