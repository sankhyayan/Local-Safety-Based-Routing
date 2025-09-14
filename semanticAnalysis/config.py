import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "safety-route-demo")

print(f"PINECONE_INDEX_NAME={PINECONE_INDEX_NAME}")
print(f"PINECONE_ENV={PINECONE_ENV}")
print(f"PINECONE_API_KEY= {PINECONE_API_KEY}")
