
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import os
import pyexcel

st.set_page_config(layout="wide")

# --- Custom Theme ---
st.markdown(
    "<style>"
    "header {visibility: hidden;}"
    ".reportview-container .main .block-container {padding-top: 2rem;}"
    "</style>",
    unsafe_allow_html=True
)

import os
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("Structural Movement Graph Analyser")

uploaded_file = st.file_uploader("Upload Excel (.xls or .xlsx)", type=["xls", "xlsx"])

if uploaded_file:
    try:
        # Try reading modern .xlsx first
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except:
            # Handle legacy .xls using pyexcel
            content = uploaded_file.read()
            temp_path = "/tmp/temp.xls"
            with open(temp_path, "wb") as f:
                f.write(content)
            sheet = pyexcel.get_sheet(file_name=temp_path)
            df = pd.DataFrame(sheet.to_array()[1:], columns=sheet.row[0])

        st.success("File loaded!")
        st.dataframe(df.head())

        time_col = st.selectbox("Select time column", df.columns)
        value_col = st.selectbox("Select sensor value column", df.columns)
        temp_col = st.selectbox("Select temperature column (optional)", ['None'] + list(df.columns))

        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col)

        fig, ax = plt.subplots()
        ax.plot(df[time_col], df[value_col], label='Sensor Value')
        if temp_col != 'None':
            ax2 = ax.twinx()
            ax2.plot(df[time_col], df[temp_col], color='orange', alpha=0.5, label='Temperature')
        ax.set_title("Sensor Value Over Time")
        st.pyplot(fig)

        delta = df[value_col].iloc[-1] - df[value_col].iloc[0]
        std_dev = df[value_col].rolling(10, min_periods=1).std().mean()
        trend = df[value_col].rolling(10, min_periods=1).mean()

        progressive_score = abs(delta) > std_dev * 2

        if temp_col != 'None':
            temp_corr = df[value_col].corr(df[temp_col])
            thermal_score = abs(temp_corr) > 0.6
        else:
            thermal_score = False

        fft_vals = np.fft.fft(df[value_col] - df[value_col].mean())
        seasonal_score = np.max(np.abs(fft_vals[1:20])) > std_dev * 5

        st.subheader("Pattern Classification")
        if progressive_score:
            st.write("🟥 **Progressive Movement Detected**")
        if thermal_score:
            st.write("🟨 **Thermal Movement Likely (correlated with temperature)**")
        if seasonal_score:
            st.write("🟦 **Seasonal Pattern Detected**")
        if not any([progressive_score, thermal_score, seasonal_score]):
            st.write("🟩 **No clear pattern detected**")

    except Exception as e:
        st.error(f"Failed to read or process file: {e}")


# --- FUTURE FEATURES ---

# ✅ Machine Learning Pattern Recognition (Scaffold)
# You can later replace this logic with a trained classifier
def classify_pattern_ml(values, temperature=None):
    # Placeholder example logic (can be replaced with a real model)
    results = []
    if abs(values[-1] - values[0]) > values.std() * 2:
        results.append("progressive")
    if temperature is not None and abs(np.corrcoef(values, temperature)[0, 1]) > 0.6:
        results.append("thermal")
    fft_vals = np.fft.fft(values - values.mean())
    if np.max(np.abs(fft_vals[1:20])) > values.std() * 5:
        results.append("seasonal")
    if not results:
        results.append("none")
    return results

# ✅ Export PDF Report (Scaffold)
def export_pdf_report(dataframe, time_col, value_col, temp_col, classification):
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    import tempfile

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Structural Graph Report", ln=True)

    # Add classification summary
    pdf.cell(200, 10, txt=f"Detected Pattern(s): {', '.join(classification)}", ln=True)

    # Save plot to image
    fig, ax = plt.subplots()
    ax.plot(dataframe[time_col], dataframe[value_col], label='Sensor')
    if temp_col != 'None':
        ax2 = ax.twinx()
        ax2.plot(dataframe[time_col], dataframe[temp_col], color='orange', alpha=0.5, label='Temperature')
    ax.set_title("Sensor Graph")
    img_path = tempfile.mktemp(suffix=".png")
    plt.savefig(img_path)
    pdf.image(img_path, x=10, y=40, w=180)

    # Save to file
    pdf_path = tempfile.mktemp(suffix=".pdf")
    pdf.output(pdf_path)
    return pdf_path


# --- UI Enhancements for ML and PDF ---

if uploaded_file:
    classification_result = classify_pattern_ml(df[value_col].astype(float), 
                                                df[temp_col].astype(float) if temp_col != 'None' else None)

    st.subheader("ML-Based Pattern Recognition")
    st.write("📊 Detected Pattern(s):", ", ".join(classification_result))

    if st.button("Export PDF Report"):
        pdf_path = export_pdf_report(df, time_col, value_col, temp_col, classification_result)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(label="Download Report", data=pdf_file, file_name="graph_report.pdf", mime="application/pdf")



    # Optional: Send PDF via email (stub)
    # import smtplib
    # from email.message import EmailMessage
    # msg = EmailMessage()
    # msg['Subject'] = 'Your Structural Report'
    # msg['From'] = 'you@example.com'
    # msg['To'] = 'user@example.com'
    # msg.set_content('Attached is your PDF report.')
    # with open(pdf_path, 'rb') as f:
    #     msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='graph_report.pdf')
    # s = smtplib.SMTP('localhost')
    # s.send_message(msg)
    # s.quit()
