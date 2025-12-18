from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def apply_oracle_bv(qc: QuantumCircuit, secret: str) -> None:
    """Apply the Bernstein–Vazirani oracle for a given secret bitstring.

    Qubit layout:
      - qubits 0..n-1: input register
      - qubit n: ancilla

    f(x) = a · x (mod 2), where a is the secret bitstring.
    The oracle marks f(x) into the ancilla with CNOT gates.
    """
    n = len(secret)
    for i, bit in enumerate(reversed(secret)):
        # secret string assumed most-significant bit first; map to qubits 0..n-1
        if bit == "1":
            qc.cx(i, n)


def run_bernstein_vazirani(secret: str, shots: int = 1024) -> Dict[str, int]:
    """Run the Bernstein–Vazirani algorithm for a given secret bitstring.

    Returns counts over the measured input register, which ideally reveal the secret.
    """
    if not secret or any(bit not in {"0", "1"} for bit in secret):
        raise ValueError("secret must be a non-empty bitstring of 0s and 1s")
    if shots <= 0:
        raise ValueError("shots must be >= 1")

    n = len(secret)
    qc = QuantumCircuit(n + 1, n)

    # Prepare ancilla in |1>
    qc.x(n)

    # Apply H to all qubits (inputs + ancilla)
    for i in range(n + 1):
        qc.h(i)

    # Oracle encodes f(x) = a · x into ancilla
    apply_oracle_bv(qc, secret)

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


def print_bv_results(counts: Dict[str, int], secret: str, shots: int) -> None:
    print(f"\n[bernstein_vazirani] secret = {secret}")
    print("Raw counts:")
    print(counts)

    # Identify the most frequent bitstring as the recovered secret
    if counts:
        recovered = max(counts.items(), key=lambda item: item[1])[0]
    else:
        recovered = ""

    print("\nInferred secret (most frequent result):")
    print(f"  recovered: {recovered}")
    print(f"  expected : {secret}")
    if recovered == secret:
        print("  status   : match")
    else:
        print("  status   : mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bernstein–Vazirani algorithm demo")
    parser.add_argument("--secret", type=str, default="1011", help="Secret bitstring a (e.g. 1011)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    counts = run_bernstein_vazirani(secret=args.secret, shots=args.shots)
    print_bv_results(counts, args.secret, args.shots)


if __name__ == "__main__":
    main()
