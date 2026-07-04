# vector_db.py
import math
import sys
import re
from openai import OpenAI
from config import EMBEDDING_MODEL, OPENROUTER_API_KEY

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env")
    sys.exit(1)

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

class LightweightVectorDB:
    def __init__(self):
        self.documents = []

    def add_document(self, text):
        """Structurally splits a policy document into sections and embeds them individually."""
        # FIX 1: Parse document by sections (e.g., "Section 1:", "Section 2:") to create granular chunks
        sections = re.split(r'(?=Section \d+:)', text)
        
        # Clean chunks and filter out empty strings
        chunks = [s.strip() for s in sections if s.strip()]
        
        print(f"📦 Vector DB: Parsing policy into {len(chunks)} high-fidelity semantic chunks...")

        for chunk in chunks:
            try:
                response = client.embeddings.create(
                    input=chunk,
                    model=EMBEDDING_MODEL,
                    encoding_format="float"
                )
                
                # FIX 2: Defensive check on embedding response
                if not response or not hasattr(response, 'data') or not response.data:
                    print(f"🚨 EMBEDDING ERROR: Failed to generate vector for chunk: {chunk[:30]}...")
                    continue
                    
                embedding = response.data[0].embedding
                self.documents.append({"text": chunk, "embedding": embedding})
                
            except Exception as e:
                print(f"🚨 API Failure during embedding: {e}")
                sys.exit(1)

    def cosine_similarity(self, v1, v2):
        """Core algorithmic math to find vector distance."""
        dot_product = sum(x * y for x, y in zip(v1, v2))
        mag1 = math.sqrt(sum(x * x for x in v1))
        mag2 = math.sqrt(sum(x * x for x in v2))
        return dot_product / (mag1 * mag2) if mag1 and mag2 else 0.0

    def search(self, query, top_k=1):
        """Embeds the query and returns the single most semantically relevant corporate section."""
        if not self.documents: 
            return "No policies loaded."
        
        try:
            response = client.embeddings.create(
                input=query,
                model=EMBEDDING_MODEL,
                encoding_format="float"
            )
            
            if not response or not hasattr(response, 'data') or not response.data:
                return "Error: Query embedding generation failed."
                
            query_embedding = response.data[0].embedding
            
            scored_docs = []
            for doc in self.documents:
                score = self.cosine_similarity(query_embedding, doc["embedding"])
                scored_docs.append((score, doc["text"]))
            
            scored_docs.sort(reverse=True, key=lambda x: x[0])
            
            print(f"🎯 Vector Match: Selected policy context with confidence score: {scored_docs[0][0]:.4f}")
            return scored_docs[0][1]
            
        except Exception as e:
            print(f"🚨 Vector DB Search Failure: {e}")
            return "Error retrieving policies."