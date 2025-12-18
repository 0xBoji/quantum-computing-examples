from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def run_quantum_coin(num_qubits: int = 1, shots: int = 1024) -> Dict[str, int]:
    """Simulate a quantum coin/dice using Hadamard gates.

    - num_qubits = 1  -> 2 outcomes (0, 1)  ~ coin
    - num_qubits = 2  -> 4 outcomes (00..11) ~ 4-sided dice (base-2)
    - num_qubits = n  -> 2^n outcomes
    """
    if num_qubits <= 0:
        raise ValueError("num_qubits must be >= 1")
    if shots <= 0:
        raise ValueError("shots must be >= 1")

    qc = QuantumCircuit(num_qubits)

    # Put all qubits into equal superposition
    for qubit in range(num_qubits):
        qc.h(qubit)

    qc.measure_all()

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def print_counts_and_probabilities(counts: Dict[str, int], shots: int) -> None:
    print("Raw counts:")
    print(counts)
    print("\nProbabilities:")
    for state, count in sorted(counts.items(), reverse=True):
        prob = count / shots
        print(f"  {state}: {count} / {shots} ≈ {prob:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum coin/dice demo using Qiskit")
    parser.add_argument("--qubits", type=int, default=1, help="Number of qubits (>=1)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    counts = run_quantum_coin(num_qubits=args.qubits, shots=args.shots)

    print(f"\nQuantum coin/dice with {args.qubits} qubit(s), {args.shots} shots")
    print_counts_and_probabilities(counts, args.shots)


if __name__ == "__main__":
    main()
