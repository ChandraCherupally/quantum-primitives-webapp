import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st
import requests
from quantum.rng import rng_statevector
from quantum.correlation import quantum_zz, classical_corr, DATASETS as datasets
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

st.set_page_config("Quantum Primitives Lab", layout="wide")

st.title("Quantum Primitives Interactive Lab")

project = st.sidebar.selectbox(
    "Select Project",
    ["Quantum Random Number Generator", "Quantum Height&Weight Correlation Estimator"],
)

if project == "Quantum Random Number Generator":
    bits = st.slider("Number of qubits", 2, 15, 5)
    mode = st.radio("Execution Mode", ["Simulator", "Real Quantum Hardware"])

    if st.button("Generate"):
        if mode == "Simulator":
            b, v, _ = rng_statevector(bits)
            st.success(f"Bitstring: {b}")
            st.metric("Random Value", v)
        else:
            res = requests.post(
                "http://localhost:8000/rng/hardware",
                json={"num_bits": bits},
            ).json()
            st.success(f"Bitstring: {res['bitstring']}")
            st.metric("Random Value", res["value"])



if project == "Quantum Height&Weight Correlation Estimator":    

    # -------------------------------
    # Dataset selector
    # -------------------------------
    selection = st.selectbox(
        "Select Correlation Type",
        list(datasets.keys())
    )
    health_mode = selection == "X-or health data"

    data = datasets[selection]

    st.subheader(f"{selection} Dataset")

    
    # -------------------------------
    # Classical correlation
    # -------------------------------
    r, p = classical_corr(data)

    # -------------------------------
    # Quantum correlations
    # -------------------------------
    q_ent = quantum_zz(data, entangle=True, health_mode=health_mode)
    q_no = quantum_zz(data, entangle=False, health_mode=health_mode)

    # -------------------------------
    # Results display
    # -------------------------------
    st.markdown("### Classical Result")
    st.metric("Pearson Correlation (r)", round(r, 3))

    st.markdown("### Quantum Results")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("⟨ZZ⟩ (Product State)", round(q_no.mean(), 3))
    with col2:
        st.metric("⟨ZZ⟩ (Entangled)", round(q_ent.mean(), 3))

    # -------------------------------
    # Compact scatter plot
    # -------------------------------
    st.markdown("### Height vs Weight Scatter Plot")

    df = pd.DataFrame(
        data,
        columns=["Height (cm)", "Weight (kg)"]
    )

    sns.set_theme(style="whitegrid", context="notebook")

    palette = {
        "Positive Correlation": "#1f77b4",
        "Negative Correlation": "#d62728",
        "Uncorrelated": "#7f7f7f",
        "X-or health data": "#2ca02c",
    }

    # 🔹 Smaller figure + lower DPI
    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=90)

    sns.scatterplot(
        data=df,
        x="Height (cm)",
        y="Weight (kg)",
        color=palette.get(selection, "#1f77b4"),
        s=40,              # smaller markers
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
        ax=ax
    )

    ax.set_title(f"{selection}", fontsize=11)
    ax.set_xlabel("Height (cm)", fontsize=9)
    ax.set_ylabel("Weight (kg)", fontsize=9)

    # Reduce padding
    ax.tick_params(axis='both', labelsize=8)
    fig.tight_layout(pad=0.8)

    # 🔹 Prevent Streamlit from stretching it
    st.pyplot(fig, use_container_width=False)

