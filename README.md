# Structural Graph Analyser

This Streamlit app lets you:
- Upload `.xls` or `.xlsx` structural sensor data
- Detect movement patterns (progressive, thermal, seasonal)
- Run ML-based pattern recognition (scaffolded)
- Export annotated PDF reports

## Run locally

```bash
pip install -r requirements.txt
streamlit run graph_analyser.py
```

## Deploy to Streamlit Cloud

1. Upload this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Create a new app pointing to `graph_analyser.py`
