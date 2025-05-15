
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Structural Movement Graph Analyser")

uploaded_file = st.file_uploader("Upload Excel (.xls or .xlsx)", type=["xls", "xlsx"])

if uploaded_file:
    try:
        # Read Excel with fallback
        if uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        else:
            df = pd.read_excel(uploaded_file)

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

        ### PATTERN ANALYSIS ###
        delta = df[value_col].iloc[-1] - df[value_col].iloc[0]
        std_dev = df[value_col].rolling(10, min_periods=1).std().mean()
        trend = df[value_col].rolling(10, min_periods=1).mean()

        progressive_score = abs(delta) > std_dev * 2

        if temp_col != 'None':
            temp_corr = df[value_col].corr(df[temp_col])
            thermal_score = abs(temp_corr) > 0.6
        else:
            thermal_score = False

        # Seasonal check (basic FFT detection of periodicity)
        fft_vals = np.fft.fft(df[value_col] - df[value_col].mean())
        fft_freqs = np.fft.fftfreq(len(fft_vals))
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
        st.error(f"Failed to read file: {e}")
