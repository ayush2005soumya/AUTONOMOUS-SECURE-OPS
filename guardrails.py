import sys
import re
from openai import OpenAI
from config import FAST_MODEL, OPENROUTER_API_KEY

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env")
    sys.exit(1)

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def run_guardrails(tf_code):
    print("🛡️ Running pre-flight guardrails...")
    
    # 1. Size Limiter (Prevents Denial of Service / Token Exhaustion)
    if len(tf_code) > 20000:
        print("🚨 GUARDRAIL BLOCKED: Payload exceeds maximum allowed size (20,000 characters).")
        sys.exit(1)

    # 2. Expanded IaC Blocklist (Catches rogue compute and destructive actions)
    forbidden_commands = [
        "destroy", 
        "null_resource", 
        "local-exec", 
        "remote-exec",
        "aws_iam_access_key", # Prevents creating raw IAM keys in code
        "aws_iam_user_login_profile" # Prevents creating backdoor console users
    ]
    
    # FIX 1: Use regex word boundaries (\b) to prevent substring false positives
    for word in forbidden_commands:
        if re.search(rf'\b{word}\b', tf_code):
            print(f"🚨 GUARDRAIL BLOCKED: Code contains forbidden action or resource '{word}'.")
            sys.exit(1)

    # 3. Regex Secret Scanning (Catches hardcoded credentials)
    secret_patterns = {
        "AWS Access Key": r"(?i)AKIA[0-9A-Z]{16}",
        "Private RSA/SSH Key": r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----",
        "Generic Password Field": r'(?i)password\s*=\s*["\'][^"\']+["\']'
    }
    for label, pattern in secret_patterns.items():
        if re.search(pattern, tf_code):
            print(f"🚨 GUARDRAIL BLOCKED: Hardcoded secret detected ({label}).")
            sys.exit(1)

    print("   Guardrails passed.")


def classify_intent(tf_code):
    print("🕵️ Fast Agent: Classifying Intent...")
    
    # 🛠️ 1. Enforced System Prompting (Sets a strict persona)
    messages = [
         {
        "role": "system",
        "content": """
You are a binary classifier.

Output EXACTLY one word:
YES
or
NO

Do not explain.
Do not reason.
Do not output anything else.
"""
    },
        {
            "role": "user",
            "content": f"Text to classify:\n\n{tf_code}"
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model=FAST_MODEL,
            messages=messages,
            temperature=0.0,  # 🛠️ 2. Zero Temperature (Eliminates creative hallucinations)
            max_tokens=50      # 🛠️ 3. Token Limiter (Forces a short answer, prevents long explanations)
        )

        # Defensive Checks
        if not hasattr(response, 'choices') or not response.choices or response.choices[0].message.content is None:
            print("🚨 API ERROR: OpenRouter failed to return valid model choices.")
            sys.exit(1)
            
        # 🛠️ 4. Clean Parsing (Strips invisible whitespace or punctuation)
        raw_result = response.choices[0].message.content.strip().upper()
        clean_result = ''.join(char for char in raw_result if char.isalnum())
            
        # FIX 2: Use startswith to handle slight LLM verbosity (e.g. "YESITIS") safely
        if not clean_result.startswith("YES"):
            print(f"🚨 INTENT REJECTED: Input is not recognized as Terraform code. (Model replied: {raw_result})")
            sys.exit(1)
            
        print("   Intent valid. Proceeding to audit.")

    except Exception as e:
        print(f"🚨 FATAL: Intent classification failed. Error: {e}")
        sys.exit(1)