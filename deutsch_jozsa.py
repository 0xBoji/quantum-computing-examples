from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def apply_oracle_dj(qc: QuantumCircuit, n: int, oracle_type: str) -> None:
    """Apply a simple Deutsch–Jozsa oracle on the circuit.

    Qubit layout:
      - qubits 0..n-1: input register
      - qubit n: ancilla

    Supported oracle types:
      - "constant_zero"  : f(x) = 0
      - "constant_one"   : f(x) = 1
      - "balanced_first" : f(x) = x_0
      - "balanced_parity": f(x) = x_0 ⊕ x_1 ⊕ ... ⊕ x_{n-1}
    """
    if oracle_type == "constant_zero":
        # f(x) = 0, do nothing
        return
    if oracle_type == "constant_one":
        # f(x) = 1, flip ancilla for all inputs
        qc.x(n)
        return
    if oracle_type == "balanced_first":
        # f(x) = x_0, use CNOT from first input onto ancilla
        qc.cx(0, n)
        return
    if oracle_type == "balanced_parity":
        # f(x) = parity of all input bits
        for i in range(n):
            qc.cx(i, n)
        return

    raise ValueError("Unsupported oracle_type for Deutsch–Jozsa")


def run_deutsch_jozsa(n: int, oracle_type: str, shots: int = 1024) -> Dict[str, int]:
    """Run the Deutsch–Jozsa algorithm on n input qubits.

    Returns a counts dictionary over the measured input register.
    """
    if n <= 0:
        raise ValueError("n must be >= 1")
    if shots <= 0:
        raise ValueError("shots must be >= 1")

    # n input qubits + 1 ancilla, measure only the n input qubits
    qc = QuantumCircuit(n + 1, n)

    # Prepare ancilla in |1>
    qc.x(n)

    # Apply H to all qubits (inputs + ancilla)
    for i in range(n + 1):
        qc.h(i)

    # Oracle U_f
    apply_oracle_dj(qc, n, oracle_type)

    # Apply H on input register again
    for i in range(n):
        qc.h(i)

    # Measure input register
    for i in range(n):
        qc.measure(i, i)

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def classify_deutsch_jozsa(counts: Dict[str, int], n: int) -> str:
    """Classify oracle as constant or balanced based on measurement results."""
    total = sum(counts.values())
    if total == 0:
        return "unknown"

    # In the ideal case, all probability mass on 0^n for constant, none for balanced.
    zero_string = "0" * n
    zero_counts = counts.get(zero_string, 0)
    # Use a simple heuristic threshold
    if zero_counts > 0.8 * total:
        return "constant"
    return "balanced"


def print_dj_results(counts: Dict[str, int], n: int, oracle_type: str, shots: int) -> None:
    classification = classify_deutsch_jozsa(counts, n)

    print(f"\n[deutsch_jozsa] n = {n}, oracle_type = {oracle_type}")
    print("Raw counts:")
    print(counts)
    print("\nClassification (Deutsch–Jozsa):")
    print(f"  Detected as: {classification}")
    print(f"  Ideal behavior: constant -> all zeros, balanced -> any non-zero bitstring")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deutsch–Jozsa algorithm demo")
    parser.add_argument("--n", type=int, default=2, help="Number of input qubits (>=1)")
    parser.add_argument(
        "--oracle",
        type=str,
        choices=["constant_zero", "constant_one", "balanced_first", "balanced_parity"],
        default="balanced_parity",
        help="Type of oracle function to use",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    counts = run_deutsch_jozsa(n=args.n, oracle_type=args.oracle, shots=args.shots)
    print_dj_results(counts, args.n, args.oracle, args.shots)


if __name__ == "__main__":
    main()
