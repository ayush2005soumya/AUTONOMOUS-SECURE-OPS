# remediate.py
import sys
import subprocess
from agents import acting_agent_remediate

def run_git_operations(target_file):
    print("🐙 Initializing Git workflow for automated remediation...")
    branch_name = f"security-remediation-{target_file.replace('.', '-')}"
    
    try:
        # Create a new isolated branch for the fix
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        # Stage the secure code rewritten by the AI
        subprocess.run(["git", "add", target_file], check=True)
        # Commit with an enterprise security tag
        subprocess.run(["git", "commit", "-m", f"security: automated patch applied to {target_file} via RNM Gatekeeper Agent"], check=True)
        # Push branch upstream
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        
        print("🚀 Opening GitHub Pull Request using GitHub CLI...")
        pr_title = f"🚨 DevSecOps Patch: Automated Remediation for {target_file}"
        pr_body = "This Pull Request was autonomously generated and authorized via Microsoft Teams approval routing."
        subprocess.run(["gh", "pr", "create", "--title", pr_title, "--body", pr_body], check=True)
        print("✅ Pull Request successfully created and staged for peer review.")
        
    except subprocess.CalledProcessError as e:
        print(f"🚨 Git/CLI Operational Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Missing required arguments. Usage: python remediate.py [filename] '[fix_plan]'")
        sys.exit(1)
        
    target_file = sys.argv[1]
    fix_plan = sys.argv[2]
    
    print(f"🦾 Initializing Acting Agent patch sequence for: {target_file}")
    
    try:
        with open(target_file, "r") as f:
            current_code = f.read()
    except FileNotFoundError:
        print(f"Error: Target file '{target_file}' could not be located.")
        sys.exit(1)
        
    # Trigger Acting Agent to perform complex structural formatting rewrite
    secure_code = acting_agent_remediate(current_code, fix_plan)
    
    # Overwrite the local repository file with secure infrastructure code
    with open(target_file, 'w') as file:
        file.write(secure_code)
    print("💾 Local workspace successfully synchronized with policy-compliant code configuration.")
    
    # Run the downstream automation chain to push code and open a PR
    run_git_operations(target_file)