from fastapi import FastAPI
from pydantic import BaseModel
from qiskit_ibm_runtime import QiskitRuntimeService
from quantum.rng import rng_hardware

app = FastAPI()

class RNGRequest(BaseModel):
    num_bits: int


def get_backend():
    
    service = QiskitRuntimeService(channel="ibm_quantum_platform",
                               )
    return service.least_busy(operational=True)


#service.backend("ibm_fez")


@app.post("/rng/hardware")
def run_rng(req: RNGRequest):
    backend = get_backend()
    bits, value = rng_hardware(req.num_bits, backend)
    return {"bitstring": bits, "value": value}
