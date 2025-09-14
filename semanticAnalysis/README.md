# Semantic Analysis Environment

This folder provides dependencies for running local & hosted language model workflows combining Hugging Face libraries and an Ollama runtime.

## Contents
- `requirements.txt`: Python dependencies for transformer inference, dataset handling, sentence embeddings, and optional local model orchestration.

## Install (Python v3.11+ recommended)
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r semanticAnalysis/requirements.txt
```

## Notes on Dependencies
- `torch`: CPU build by default. For GPU (CUDA 12.x) you can instead run:
  ```bash
  pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
  ```
- `bitsandbytes`: Skipped on Windows (wheel availability limited). Remove the environment marker in `requirements.txt` if you add WSL or Linux.
- `ollama`: Python client to interact with a locally running Ollama daemon (install native Ollama separately: https://ollama.com/download).

## Example: Download & Run a Sentence Embedding Model
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb = model.encode(["Test sentence"], convert_to_tensor=False)
print(emb[0][:8])
```

## Example: Hugging Face Transformer (Text Generation)
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = "gpt2"
tok = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
inputs = tok("Hello world", return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=20)
print(tok.decode(out[0]))
```

## Example: Calling Ollama (Python)
```python
from ollama import Client
client = Client()
for chunk in client.generate(model="llama3", prompt="Say hi"):
    print(chunk.get("response"), end="", flush=True)
```
Ensure the Ollama service is running locally before calling.

## Environment Variables
Use a project-level `.env` if you need Hugging Face tokens:
```
HUGGINGFACE_HUB_TOKEN=hf_...
```
`python-dotenv` will help load these if you create scripts under this folder.

## Optional Extras
Add these manually if needed:
```
peft
trl
flash-attn  # (Linux, specific CUDA required)
```

## Next Steps
- Add a script `embed.py` to batch embed your domain documents.
- Add a FastAPI microservice for semantic search if required.

