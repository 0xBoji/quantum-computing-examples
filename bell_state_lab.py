from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def run_bell_state(shots: int = 1024) -> Dict[str, int]:
    """Create and measure a Bell state (maximally entangled)."""
    qc = QuantumCircuit(2)

    # Create Bell state (|00> + |11>) / sqrt(2)
    qc.h(0)
    qc.cx(0, 1)

    qc.measure_all()

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def run_product_superposition(shots: int = 1024) -> Dict[str, int]:
    """Create a product state H⊗H (no entanglement)."""
    qc = QuantumCircuit(2)

    # Independent superposition on each qubit: (|0>+|1>)⊗(|0>+|1>) / 2
    qc.h(0)
    qc.h(1)

    qc.measure_all()

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def print_counts_and_probabilities(title: str, counts: Dict[str, int], shots: int) -> None:
    print(f"\n=== {title} ===")
    print("Raw counts:")
    print(counts)
    print("Probabilities:")
    for state, count in sorted(counts.items(), reverse=True):
        prob = count / shots
        print(f"  {state}: {count} / {shots} ≈ {prob:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bell state vs product state demo")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["bell", "product", "both"],
        default="both",
        help="Which circuit(s) to run: bell, product, or both (default)",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    if args.mode in ("bell", "both"):
        bell_counts = run_bell_state(shots=args.shots)
        print_counts_and_probabilities("Bell state (entangled)", bell_counts, args.shots)

    if args.mode in ("product", "both"):
        product_counts = run_product_superposition(shots=args.shots)
        print_counts_and_probabilities("Product H⊗H state (not entangled)", product_counts, args.shots)


if __name__ == "__main__":
    main()
