from __future__ import annotations

import argparse
import math
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np


def qft(qc: QuantumCircuit, n: int) -> None:
    """Apply Quantum Fourier Transform on the first n qubits of circuit qc.
    
    The QFT maps computational basis states to Fourier basis:
    |j⟩ → (1/√N) Σ_k e^(2πijk/N) |k⟩
    """
    for j in range(n):
        # Apply Hadamard to current qubit
        qc.h(j)
        
        # Apply controlled phase rotations
        for k in range(j + 1, n):
            angle = 2 * math.pi / (2 ** (k - j + 1))
            qc.cp(angle, k, j)
    
    # Swap qubits to reverse the order (optional, for standard QFT)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)


def inverse_qft(qc: QuantumCircuit, n: int) -> None:
    """Apply inverse Quantum Fourier Transform on the first n qubits."""
    # Reverse the swaps
    for i in range(n // 2):
        qc.swap(i, n - i - 1)
    
    # Apply inverse of QFT operations in reverse order
    for j in range(n - 1, -1, -1):
        # Apply inverse controlled phase rotations
        for k in range(n - 1, j, -1):
            angle = -2 * math.pi / (2 ** (k - j + 1))
            qc.cp(angle, k, j)
        
        # Apply Hadamard
        qc.h(j)


def run_qft_demo(n: int, initial_state: str, shots: int = 1024) -> Dict[str, int]:
    """Run QFT followed by inverse QFT to demonstrate round-trip.
    
    Args:
        n: Number of qubits
        initial_state: Binary string representing initial computational basis state
        shots: Number of measurement shots
    
    Returns:
        Measurement counts
    """
    if n <= 0:
        raise ValueError("n must be >= 1")
    if len(initial_state) != n or any(bit not in {"0", "1"} for bit in initial_state):
        raise ValueError(f"initial_state must be a {n}-bit string")
    if shots <= 0:
        raise ValueError("shots must be >= 1")
    
    qc = QuantumCircuit(n, n)
    
    # Prepare initial state
    for i, bit in enumerate(reversed(initial_state)):
        if bit == "1":
            qc.x(i)
    
    # Add barrier for visualization
    qc.barrier()
    
    # Apply QFT
    qft(qc, n)
    
    qc.barrier()
    
    # Apply inverse QFT (should recover original state)
    inverse_qft(qc, n)
    
    qc.barrier()
    
    # Measure all qubits
    for i in range(n):
        qc.measure(i, i)
    
    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def run_qft_phase_demo(n: int, shots: int = 1024) -> Dict[str, int]:
    """Demonstrate QFT on a superposition state showing phase encoding."""
    qc = QuantumCircuit(n, n)
    
    # Create equal superposition
    for i in range(n):
        qc.h(i)
    
    qc.barrier()
    
    # Apply QFT
    qft(qc, n)
    
    qc.barrier()
    
    # Measure
    for i in range(n):
        qc.measure(i, i)
    
    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def print_qft_results(counts: Dict[str, int], initial_state: str, shots: int) -> None:
    print(f"\n[QFT Demo] Round-trip test (QFT → inverse QFT)")
    print(f"Initial state: |{initial_state}⟩")
    print("\nMeasurement results (should recover initial state):")
    print(counts)
    
    print("\nProbabilities:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        prob = count / shots
        marker = " ← expected" if state == initial_state else ""
        print(f"  |{state}⟩: {count:4d} / {shots} ≈ {prob:.3f}{marker}")
    
    # Check fidelity
    expected_count = counts.get(initial_state, 0)
    fidelity = expected_count / shots
    print(f"\nFidelity with initial state: {fidelity:.4f}")


def print_phase_results(counts: Dict[str, int], n: int, shots: int) -> None:
    print(f"\n[QFT Demo] QFT on equal superposition ({n} qubits)")
    print("QFT transforms the uniform superposition into a different basis")
    print("\nMeasurement results:")
    print(counts)
    
    print("\nTop measured states:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        prob = count / shots
        print(f"  |{state}⟩: {count:4d} / {shots} ≈ {prob:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Fourier Transform (QFT) demo")
    parser.add_argument("--n", type=int, default=3, help="Number of qubits (>=1)")
    parser.add_argument(
        "--initial-state",
        type=str,
        default=None,
        help="Initial state as binary string (e.g. '101'). If not provided, runs phase demo",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")
    
    args = parser.parse_args()
    
    if args.initial_state:
        # Round-trip test
        counts = run_qft_demo(n=args.n, initial_state=args.initial_state, shots=args.shots)
        print_qft_results(counts, args.initial_state, args.shots)
    else:
        # Phase encoding demo
        counts = run_qft_phase_demo(n=args.n, shots=args.shots)
        print_phase_results(counts, args.n, args.shots)


if __name__ == "__main__":
    main()
