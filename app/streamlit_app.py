import sys
import os
from pathlib import Path

# -------------------------------------------------
# Path setup (kept minimal and safe)
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# -------------------------------------------------
# Imports
# -------------------------------------------------
import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from quantum.rng import rng_statevector, rng_hardware
from quantum.correlation import quantum_zz, classical_corr, DATASETS as datasets
from dotenv import load_dotenv

load_dotenv()  # 👈 THIS WAS MISSING

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Quantum Primitives Lab",
    layout="wide"
)

st.title("Quantum Primitives Interactive Lab")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
project = st.sidebar.selectbox(
    "Select Project",
    [
        "Quantum Random Number Generator",
        "Quantum Height & Weight Correlation Estimator",
    ],
)

# =================================================
# PROJECT 1: Quantum Random Number Generator
# =================================================
if project == "Quantum Random Number Generator":

    bits = st.slider(
        "Number of qubits",
        min_value=2,
        max_value=20,
        value=5,
    )

    mode = st.radio(
        "Execution Mode",
        ["Simulator", "Real Quantum Hardware"],
    )

    if st.button("Generate"):

        # -----------------------------
        # Simulator
        # -----------------------------
        if mode == "Simulator":
            b, v, _ = rng_statevector(bits)
            st.success(f"Bitstring: {b}")
            st.metric("Random Value", v)

        # -----------------------------
        # Real Quantum Hardware
        # -----------------------------
        else:
            if not os.getenv("IBM_QUANTUM_API_KEY"):
                st.error(
                    "IBM Quantum API key is not configured.\n\n"
                    "Add it in Streamlit → App → Settings → Secrets."
                )
                st.stop()

            st.info(
                "Submitting job to real IBM Quantum hardware.\n"
                "Queue times may vary (30s–2min)."
            )

            with st.spinner("Running on quantum hardware..."):
                b, v = rng_hardware(bits)

            st.success(f"Bitstring: {b}")
            st.metric("Random Value", v)

# =================================================
# PROJECT 2: Quantum Height & Weight Correlation
# =================================================
if project == "Quantum Height & Weight Correlation Estimator":

    # -----------------------------
    # Dataset selector
    # -----------------------------
    selection = st.selectbox(
        "Select Correlation Type",
        list(datasets.keys())
    )

    health_mode = selection == "X-or health data"
    data = datasets[selection]

    st.subheader(f"{selection} Dataset")

    # -----------------------------
    # Classical correlation
    # -----------------------------
    r, p = classical_corr(data)

    # -----------------------------
    # Quantum correlations
    # -----------------------------
    q_ent = quantum_zz(data, entangle=True, health_mode=health_mode)
    q_no = quantum_zz(data, entangle=False, health_mode=health_mode)

    # -----------------------------
    # Results
    # -----------------------------
    st.markdown("### Classical Result")
    st.metric("Pearson Correlation (r)", round(r, 3))

    st.markdown("### Quantum Results")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("⟨ZZ⟩ (Product State)", round(q_no.mean(), 3))
    with col2:
        st.metric("⟨ZZ⟩ (Entangled)", round(q_ent.mean(), 3))

    # -----------------------------
    # Scatter plot
    # -----------------------------
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

    fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=90)

    sns.scatterplot(
        data=df,
        x="Height (cm)",
        y="Weight (kg)",
        color=palette.get(selection, "#1f77b4"),
        s=40,
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
        ax=ax
    )

    ax.set_title(selection, fontsize=11)
    ax.set_xlabel("Height (cm)", fontsize=9)
    ax.set_ylabel("Weight (kg)", fontsize=9)
    ax.tick_params(axis="both", labelsize=8)

    fig.tight_layout(pad=0.8)
    st.pyplot(fig, use_container_width=False)
