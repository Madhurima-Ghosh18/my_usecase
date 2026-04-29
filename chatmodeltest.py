from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()  # ← load .env file

HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
print(f"API Key found: {HF_API_KEY[:10]}...")  # ← verify key is loading

models = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "google/gemma-2-2b-it",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
]

for model in models:
    try:
        client = InferenceClient(model=model, token=HF_API_KEY)
        response = client.chat_completion(
            messages=[{"role": "user", "content": "say hi"}],
            max_tokens=10
        )
        print(f"✅ WORKS: {model}")
    except Exception as e:
        print(f"❌ FAILED: {model} - {str(e)[:100]}")