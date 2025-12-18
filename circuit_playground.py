from __future__ import annotations

import argparse
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


GATE_HELP = """Available commands (type then Enter):
  h i        - apply Hadamard on qubit i
  x i        - apply Pauli-X on qubit i
  z i        - apply Pauli-Z on qubit i
  cx c t     - apply CNOT with control c and target t
  draw       - print the circuit diagram
  run        - run the circuit on simulator and show counts
  reset      - reset circuit (keep same number of qubits)
  help       - show this help
  quit       - exit
"""


def run_circuit(qc: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
    backend = Aer.get_backend("aer_simulator")
    qc_to_run = qc.copy()
    # Ensure we measure all qubits if there are no measurements yet
    if qc_to_run.num_clbits == 0:
        qc_to_run.measure_all()
    compiled = transpile(qc_to_run, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts: Dict[str, int] = result.get_counts()
    return counts


def interactive_playground(num_qubits: int, shots: int) -> None:
    qc = QuantumCircuit(num_qubits)
    print(f"Quantum Circuit Playground - {num_qubits} qubit(s)")
    print(GATE_HELP)

    while True:
        try:
            line = input("qc> ").strip()
        except EOFError:
            print()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in {"quit", "exit"}:
            break
        elif cmd == "help":
            print(GATE_HELP)
        elif cmd == "draw":
            print(qc.draw())
        elif cmd == "reset":
            qc = QuantumCircuit(num_qubits)
            print("Circuit reset.")
        elif cmd == "h" and len(parts) == 2:
            i = int(parts[1])
            qc.h(i)
        elif cmd == "x" and len(parts) == 2:
            i = int(parts[1])
            qc.x(i)
        elif cmd == "z" and len(parts) == 2:
            i = int(parts[1])
            qc.z(i)
        elif cmd == "cx" and len(parts) == 3:
            c = int(parts[1])
            t = int(parts[2])
            qc.cx(c, t)
        elif cmd == "run":
            counts = run_circuit(qc, shots=shots)
            print(f"Ran with {shots} shots. Counts:")
            print(counts)
        else:
            print("Unrecognized command or wrong args. Type 'help' for usage.")


def demo_playground(num_qubits: int, shots: int) -> None:
    """Non-interactive demo: H on all qubits then run."""
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.h(i)
    print("Demo circuit:\n")
    print(qc.draw())
    counts = run_circuit(qc, shots=shots)
    print(f"\nRan demo with {shots} shots. Counts:")
    print(counts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum circuit playground")
    parser.add_argument("--qubits", type=int, default=2, help="Number of qubits (>=1)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots for run/demo")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["interactive", "demo"],
        default="interactive",
        help="interactive (REPL) or demo mode",
    )

    args = parser.parse_args()

    if args.qubits <= 0:
        raise SystemExit("--qubits must be >= 1")
    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    if args.mode == "interactive":
        interactive_playground(args.qubits, args.shots)
    else:
        demo_playground(args.qubits, args.shots)


if __name__ == "__main__":
    main()
