# remediate.py
import sys
import subprocess
from agents import acting_agent_remediate

# Inside remediate.py

def run_git_operations(target_file, commit_branch, merge_branch):
    print(f"🐙 Initializing Git workflow on branch: {commit_branch}...")
    
    try:
        # 1. Safely handle branch checkout or creation
        try:
            # Try to switch to the branch if it already exists
            subprocess.run(["git", "checkout", commit_branch], check=True, capture_output=True)
            print(f"   Switched to existing branch: {commit_branch}")
        except subprocess.CalledProcessError:
            # If it fails, the branch doesn't exist, so we create it
            subprocess.run(["git", "checkout", "-b", commit_branch], check=True)
            print(f"   Created and switched to new branch: {commit_branch}")
        
        # 2. Stage the secure code rewritten by the AI
        subprocess.run(["git", "add", target_file], check=True)
        
        # 3. Commit with an enterprise security tag
        subprocess.run(["git", "commit", "-m", f"security: automated patch applied to {target_file} via RNM Gatekeeper Agent"], check=True)
        
        # 4. Push the branch upstream (using --set-upstream to ensure remote tracking)
        subprocess.run(["git", "push", "--set-upstream", "origin", commit_branch], check=True)
        
        print(f"🚀 Opening GitHub Pull Request against base branch: {merge_branch}...")
        pr_title = f"🚨 DevSecOps Patch: Automated Remediation for {target_file}"
        pr_body = "This Pull Request was autonomously generated and authorized via Human-in-the-Loop IDE approval."
        
        # 5. Use GitHub CLI to target the specific merge branch
        subprocess.run([
            "gh", "pr", "create", 
            "--title", pr_title, 
            "--body", pr_body,
            "--base", merge_branch,   
            "--head", commit_branch   
        ], check=True)
        print("✅ Pull Request successfully created and staged for peer review.")
        
    except subprocess.CalledProcessError as e:
        print(f"🚨 Git/CLI Operational Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Now requires 4 arguments: script.py, file, fix_plan, commit_branch, merge_branch
    if len(sys.argv) < 5:
        print("Error: Missing required arguments. Usage: python remediate.py [filename] '[fix_plan]' [commit_branch] [merge_branch]")
        sys.exit(1)
        
    target_file = sys.argv[1]
    fix_plan = sys.argv[2]
    commit_branch = sys.argv[3]
    merge_branch = sys.argv[4]
    
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
    
    # Run the downstream automation chain using the user-defined branches
    run_git_operations(target_file, commit_branch, merge_branch)