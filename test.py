import os, requests

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL = "meta-llama/Llama-2-7b-chat-hf"  # safe public model

url = f"https://router.huggingface.co/api/{MODEL}"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
data = {"inputs": "Hello world"}

resp = requests.post(url, json=data, headers=headers)
print(resp.status_code)
print(resp.text)