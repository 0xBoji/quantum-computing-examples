from __future__ import annotations

import argparse
import math
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def apply_oracle_2_qubits(qc: QuantumCircuit, target: str) -> None:
    """Phase-flip oracle for a 2-qubit target state.

    `target` is a bitstring like '00', '01', '10', '11'.
    We follow Qiskit's bitstring convention where the leftmost bit
    corresponds to the highest qubit index.
    """
    if len(target) != 2 or any(bit not in {"0", "1"} for bit in target):
        raise ValueError("target must be a 2-bit string like '00', '01', '10', or '11'")

    num_qubits = 2

    # Map bitstring to qubits: leftmost bit -> qubit 1, rightmost -> qubit 0
    for qubit in range(num_qubits):
        bit = target[num_qubits - 1 - qubit]
        if bit == "0":
            qc.x(qubit)

    # Apply CZ to flip the phase of |11>
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)

    # Uncompute the X gates
    for qubit in range(num_qubits):
        bit = target[num_qubits - 1 - qubit]
        if bit == "0":
            qc.x(qubit)


def apply_diffusion_2_qubits(qc: QuantumCircuit) -> None:
    """Diffusion operator for 2 qubits (Grover's diffuser)."""
    qc.h([0, 1])
    qc.x([0, 1])

    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)

    qc.x([0, 1])
    qc.h([0, 1])


def run_baby_grover_2_qubits(target: str, shots: int = 1024) -> Dict[str, int]:
    """Run a single-iteration Grover search on 2 qubits for the given target.

    For N = 4 states, optimal Grover iterations ≈ π/4 * sqrt(N) ≈ 1,
    so 1 iteration is enough to significantly boost the target state's probability.
    """
    qc = QuantumCircuit(2)

    # Start in equal superposition over all 4 states
    qc.h([0, 1])

    # Oracle marks the target state
    apply_oracle_2_qubits(qc, target)

    # Diffusion operator amplifies the marked state's amplitude
    apply_diffusion_2_qubits(qc)

    qc.measure_all()

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def print_counts_and_probabilities(counts: Dict[str, int], shots: int, highlight: str | None = None) -> None:
    print("Raw counts:")
    print(counts)
    print("\nProbabilities:")
    for state, count in sorted(counts.items(), reverse=True):
        prob = count / shots
        mark = " <== target" if highlight is not None and state == highlight else ""
        print(f"  {state}: {count} / {shots} ≈ {prob:.3f}{mark}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Baby Grover search on 2 qubits")
    parser.add_argument(
        "--target",
        type=str,
        default="11",
        help="2-bit target string in {00,01,10,11} (default: 11)",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    target = args.target
    if len(target) != 2 or any(bit not in {"0", "1"} for bit in target):
        raise SystemExit("--target must be one of: 00, 01, 10, 11")
    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    counts = run_baby_grover_2_qubits(target=target, shots=args.shots)

    print(f"\nBaby Grover search on 2 qubits for target state: {target}")
    print_counts_and_probabilities(counts, args.shots, highlight=target)


if __name__ == "__main__":
    main()
