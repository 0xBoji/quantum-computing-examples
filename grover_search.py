from __future__ import annotations

import argparse
import math
from typing import Dict, List

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def create_oracle(qc: QuantumCircuit, n: int, target: str) -> None:
    """Create phase-flip oracle that marks the target state.
    
    Args:
        qc: Quantum circuit
        n: Number of qubits
        target: Target bitstring to mark
    """
    # Flip qubits where target bit is 0
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)
    
    # Multi-controlled Z gate
    if n == 1:
        qc.z(0)
    elif n == 2:
        qc.cz(0, 1)
    else:
        # Use multi-controlled Z (MCZ)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
    
    # Unflip qubits
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)


def create_diffusion_operator(qc: QuantumCircuit, n: int) -> None:
    """Create Grover's diffusion operator (inversion about average).
    
    This operator applies: 2|s⟩⟨s| - I where |s⟩ is uniform superposition.
    """
    # Apply H to all qubits
    for i in range(n):
        qc.h(i)
    
    # Apply X to all qubits
    for i in range(n):
        qc.x(i)
    
    # Multi-controlled Z gate
    if n == 1:
        qc.z(0)
    elif n == 2:
        qc.cz(0, 1)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
    
    # Apply X to all qubits
    for i in range(n):
        qc.x(i)
    
    # Apply H to all qubits
    for i in range(n):
        qc.h(i)


def run_grover_search(n: int, target: str, iterations: int = None, shots: int = 1024) -> Dict[str, int]:
    """Run Grover's search algorithm.
    
    Args:
        n: Number of qubits
        target: Target bitstring to search for
        iterations: Number of Grover iterations (auto-calculated if None)
        shots: Number of measurement shots
    
    Returns:
        Measurement counts
    """
    if n <= 0:
        raise ValueError("n must be >= 1")
    if len(target) != n or any(bit not in {"0", "1"} for bit in target):
        raise ValueError(f"target must be a {n}-bit string")
    if shots <= 0:
        raise ValueError("shots must be >= 1")
    
    # Calculate optimal number of iterations
    if iterations is None:
        N = 2 ** n
        iterations = int(math.pi / 4 * math.sqrt(N))
        iterations = max(1, iterations)
    
    qc = QuantumCircuit(n, n)
    
    # Initialize to uniform superposition
    for i in range(n):
        qc.h(i)
    
    # Apply Grover iteration
    for _ in range(iterations):
        qc.barrier()
        
        # Oracle
        create_oracle(qc, n, target)
        
        # Diffusion operator
        create_diffusion_operator(qc, n)
    
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


def print_grover_results(counts: Dict[str, int], target: str, n: int, iterations: int, shots: int) -> None:
    N = 2 ** n
    optimal_iterations = int(math.pi / 4 * math.sqrt(N))
    
    print(f"\n[Grover's Search Algorithm]")
    print(f"Search space: {N} states ({n} qubits)")
    print(f"Target state: |{target}⟩")
    print(f"Grover iterations: {iterations} (optimal ≈ {optimal_iterations})")
    
    print("\nMeasurement results:")
    print(counts)
    
    print("\nTop measured states:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (state, count) in enumerate(sorted_counts[:10]):
        prob = count / shots
        marker = " ← target" if state == target else ""
        print(f"  |{state}⟩: {count:4d} / {shots} ≈ {prob:.3f}{marker}")
    
    # Success probability
    target_count = counts.get(target, 0)
    success_prob = target_count / shots
    
    print(f"\nSuccess probability: {success_prob:.4f}")
    print(f"Classical random search: {1/N:.4f}")
    print(f"Speedup factor: {success_prob / (1/N):.2f}x" if success_prob > 0 else "N/A")


def main() -> None:
    parser = argparse.ArgumentParser(description="Grover's Search Algorithm")
    parser.add_argument("--n", type=int, default=3, help="Number of qubits (>=1)")
    parser.add_argument("--target", type=str, default=None, help="Target bitstring (e.g. '101')")
    parser.add_argument("--iterations", type=int, default=None, help="Number of Grover iterations (auto if not specified)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")
    
    args = parser.parse_args()
    
    # Generate default target if not provided
    target = args.target if args.target else "1" * args.n
    
    if len(target) != args.n:
        raise SystemExit(f"Target must be {args.n} bits")
    
    counts = run_grover_search(
        n=args.n,
        target=target,
        iterations=args.iterations,
        shots=args.shots
    )
    
    iterations_used = args.iterations if args.iterations else int(math.pi / 4 * math.sqrt(2 ** args.n))
    iterations_used = max(1, iterations_used)
    
    print_grover_results(counts, target, args.n, iterations_used, args.shots)


if __name__ == "__main__":
    main()
