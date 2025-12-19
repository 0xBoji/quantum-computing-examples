from __future__ import annotations

import argparse
import math
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np


def qft_dagger(qc: QuantumCircuit, n: int) -> None:
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


def apply_controlled_unitary(qc: QuantumCircuit, control_qubits: list, target_qubit: int, phase: float) -> None:
    """Apply controlled-U^(2^k) gates where U is a phase gate.
    
    U|ψ⟩ = e^(2πiφ)|ψ⟩ where φ is the phase we want to estimate.
    U^(2^k) adds 2^k repetitions of the phase.
    """
    for k, control in enumerate(control_qubits):
        # U^(2^k) = e^(2πi * 2^k * φ)
        angle = 2 * math.pi * phase * (2 ** k)
        qc.cp(angle, control, target_qubit)


def run_phase_estimation(n_counting: int, phase: float, shots: int = 1024) -> Dict[str, int]:
    """Run Quantum Phase Estimation algorithm.
    
    Args:
        n_counting: Number of counting qubits (precision = 1/2^n_counting)
        phase: The phase to estimate (between 0 and 1)
        shots: Number of measurement shots
    
    Returns:
        Measurement counts on counting register
    """
    if n_counting <= 0:
        raise ValueError("n_counting must be >= 1")
    if not 0 <= phase <= 1:
        raise ValueError("phase must be between 0 and 1")
    if shots <= 0:
        raise ValueError("shots must be >= 1")
    
    # n_counting qubits for counting, 1 eigenstate qubit
    n_total = n_counting + 1
    qc = QuantumCircuit(n_total, n_counting)
    
    # Prepare eigenstate |1⟩ in the target qubit
    target_qubit = n_counting
    qc.x(target_qubit)
    
    # Apply Hadamard to counting qubits
    for i in range(n_counting):
        qc.h(i)
    
    qc.barrier()
    
    # Apply controlled-U^(2^k) operations
    control_qubits = list(range(n_counting))
    apply_controlled_unitary(qc, control_qubits, target_qubit, phase)
    
    qc.barrier()
    
    # Apply inverse QFT on counting register
    qft_dagger(qc, n_counting)
    
    qc.barrier()
    
    # Measure counting register
    for i in range(n_counting):
        qc.measure(i, i)
    
    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def binary_to_phase(binary_str: str) -> float:
    """Convert binary string to phase value (0.binary)."""
    phase = 0.0
    for i, bit in enumerate(binary_str):
        if bit == "1":
            phase += 1 / (2 ** (i + 1))
    return phase


def print_phase_estimation_results(counts: Dict[str, int], true_phase: float, n_counting: int, shots: int) -> None:
    print(f"\n[Quantum Phase Estimation]")
    print(f"True phase φ = {true_phase:.6f}")
    print(f"Counting qubits: {n_counting} (theoretical precision: ±{1/(2**n_counting):.6f})")
    
    print("\nRaw measurement counts:")
    print(counts)
    
    print("\nTop measured states and estimated phases:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (state, count) in enumerate(sorted_counts[:5]):
        prob = count / shots
        # Convert binary measurement to phase estimate
        estimated_phase = binary_to_phase(state)
        error = abs(estimated_phase - true_phase)
        
        marker = " ← most probable" if i == 0 else ""
        print(f"  |{state}⟩: {count:4d} ({prob:.3f}) → φ ≈ {estimated_phase:.6f} (error: {error:.6f}){marker}")
    
    # Best estimate
    best_state = sorted_counts[0][0]
    best_estimate = binary_to_phase(best_state)
    best_error = abs(best_estimate - true_phase)
    
    print(f"\nBest estimate: φ ≈ {best_estimate:.6f}")
    print(f"Absolute error: {best_error:.6f}")
    print(f"Relative error: {100 * best_error / true_phase:.2f}%" if true_phase != 0 else "N/A")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Phase Estimation (QPE) demo")
    parser.add_argument("--n-counting", type=int, default=4, help="Number of counting qubits (>=1)")
    parser.add_argument("--phase", type=float, default=0.375, help="Phase to estimate (0 to 1)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")
    
    args = parser.parse_args()
    
    counts = run_phase_estimation(
        n_counting=args.n_counting,
        phase=args.phase,
        shots=args.shots
    )
    print_phase_estimation_results(counts, args.phase, args.n_counting, args.shots)


if __name__ == "__main__":
    main()
