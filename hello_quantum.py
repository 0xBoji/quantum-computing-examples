from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

# 1. Create a quantum circuit with 1 qubit
qc = QuantumCircuit(1)

# 2. Apply Hadamard gate to put the qubit into superposition
qc.h(0)

# 3. Measure all qubits
qc.measure_all()

# 4. Run on the Aer simulator
sim = Aer.get_backend('aer_simulator')

# Transpile for the backend
compiled_circuit = transpile(qc, sim)

job = sim.run(compiled_circuit, shots=1000)
result = job.result()
counts = result.get_counts()

print("Measurement results (counts per state):")
print(counts)
