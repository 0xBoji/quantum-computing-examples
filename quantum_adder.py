from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def majority_gate(qc: QuantumCircuit, a: int, b: int, c: int) -> None:
    """Apply MAJ gate for quantum addition.
    
    MAJ gate computes the majority of three bits and prepares carry.
    """
    qc.cx(c, b)
    qc.cx(c, a)
    qc.ccx(a, b, c)


def unmajority_gate(qc: QuantumCircuit, a: int, b: int, c: int) -> None:
    """Apply UMA (unmajority-add) gate for quantum addition.
    
    UMA gate undoes MAJ and adds the result.
    """
    qc.ccx(a, b, c)
    qc.cx(c, a)
    qc.cx(a, b)


def quantum_ripple_carry_adder(qc: QuantumCircuit, a_qubits: list, b_qubits: list, carry_in: int, carry_out: int) -> None:
    """Implement quantum ripple-carry adder.
    
    Adds two n-bit numbers stored in a_qubits and b_qubits.
    Result is stored in b_qubits, with carry in carry_out.
    
    Args:
        qc: Quantum circuit
        a_qubits: List of qubit indices for first number (LSB first)
        b_qubits: List of qubit indices for second number (LSB first)
        carry_in: Qubit index for carry in (usually prepared as |0⟩)
        carry_out: Qubit index for final carry out
    """
    n = len(a_qubits)
    
    # Forward pass: propagate carries
    for i in range(n):
        if i == 0:
            majority_gate(qc, carry_in, b_qubits[i], a_qubits[i])
        else:
            majority_gate(qc, a_qubits[i-1], b_qubits[i], a_qubits[i])
    
    # Final carry
    qc.cx(a_qubits[n-1], carry_out)
    
    # Backward pass: compute sum and uncompute carries
    for i in range(n-1, -1, -1):
        if i == 0:
            unmajority_gate(qc, carry_in, b_qubits[i], a_qubits[i])
        else:
            unmajority_gate(qc, a_qubits[i-1], b_qubits[i], a_qubits[i])


def run_quantum_addition(a: int, b: int, n_bits: int = 4, shots: int = 1024) -> Dict[str, int]:
    """Run quantum addition of two integers.
    
    Args:
        a: First integer (0 to 2^n_bits - 1)
        b: Second integer (0 to 2^n_bits - 1)
        n_bits: Number of bits for each number
        shots: Number of measurement shots
    
    Returns:
        Measurement counts
    """
    if a < 0 or a >= 2**n_bits:
        raise ValueError(f"a must be between 0 and {2**n_bits - 1}")
    if b < 0 or b >= 2**n_bits:
        raise ValueError(f"b must be between 0 and {2**n_bits - 1}")
    if n_bits <= 0:
        raise ValueError("n_bits must be >= 1")
    if shots <= 0:
        raise ValueError("shots must be >= 1")
    
    # Circuit layout:
    # - qubits 0..n-1: register a (input)
    # - qubits n..2n-1: register b (input, becomes sum output)
    # - qubit 2n: carry_in (initialized to 0)
    # - qubit 2n+1: carry_out
    total_qubits = 2 * n_bits + 2
    qc = QuantumCircuit(total_qubits, n_bits + 1)
    
    a_qubits = list(range(n_bits))
    b_qubits = list(range(n_bits, 2 * n_bits))
    carry_in = 2 * n_bits
    carry_out = 2 * n_bits + 1
    
    # Prepare input states
    # Encode a in register a (LSB first)
    a_bits = format(a, f'0{n_bits}b')[::-1]  # Reverse for LSB first
    for i, bit in enumerate(a_bits):
        if bit == '1':
            qc.x(a_qubits[i])
    
    # Encode b in register b (LSB first)
    b_bits = format(b, f'0{n_bits}b')[::-1]  # Reverse for LSB first
    for i, bit in enumerate(b_bits):
        if bit == '1':
            qc.x(b_qubits[i])
    
    qc.barrier()
    
    # Perform quantum addition
    quantum_ripple_carry_adder(qc, a_qubits, b_qubits, carry_in, carry_out)
    
    qc.barrier()
    
    # Measure result (b_qubits + carry_out)
    for i in range(n_bits):
        qc.measure(b_qubits[i], i)
    qc.measure(carry_out, n_bits)
    
    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def print_addition_results(counts: Dict[str, int], a: int, b: int, n_bits: int, shots: int) -> None:
    expected_sum = a + b
    expected_binary = format(expected_sum, f'0{n_bits+1}b')
    
    print(f"\n[Quantum Addition]")
    print(f"Input a = {a} (binary: {format(a, f'0{n_bits}b')})")
    print(f"Input b = {b} (binary: {format(b, f'0{n_bits}b')})")
    print(f"Expected sum = {expected_sum} (binary: {expected_binary})")
    
    print("\nMeasurement results:")
    print(counts)
    
    print("\nAnalysis:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Convert measured bitstring to integer (LSB first, but Qiskit returns MSB first)
        measured_value = int(state, 2)
        prob = count / shots
        marker = " ← expected" if state == expected_binary else ""
        print(f"  {state} = {measured_value}: {count:4d} / {shots} ≈ {prob:.3f}{marker}")
    
    # Success rate
    success_count = counts.get(expected_binary, 0)
    success_prob = success_count / shots
    print(f"\nSuccess probability: {success_prob:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Addition using Ripple-Carry Adder")
    parser.add_argument("--a", type=int, default=3, help="First integer to add")
    parser.add_argument("--b", type=int, default=5, help="Second integer to add")
    parser.add_argument("--n-bits", type=int, default=4, help="Number of bits per number (>=1)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")
    
    args = parser.parse_args()
    
    counts = run_quantum_addition(
        a=args.a,
        b=args.b,
        n_bits=args.n_bits,
        shots=args.shots
    )
    print_addition_results(counts, args.a, args.b, args.n_bits, args.shots)


if __name__ == "__main__":
    main()
