from __future__ import annotations

import argparse
from typing import Tuple

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer.primitives import EstimatorV2 as Estimator
from qiskit.circuit.library import RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import SamplerV2 as Sampler


def get_h2_hamiltonian() -> SparsePauliOp:
    """Return a simplified PauliSumOp representation of the H2 molecule Hamiltonian.

    This is a toy version for demonstration purposes.
    """
    # Simplified H2 Hamiltonian (in Hartree units)
    pauli_strings = [
        ("II", -1.052373245772859),
        ("IZ", 0.39793742484318045),
        ("ZI", -0.39793742484318045),
        ("ZZ", -0.01128010425624393),
        ("XX", 0.18093119978423156),
    ]
    hamiltonian = SparsePauliOp.from_list(pauli_strings)
    return hamiltonian


def create_ansatz(num_qubits: int, reps: int = 1) -> QuantumCircuit:
    """Create a simple variational form (ansatz) for the VQE algorithm."""
    ansatz = RealAmplitudes(num_qubits=num_qubits, reps=reps)
    # Bind the ansatz to concrete qubits
    ansatz = ansatz.decompose()
    return ansatz


def run_vqe_demo(shots: int = 1024) -> Tuple[float, int]:
    """Run a VQE demo to compute the ground state energy of H2.

    Returns:
        Tuple of (minimum eigenvalue, optimizer evaluations).
    """
    hamiltonian = get_h2_hamiltonian()
    num_qubits = hamiltonian.num_qubits

    ansatz = create_ansatz(num_qubits, reps=1)

    # Initial parameters (random)
    initial_point = np.random.default_rng(42).uniform(-np.pi, np.pi, ansatz.num_parameters)

    # Optimizer
    optimizer = COBYLA(maxiter=100)

    # Backend
    estimator = Estimator()
    estimator.options.default_shots = shots

    # VQE solver
    vqe = VQE(
        ansatz=ansatz,
        optimizer=optimizer,
        initial_point=initial_point,
        estimator=estimator,
    )

    # Solve
    result = vqe.compute_minimum_eigenvalue(operator=hamiltonian)

    return float(result.eigenvalue.real), result.cost_function_evals


def print_vqe_result(energy: float, evals: int) -> None:
    print("\n[VQE Demo] Ground state energy estimation for H2 molecule")
    print(f"Estimated energy (Hartree): {energy:.6f}")
    print(f"Optimizer evaluations: {evals}")

    # Known exact energy for comparison
    exact_energy = -1.137270  # From full configuration interaction (FCI)
    error = abs(energy - exact_energy)
    print(f"Exact energy (Hartree): {exact_energy:.6f}")
    print(f"Error: {error:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Variational Quantum Eigensolver (VQE) demo for H2")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots for simulation (>=1)")

    args = parser.parse_args()

    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    energy, evals = run_vqe_demo(shots=args.shots)
    print_vqe_result(energy, evals)


if __name__ == "__main__":
    main()
