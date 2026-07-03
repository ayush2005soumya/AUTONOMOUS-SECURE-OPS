# vector_db.py
import math
import sys
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
        """Generates an embedding using Nvidia's model via OpenRouter."""
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            encoding_format="float"  # 🛠️ FORCES COMPATIBILITY WITH OPENROUTER
        )
        # Extract the vector array from the OpenAI-compatible response
        embedding = response.data[0].embedding
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
        
        response = client.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL,
            encoding_format="float"  # 🛠️ FORCES COMPATIBILITY WITH OPENROUTER
        )
        query_embedding = response.data[0].embedding
        
        scored_docs = []
        for doc in self.documents:
            score = self.cosine_similarity(query_embedding, doc["embedding"])
            scored_docs.append((score, doc["text"]))
        
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return scored_docs[0][1]