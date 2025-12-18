from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

# 1. Create a quantum circuit with 1 qubit

def run_hello(shots: int = 1000):
    qc = QuantumCircuit(1)

    # 2. Apply Hadamard gate to put the qubit into superposition
    qc.h(0)

    # 3. Measure all qubits
    qc.measure_all()

    # 4. Run on the Aer simulator
    sim = Aer.get_backend("aer_simulator")

    # Transpile for the backend
    compiled_circuit = transpile(qc, sim)

    job = sim.run(compiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return counts


if __name__ == "__main__":
    counts = run_hello()
    print("Measurement results (counts per state):")
    print(counts)
