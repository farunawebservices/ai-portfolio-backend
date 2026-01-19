from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

models = client.models.list()

for m in models:
    print("MODEL NAME:", m.name)
    print("MODEL OBJECT:", m)
    print("-" * 60)
