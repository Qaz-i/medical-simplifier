# 🏥 MedSimplify — Medical Report Simplifier

An AI-powered tool that transforms confusing medical reports into plain English.

## What it does
- Upload any medical report PDF (blood test, MRI, discharge summary)
- Extracts text using PyMuPDF + EasyOCR (works on scanned PDFs too)
- Claude AI explains every parameter in simple language
- Abnormal values highlighted in red
- Recommends which specialist to consult
- Download your simplified summary

## Tech Stack
- Python + Streamlit (UI)
- PyMuPDF + EasyOCR (PDF extraction + OCR)
- Anthropic Claude API (AI explanation)
- python-dotenv (secure API key management)

## Setup
1. Clone the repo
2. Create virtual environment:
   python3 -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Add your API key to .env:
   ANTHROPIC_API_KEY=your-key-here
5. Run:
   streamlit run app.py

## Disclaimer
This tool is for educational purposes only.
It does not provide medical advice or diagnosis.
Always consult a qualified healthcare professional.
