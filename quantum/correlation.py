import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from scipy.stats import pearsonr


def angle_encode(x, xmin, xmax, scale=np.pi, eps=1e-9):
    """
    Generic angle encoder.

    scale = π   → standard datasets
    scale = 2π  → XOR / health-style datasets
    """
    x = np.clip(x, xmin, xmax)
    return scale * (x - xmin) / (xmax - xmin + eps)


def feature_map(theta_x, theta_y, entangle=False):
    qc = QuantumCircuit(2)
    qc.ry(theta_x, 0)
    qc.ry(theta_y, 1)
    if entangle:
        qc.cx(0, 1)
    return qc

def quantum_zz(data, entangle=False, health_mode=False):
    heights, weights = data[:, 0], data[:, 1]
    hmin, hmax = heights.min(), heights.max()
    wmin, wmax = weights.min(), weights.max()

    scale = 2 * np.pi if health_mode else np.pi

    ZZ = SparsePauliOp.from_list([("ZZ", 1)])
    estimator = StatevectorEstimator()

    values = []
    for h, w in data:
        qc = feature_map(
            angle_encode(h, hmin, hmax, scale=scale),
            angle_encode(w, wmin, wmax, scale=scale),
            entangle,
        )
        job = estimator.run([(qc, ZZ)])
        values.append(job.result()[0].data.evs)

    return np.array(values)


def classical_corr(data):
    return pearsonr(data[:, 0], data[:, 1])



# ======================================================
# DATASETS (single source of truth)
# ======================================================
np.random.seed(42)

# Base X variable
x = np.linspace(150, 199, 100)

# 1. Positive Correlation
noise_pos = np.random.normal(0, 2.0, 100)
y_pos = 0.5 * x - 25 + noise_pos

# 2. Negative Correlation
noise_neg = np.random.normal(0, 2.0, 100)
y_neg = -0.5 * x + 150 + noise_neg

# 3. Uncorrelated
y_uncorr = np.random.uniform(40, 100, 100)


def generate_real_world_health_data(n_points=100):
    # Realistic ranges
    # Height: 150cm to 200cm | Weight: 50kg to 110kg
    
    data = []
    labels = []
    
    for _ in range(n_points):
        case = np.random.choice(['TL', 'SH', 'SL', 'TH'])
        
        if case == 'TL': # Tall & Light (Outlier)
            h, w = np.random.uniform(185, 200), np.random.uniform(50, 65)
            labels.append(1)
        elif case == 'SH': # Short & Heavy (Outlier)
            h, w = np.random.uniform(150, 165), np.random.uniform(95, 110)
            labels.append(1)
        elif case == 'SL': # Short & Light (Standard)
            h, w = np.random.uniform(150, 165), np.random.uniform(50, 65)
            labels.append(0)
        else: # TH: Tall & Heavy (Standard)
            h, w = np.random.uniform(185, 200), np.random.uniform(95, 110)
            labels.append(0)
            
        data.append((h, w))
        
    return np.array(data), np.array(labels)

data_health, labels_health = generate_real_world_health_data()
    


DATASETS = {
    "Positive Correlation": np.column_stack((x, y_pos)).astype(float),
    "Negative Correlation": np.column_stack((x, y_neg)).astype(float),
    "Uncorrelated": np.column_stack((x, y_uncorr)).astype(float),
    "X-or health data": data_health,
}
