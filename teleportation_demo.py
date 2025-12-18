from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


def prepare_state(qc: QuantumCircuit, qubit: int, state: str) -> None:
    """Prepare a simple 1-qubit state on the given qubit.

    Supported states:
      - 'zero' : |0>
      - 'one'  : |1>
      - 'plus' : (|0> + |1>)/sqrt(2)
      - 'minus': (|0> - |1>)/sqrt(2)
    """
    if state == "zero":
        # |0> is default, nothing to do
        return
    if state == "one":
        qc.x(qubit)
    elif state == "plus":
        qc.h(qubit)
    elif state == "minus":
        qc.x(qubit)
        qc.h(qubit)
    else:
        raise ValueError("Unsupported state. Use zero, one, plus, or minus.")


def build_teleportation_circuit(state: str) -> QuantumCircuit:
    """Build a standard 3-qubit quantum teleportation circuit.

    This version omits in-circuit classical control and instead relies on
    classical post-processing of measurement results to emulate the
    corrective X operation.
    """
    qc = QuantumCircuit(3, 3)

    # 1. Prepare the state to teleport on qubit 0
    prepare_state(qc, 0, state)

    # 2. Create Bell pair between qubits 1 and 2
    qc.h(1)
    qc.cx(1, 2)

    # 3. Bell measurement on qubits 0 and 1
    qc.cx(0, 1)
    qc.h(0)

    qc.measure(0, 0)
    qc.measure(1, 1)

    # 4. Measure the (un-corrected) output qubit
    qc.measure(2, 2)

    return qc


def run_teleportation(state: str, shots: int = 1024) -> Dict[str, int]:
    qc = build_teleportation_circuit(state)

    backend = Aer.get_backend("aer_simulator")
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def summarize_target_qubit(counts: Dict[str, int]) -> Dict[str, int]:
    """Return aggregated counts for the teleported qubit (qubit 2 / classical bit 2).

    We classically emulate the X correction that would be applied when the
    measurement result on qubit 0 (c0) is 1. Bitstrings are ordered as
    c2 c1 c0, so:
      - c2 corresponds to qubit 2 (the teleported state)
      - c0 (last bit) corresponds to qubit 0.
    """
    target_counts: Dict[str, int] = {"0": 0, "1": 0}
    for bitstring, count in counts.items():
        if len(bitstring) != 3:
            continue
        raw_bit = bitstring[0]  # c2
        m0 = bitstring[2]       # c0
        # If m0 == '1', an X would be applied to qubit 2, flipping its outcome.
        if m0 == "1":
            corrected_bit = "1" if raw_bit == "0" else "0"
        else:
            corrected_bit = raw_bit
        target_counts[corrected_bit] += count
    return target_counts


def print_results(state: str, counts: Dict[str, int], shots: int) -> None:
    print(f"\nTeleportation of state: |{state}> (up to global phase)")
    print("Raw 3-bit counts (c2 c1 c0):")
    print(counts)

    target_counts = summarize_target_qubit(counts)
    print("\nMarginal distribution of teleported qubit (qubit 2):")
    for bit in sorted(target_counts.keys(), reverse=True):
        cnt = target_counts[bit]
        prob = cnt / shots
        print(f"  {bit}: {cnt} / {shots} ≈ {prob:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum teleportation demo")
    parser.add_argument(
        "--state",
        type=str,
        choices=["zero", "one", "plus", "minus"],
        default="plus",
        help="State to teleport (default: plus)",
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots (>=1)")

    args = parser.parse_args()

    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    counts = run_teleportation(args.state, shots=args.shots)
    print_results(args.state, counts, args.shots)


if __name__ == "__main__":
    main()
