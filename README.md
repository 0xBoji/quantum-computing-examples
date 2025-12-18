# Quantum Coding Playground

A small collection of hands-on quantum computing examples using Python and Qiskit. The goal is to build intuition for core quantum concepts by actually running circuits, not just reading theory.

## Quick start: unified CLI

All demos can be run through a single entry point:

```bash
cd /Volumes/0xbojissd/quantumn-science
source qenv/bin/activate
python3 quantum_lab.py --mode hello --shots 512
```

Supported `--mode` values:

- `hello`
- `coin`
- `grover`
- `bell`
- `playground`
- `teleport`
- `deutsch_jozsa`
- `bernstein_vazirani`
- `vqe`

Run with `-h`/`--help` for details on additional flags (qubits, targets, states, etc.).

## Prerequisites

- Python 3.13 (or a compatible 3.x installation)
- Qiskit and Qiskit Aer (installed inside the local `qenv` virtual environment)

### Setup (first time)

```bash
cd /Volumes/0xbojissd/quantumn-science
python3 -m venv qenv
source qenv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install qiskit 'qiskit[visualization]' qiskit-aer
```

### Activate environment (every time)

```bash
cd /Volumes/0xbojissd/quantumn-science
source qenv/bin/activate
```

---

## Scripts Overview

### 1. `hello_quantum.py`

**Concept:** Single-qubit superposition with the Hadamard gate.

```bash
python3 hello_quantum.py
```

Measurement results are typically close to 50% `0` and 50% `1`.

---

### 2. `quantum_coin.py`

**Concept:** Quantum coin / dice using multiple qubits in superposition.

```bash
# 1-qubit coin (2 outcomes)
python3 quantum_coin.py --qubits 1 --shots 1000

# 2-qubit "dice" (4 outcomes: 00, 01, 10, 11)
python3 quantum_coin.py --qubits 2 --shots 1000
```

This shows how measurement distributions change with qubit count and number of shots.

---

### 3. `baby_grover.py`

**Concept:** Tiny Grover search on 2 qubits (4 states). One marked state gets its amplitude boosted.

```bash
# Search for target state 11
python3 baby_grover.py --target 11 --shots 1000

# Try other targets: 00, 01, or 10
python3 baby_grover.py --target 01 --shots 1000
```

The marked target should dominate the measurement statistics.

---

### 4. `bell_state_lab.py`

**Concept:** Entanglement vs non-entangled product states.

```bash
# Run both circuits for comparison
python3 bell_state_lab.py --mode both --shots 1000

# Only Bell state
python3 bell_state_lab.py --mode bell --shots 1000

# Only product H⊗H state
python3 bell_state_lab.py --mode product --shots 1000
```

- Bell state: results concentrate on `00` and `11`.
- Product H⊗H: all four states appear with roughly equal probability.

---

### 5. `circuit_playground.py`

**Concept:** Interactive REPL to build and run quantum circuits from the command line.

```bash
# Interactive mode
python3 circuit_playground.py --mode interactive --qubits 2 --shots 1024
```

Available commands inside the REPL:

- `h i` &mdash; apply Hadamard on qubit `i`
- `x i` &mdash; apply Pauli-X on qubit `i`
- `z i` &mdash; apply Pauli-Z on qubit `i`
- `cx c t` &mdash; apply CNOT (control `c`, target `t`)
- `draw` &mdash; print the circuit diagram
- `run` &mdash; run on the simulator and show counts
- `reset` &mdash; reset the circuit (same qubit count)
- `help` &mdash; show the help menu
- `quit` &mdash; exit the playground

You can also run a simple demo:

```bash
python3 circuit_playground.py --mode demo --qubits 2 --shots 512
```

---

### 6. `teleportation_demo.py`

**Concept:** Quantum teleportation of a single-qubit state using a 3-qubit circuit and Bell pair.

Supported input states:

- `zero`  &rarr; \|0⟩
- `one`   &rarr; \|1⟩
- `plus`  &rarr; (\|0⟩ + \|1⟩)/√2
- `minus` &rarr; (\|0⟩ − \|1⟩)/√2

Example usage:

```bash
python3 teleportation_demo.py --state plus --shots 1024
python3 teleportation_demo.py --state one --shots 1024
```

The script prints full 3-bit measurement results and the marginal distribution of the teleported qubit (after classical correction in post-processing).

---

### 7. `deutsch_jozsa.py`

**Concept:** Deutsch–Jozsa algorithm on a small number of input qubits.

```bash
# Run via the dedicated script
python3 deutsch_jozsa.py --n 2 --oracle balanced_parity --shots 1024

# Or via the unified CLI
python3 quantum_lab.py --mode deutsch_jozsa --dj-n 2 --dj-oracle balanced_parity --shots 1024
```

The output includes raw counts over the input register and a classification of the oracle as `constant` or `balanced`.

---

### 8. `bernstein_vazirani.py`

**Concept:** Bernstein–Vazirani algorithm to recover a hidden bitstring with a single query.

```bash
# Run via the dedicated script
python3 bernstein_vazirani.py --secret 1011 --shots 1024

# Or via the unified CLI
python3 quantum_lab.py --mode bernstein_vazirani --bv-secret 1011 --shots 1024
```

The output shows raw counts over the input register and confirms whether the recovered bitstring matches the configured secret.

---

### 10. `vqe_demo.py`

**Concept:** Variational Quantum Eigensolver (VQE) to estimate the ground state energy of the H2 molecule.

```bash
# Run via the dedicated script
python3 vqe_demo.py --shots 1024

# Or via the unified CLI
python3 quantum_lab.py --mode vqe --shots 1024
```

The output shows the estimated ground state energy (in Hartree) and compares it to the known exact value.

---

### 9. `statevector_demo.py`

**Concept:** Inspect quantum statevectors (amplitudes and probabilities) before measurement.

```bash
# Run all demos
python3 statevector_demo.py --demo all

# Run specific demo
python3 statevector_demo.py --demo bell
python3 statevector_demo.py --demo grover
```

The output displays complex amplitudes and probabilities for each basis state, useful for debugging quantum algorithms.

---

## Testing

The project includes probabilistic unit tests in `tests/test_quantum_demos.py`.

Run tests with pytest:

```bash
# Install pytest (if not already installed)
python3 -m pip install pytest

# Run all tests
python3 -m pytest tests/ -v
```

Tests validate:
- Correct count sums
- Expected probability distributions (with statistical thresholds)
- Algorithm-specific behavior (e.g., Grover target dominance, DJ classification)

---

## Contributing

This project is intentionally small and focused on being a practical learning lab.
If you would like to contribute:

- Open an issue with a short description of the concept or algorithm you want to add.
- Keep new examples minimal and runnable from the command line.
- Prefer clear, well-commented circuits over heavy abstraction.

Examples of great contributions:

- New small algorithms (e.g. Deutsch–Jozsa, Bernstein–Vazirani, simple QPE).
- Additional educational demos (more entanglement patterns, simple VQE examples).
- Improvements to the interactive playground or unified CLI.

## Notes

- The `.gitignore` is configured to exclude Python bytecode, virtual environments (including `qenv/`), and common editor/system files.
- All scripts use the local Aer simulator via `qiskit_aer`. No access to real hardware is required.
