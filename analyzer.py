from groq import Groq
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_report(report_text: str) -> dict:

    user_prompt = f"""
You are a compassionate medical report explainer.
Your job is to help non-medical patients understand their reports.
Always be clear, simple, and non-alarming. Use everyday language.
Never diagnose. Always recommend consulting a doctor for anything serious.

Here is a medical report text extracted from a PDF:

---
{report_text[:2000]}
---

Analyze this and return a JSON object with this exact structure:
{{
  "patient_name": "Full name of the patient extracted from the report. If not found, return Unknown Patient",
  "report_type": "Blood Test / MRI / Discharge Summary / etc.",
  "summary": "2-3 sentence plain English overview of what this report shows",
  "findings": [
    {{
      "parameter": "Parameter name (e.g. Haemoglobin)",
      "value": "Value from report (e.g. 9.5 g/dL)",
      "normal_range": "Normal range (e.g. 12-17 g/dL)",
      "status": "normal | low | high | abnormal",
      "plain_explanation": "What this means in simple words",
      "impact": "How this might affect the patient day-to-day"
    }}
  ],
  "abnormal_count": <number of abnormal findings>,
  "recommended_specialists": ["e.g. General Physician", "Cardiologist"],
  "next_steps": "What the patient should do next in simple language",
  "disclaimer": "This is an educational explanation only. Please consult a qualified doctor for medical advice."
}}

Return ONLY the JSON object, nothing else. No markdown, no backticks.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.3,
        max_tokens=4000
    )

    raw = response.choices[0].message.content
    raw = re.sub(r'```json|```', '', raw).strip()
    return json.loads(raw)
