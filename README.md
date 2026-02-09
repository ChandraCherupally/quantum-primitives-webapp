# Quantum Primitives Interactive Lab 🚀

An interactive web application demonstrating **Qiskit Sampler & Estimator primitives**
using **Streamlit**, **FastAPI**, and **real IBM Quantum hardware**.

---

## Features
- Quantum Random Number Generator
  - Simulator (StatevectorSampler)
  - Real Quantum Hardware (SamplerV2)
- Quantum Height–Weight Correlation Analysis
  - Classical Pearson correlation
  - Quantum ⟨ZZ⟩ observable
  - Entangled vs product states
- Secure hardware access (PIN-protected)
- Clean separation of UI, API, and quantum logic

---

## Tech Stack
- Python
- Qiskit & Qiskit Runtime
- IBM Quantum
- Streamlit
- FastAPI
- NumPy, SciPy, Seaborn

---

## Architecture
Streamlit UI → FastAPI → IBM Quantum Runtime


---

## How to Run Locally

```bash
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
streamlit run app/streamlit_app.py
