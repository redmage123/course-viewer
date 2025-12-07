#!/usr/bin/env python3
"""Test OpenAI API connection with different models."""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai package...")
    os.system(f"{sys.executable} -m pip install openai -q")
    from openai import OpenAI

# Get API key from environment or prompt
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    api_key = input("Enter your OpenAI API key: ").strip()

client = OpenAI(api_key=api_key)

# Models to test (in order of preference)
models_to_test = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4.1",
    "gpt-4",
    "gpt-3.5-turbo",
]

print("\nTesting OpenAI API connection...\n")

for model in models_to_test:
    try:
        print(f"Testing {model}...", end=" ")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            max_tokens=10
        )
        result = response.choices[0].message.content
        print(f"✓ SUCCESS - Response: {result}")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "not found" in error_msg.lower():
            print(f"✗ Model not available")
        elif "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            print(f"✗ Invalid API key")
            break
        else:
            print(f"✗ Error: {error_msg[:80]}")

print("\nDone!")
