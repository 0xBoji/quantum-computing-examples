from __future__ import annotations

import argparse
from typing import Dict, List

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
import numpy as np


def run_circuit_with_statevector(qc: QuantumCircuit) -> Statevector:
    """Run a circuit and return the final statevector (before measurement)."""
    # Remove any measurements to get pure statevector
    qc_copy = qc.copy()
    qc_copy.remove_final_measurements(inplace=False)
    
    # Use statevector simulator
    sv = Statevector(qc_copy)
    return sv


def print_statevector_analysis(sv: Statevector, label: str = "Circuit") -> None:
    """Print detailed analysis of a statevector."""
    print(f"\n=== {label} Statevector Analysis ===")
    
    n_qubits = sv.num_qubits
    print(f"Number of qubits: {n_qubits}")
    print(f"Dimension: {sv.dim}")
    
    print("\nAmplitudes (complex):")
    data = sv.data
    for i, amplitude in enumerate(data):
        bitstring = format(i, f"0{n_qubits}b")
        real = amplitude.real
        imag = amplitude.imag
        prob = abs(amplitude) ** 2
        
        # Only print non-negligible amplitudes
        if prob > 1e-6:
            print(f"  |{bitstring}⟩: ({real:+.4f} {imag:+.4f}j)  probability: {prob:.4f}")
    
    print("\nProbabilities (measurement outcomes):")
    probs = sv.probabilities()
    for i, prob in enumerate(probs):
        if prob > 1e-6:
            bitstring = format(i, f"0{n_qubits}b")
            print(f"  |{bitstring}⟩: {prob:.4f}")


def demo_bell_state_statevector() -> None:
    """Demo: Bell state statevector analysis."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    sv = run_circuit_with_statevector(qc)
    print_statevector_analysis(sv, "Bell State (|00⟩ + |11⟩)/√2")


def demo_hadamard_statevector() -> None:
    """Demo: Single Hadamard statevector."""
    qc = QuantumCircuit(1)
    qc.h(0)
    
    sv = run_circuit_with_statevector(qc)
    print_statevector_analysis(sv, "Single Hadamard")


def demo_grover_statevector() -> None:
    """Demo: Grover iteration statevector (before measurement)."""
    qc = QuantumCircuit(2)
    
    # Equal superposition
    qc.h([0, 1])
    
    # Oracle for target |11⟩
    qc.cz(0, 1)
    
    # Diffusion
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    
    sv = run_circuit_with_statevector(qc)
    print_statevector_analysis(sv, "Grover (1 iteration, target |11⟩)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Statevector simulator demo")
    parser.add_argument(
        "--demo",
        type=str,
        choices=["bell", "hadamard", "grover", "all"],
        default="all",
        help="Which statevector demo to run",
    )
    
    args = parser.parse_args()
    
    if args.demo in ("bell", "all"):
        demo_bell_state_statevector()
    
    if args.demo in ("hadamard", "all"):
        demo_hadamard_statevector()
    
    if args.demo in ("grover", "all"):
        demo_grover_statevector()


if __name__ == "__main__":
    main()
