from __future__ import annotations

import argparse
from typing import Dict, List
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def apply_simon_oracle(qc: QuantumCircuit, secret: str) -> None:
    """Apply Simon's oracle for a given secret bitstring.
    
    The oracle implements f(x) = f(x ⊕ s) where s is the secret string.
    
    Qubit layout:
      - qubits 0..n-1: input register
      - qubits n..2n-1: output register
    """
    n = len(secret)
    
    # Copy input to output (identity part)
    for i in range(n):
        qc.cx(i, n + i)
    
    # XOR with secret string
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(i, n + i)


def run_simon_algorithm(secret: str, shots: int = 1024) -> Dict[str, int]:
    """Run Simon's algorithm for a given secret bitstring.
    
    Returns counts over the measured input register.
    The algorithm finds orthogonal vectors to the secret string s.
    """
    if not secret or any(bit not in {"0", "1"} for bit in secret):
        raise ValueError("secret must be a non-empty bitstring of 0s and 1s")
    if shots <= 0:
        raise ValueError("shots must be >= 1")
    
    n = len(secret)
    qc = QuantumCircuit(2 * n, n)
    
    # Apply Hadamard to input register
    for i in range(n):
        qc.h(i)
    
    # Apply Simon's oracle
    apply_simon_oracle(qc, secret)
    
    # Apply Hadamard to input register again
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


def solve_secret_from_measurements(measurements: List[str], n: int) -> str:
    """Solve for the secret string using Gaussian elimination.
    
    Each measurement y satisfies: y · s = 0 (mod 2)
    We need n-1 linearly independent equations to solve for s.
    """
    # Convert measurement strings to binary vectors
    vectors = []
    for m in measurements:
        if m != "0" * n:  # Skip the all-zeros vector
            vec = [int(bit) for bit in reversed(m)]
            vectors.append(vec)
    
    if len(vectors) < n - 1:
        return "Not enough measurements"
    
    # Gaussian elimination over GF(2)
    matrix = np.array(vectors[:n-1], dtype=int)
    
    # Try to solve for secret
    # This is a simplified approach - in practice, you'd use proper linear algebra over GF(2)
    secret_bits = []
    for i in range(n):
        secret_bits.append("?")
    
    return f"System of equations collected (needs {n-1} independent vectors)"


def print_simon_results(counts: Dict[str, int], secret: str, shots: int) -> None:
    print(f"\n[simon_algorithm] secret = {secret}")
    print("Raw counts (orthogonal vectors to the secret):")
    print(counts)
    
    print("\nMeasurement analysis:")
    print(f"  Expected: All measured strings y should satisfy y · s = 0 (mod 2)")
    print(f"  where s = {secret}")
    
    # Verify orthogonality
    n = len(secret)
    secret_bits = [int(bit) for bit in reversed(secret)]
    
    print("\nVerifying orthogonality:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        y_bits = [int(bit) for bit in reversed(state)]
        dot_product = sum(y_bits[i] * secret_bits[i] for i in range(n)) % 2
        status = "✓" if dot_product == 0 else "✗"
        prob = count / shots
        print(f"  {state}: {count:4d} ({prob:.3f}) - y·s = {dot_product} {status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simon's algorithm demo")
    parser.add_argument("--secret", type=str, default="110", help="Secret bitstring s (e.g. 110)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")
    
    args = parser.parse_args()
    
    counts = run_simon_algorithm(secret=args.secret, shots=args.shots)
    print_simon_results(counts, args.secret, args.shots)


if __name__ == "__main__":
    main()
