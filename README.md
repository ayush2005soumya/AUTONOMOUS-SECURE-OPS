# Autonomous DevSecOps Gatekeeper

This project is an Agentic AI pipeline designed to intercept, audit, and autonomously remediate infrastructure code (Terraform) before deployment. It runs entirely locally using open-source models to ensure strict data privacy.

## Features
* **Zero-Data Leakage:** Uses local Ollama models (`mistral` and `llama3`).
* **Intent Classification:** Blocks malicious prompts or non-infrastructure inputs.
* **Semantic Policy RAG:** Consults a local Vector Database of corporate security policies.
* **Auto-Remediation:** Autonomously rewrites insecure Terraform code to match compliance.

## System Architecture
```mermaid
graph TD
    %% Define System Boundary
    subgraph Local_Machine [Local Machine Workstation / 16GB RAM sweet-spot]
        
        %% Files
        file_tf[(main.tf)]
        file_policy[(rnm_security_policies.txt)]
        
        %% Core Engine
        script[enterprise_gatekeeper.py Core Loop]
        vdb[(Lightweight In-Memory VectorDB)]
        
        %% Ollama Local Models
        subgraph Ollama_Service [Ollama Local Runtime Service]
            model_embed[nomic-embed-text <br> Embedding Model]
            model_act[mistral <br> Acting / Intent Model]
            model_reason[llama3 <br> Reasoning Model]
        end

        %% Process Flows
        file_policy -->|1. Load & Read| script
        script -->|2. Chunk & Embed| model_embed
        model_embed -->|3. Populate Vectors| vdb
        
        file_tf -->|4. Read Insecure Code| script
        
        script -->|5. Intent Check Prompt| model_act
        model_act -->|6. Return YES/NO| script
        
        script -->|7. Hardcoded Regex Guardrails| script
        
        script -->|8. Semantic Policy Search| vdb
        vdb -->|9. Return Context| script
        
        script -->|10. Strict JSON Audit Prompt| model_reason
        model_reason -->|11. Return Remediate Plan JSON| script
        
        script -->|12. Clean Code Rewrite Prompt| model_act
        model_act -->|13. Return Secure Terraform Code| script
        
        script -->|14. Tool Call: File Overwrite| file_tf
    end

    %% Visual Styling
    style Local_Machine fill:#f9f9f9,stroke:#333,stroke-width:2px;
    style Ollama_Service fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    style vdb fill:#fff9c4,stroke:#fbc02d,stroke-width:1px;
    style file_tf fill:#ffe0b2,stroke:#f57c00,stroke-width:1px;
    style file_policy fill:#ffe0b2,stroke:#f57c00,stroke-width:1px;
    style script fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
```