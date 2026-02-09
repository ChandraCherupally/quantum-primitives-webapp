from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit_ibm_runtime import SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
import os

def build_rng_circuit(num_bits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_bits)
    qc.h(range(num_bits))
    qc.measure_all()
    return qc


def rng_statevector(num_bits: int):
    qc = build_rng_circuit(num_bits)
    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=1)
    result = job.result()

    bitstring = next(iter(result[0].data.meas.get_counts()))
    return bitstring, int(bitstring, 2), qc


def rng_hardware(num_bits):
    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=os.getenv("IBM_QUANTUM_API_KEY"),
    )

    backend = service.least_busy(operational=True)
    print(backend.name)

    qc = build_rng_circuit(num_bits)

    pm = generate_preset_pass_manager(
    backend=backend, optimization_level=3
    )
    isa_qc = pm.run(qc)

    sampler = SamplerV2(backend)
    job = sampler.run([isa_qc], shots=1)
    result = job.result()

    bitstring = next(iter(result[0].data.meas.get_counts()))
    return bitstring, int(bitstring, 2)
