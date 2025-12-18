from __future__ import annotations

import argparse

from hello_quantum import run_hello
from quantum_coin import run_quantum_coin, print_counts_and_probabilities as print_coin_counts
from baby_grover import run_baby_grover_2_qubits, print_counts_and_probabilities as print_grover_counts
from bell_state_lab import (
    run_bell_state,
    run_product_superposition,
    print_counts_and_probabilities as print_bell_counts,
)
from circuit_playground import interactive_playground, demo_playground
from teleportation_demo import run_teleportation, print_results as print_teleportation_results
from deutsch_jozsa import run_deutsch_jozsa, print_dj_results


MODES = ["hello", "coin", "grover", "bell", "playground", "teleport", "deutsch_jozsa"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified CLI for the Quantum Coding Playground examples",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=MODES,
        required=True,
        help="Which demo to run: one of " + ", ".join(MODES),
    )
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots for simulations (>=1)")

    # Extra parameters for specific modes
    parser.add_argument("--qubits", type=int, default=2, help="Number of qubits (for coin/playground modes)")
    parser.add_argument("--target", type=str, default="11", help="Target bitstring for Grover (2 bits)")
    parser.add_argument(
        "--dj-n",
        type=int,
        default=2,
        help="Number of input qubits for Deutsch–Jozsa",
    )
    parser.add_argument(
        "--dj-oracle",
        type=str,
        choices=["constant_zero", "constant_one", "balanced_first", "balanced_parity"],
        default="balanced_parity",
        help="Oracle type for Deutsch–Jozsa demo",
    )
    parser.add_argument(
        "--bell-mode",
        type=str,
        choices=["both", "bell", "product"],
        default="both",
        help="Which Bell lab circuit(s) to run",
    )
    parser.add_argument(
        "--playground-mode",
        type=str,
        choices=["interactive", "demo"],
        default="interactive",
        help="Playground mode: interactive REPL or demo",
    )
    parser.add_argument(
        "--state",
        type=str,
        choices=["zero", "one", "plus", "minus"],
        default="plus",
        help="State to teleport in teleportation demo",
    )

    args = parser.parse_args()

    if args.shots <= 0:
        raise SystemExit("--shots must be >= 1")

    if args.mode == "hello":
        counts = run_hello(shots=args.shots)
        print("\n[hello_quantum] Single-qubit Hadamard demo")
        print("Measurement results (counts per state):")
        print(counts)

    elif args.mode == "coin":
        if args.qubits <= 0:
            raise SystemExit("--qubits must be >= 1 for coin mode")
        counts = run_quantum_coin(num_qubits=args.qubits, shots=args.shots)
        print(f"\n[quantum_coin] Quantum coin/dice with {args.qubits} qubit(s)")
        print_coin_counts(counts, args.shots)

    elif args.mode == "grover":
        if len(args.target) != 2 or any(bit not in {"0", "1"} for bit in args.target):
            raise SystemExit("--target must be one of: 00, 01, 10, 11")
        counts = run_baby_grover_2_qubits(target=args.target, shots=args.shots)
        print(f"\n[baby_grover] 2-qubit Grover for target: {args.target}")
        print_grover_counts(counts, args.shots, highlight=args.target)

    elif args.mode == "bell":
        if args.bell_mode in ("bell", "both"):
            bell_counts = run_bell_state(shots=args.shots)
            print_bell_counts("Bell state (entangled)", bell_counts, args.shots)
        if args.bell_mode in ("product", "both"):
            product_counts = run_product_superposition(shots=args.shots)
            print_bell_counts("Product H⊗H state (not entangled)", product_counts, args.shots)

    elif args.mode == "playground":
        if args.qubits <= 0:
            raise SystemExit("--qubits must be >= 1 for playground mode")
        if args.playground_mode == "interactive":
            interactive_playground(args.qubits, args.shots)
        else:
            demo_playground(args.qubits, args.shots)

    elif args.mode == "teleport":
        counts = run_teleportation(args.state, shots=args.shots)
        print_teleportation_results(args.state, counts, args.shots)

    elif args.mode == "deutsch_jozsa":
        if args.dj_n <= 0:
            raise SystemExit("--dj-n must be >= 1 for Deutsch–Jozsa mode")
        counts = run_deutsch_jozsa(n=args.dj_n, oracle_type=args.dj_oracle, shots=args.shots)
        print_dj_results(counts, args.dj_n, args.dj_oracle, args.shots)


if __name__ == "__main__":
    main()
