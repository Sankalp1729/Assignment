import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
from utils.gemini_client import init_gemini, ask_gemini_json
init_gemini()
prompt = """
Extract detailed observations from the text.
Each observation must include:
- area (specific location like "Living Room Wall")
- issue (specific problem like "crack", "leakage")
- description (clear explanation from text)
- severity_hint (minor/major based on wording)

STRICT RULES:
- Use ONLY information from text
- DO NOT use generic words like "detected issue"
- DO NOT return placeholders
- Return ONLY JSON list

Example:
[
  {
    "area": "Living Room Wall",
    "issue": "Crack",
    "description": "Visible structural crack near ceiling corner",
    "severity_hint": "minor"
  }
]

Text:
There is a massive water leak in the basement ceiling causing severe mold growth.
"""
print(ask_gemini_json(prompt))
