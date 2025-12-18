"""
Unit tests for quantum demos with probabilistic validation.

Since quantum measurements are probabilistic, tests use statistical thresholds
rather than exact value matching.
"""

from hello_quantum import run_hello
from quantum_coin import run_quantum_coin
from baby_grover import run_baby_grover_2_qubits
from deutsch_jozsa import run_deutsch_jozsa, classify_deutsch_jozsa
from bernstein_vazirani import run_bernstein_vazirani


def test_hello_quantum_sum():
    """Test that hello_quantum returns counts that sum to shots."""
    shots = 100
    counts = run_hello(shots=shots)
    total = sum(counts.values())
    assert total == shots, f"Expected total {shots}, got {total}"


def test_hello_quantum_distribution():
    """Test that hello_quantum produces roughly 50/50 distribution."""
    shots = 1000
    counts = run_hello(shots=shots)
    
    # Allow 40-60% for each outcome (generous threshold for statistical fluctuation)
    count_0 = counts.get("0", 0)
    count_1 = counts.get("1", 0)
    
    prob_0 = count_0 / shots
    prob_1 = count_1 / shots
    
    assert 0.4 <= prob_0 <= 0.6, f"Probability of '0' is {prob_0:.3f}, expected ~0.5"
    assert 0.4 <= prob_1 <= 0.6, f"Probability of '1' is {prob_1:.3f}, expected ~0.5"


def test_quantum_coin_sum():
    """Test that quantum_coin returns counts summing to shots."""
    shots = 100
    counts = run_quantum_coin(num_qubits=2, shots=shots)
    total = sum(counts.values())
    assert total == shots, f"Expected total {shots}, got {total}"


def test_quantum_coin_outcomes():
    """Test that quantum_coin produces all expected 2-qubit outcomes."""
    shots = 500
    counts = run_quantum_coin(num_qubits=2, shots=shots)
    
    # All 4 outcomes should appear with reasonable probability
    expected_outcomes = {"00", "01", "10", "11"}
    observed_outcomes = set(counts.keys())
    
    assert expected_outcomes == observed_outcomes, \
        f"Expected outcomes {expected_outcomes}, got {observed_outcomes}"


def test_baby_grover_target_dominance():
    """Test that Grover's algorithm significantly boosts target state probability."""
    shots = 1000
    target = "11"
    counts = run_baby_grover_2_qubits(target=target, shots=shots)
    
    target_count = counts.get(target, 0)
    target_prob = target_count / shots
    
    # Target should dominate: expect > 80% probability
    assert target_prob > 0.8, \
        f"Target '{target}' probability is {target_prob:.3f}, expected > 0.8"


def test_deutsch_jozsa_constant():
    """Test that Deutsch–Jozsa correctly identifies constant oracles."""
    shots = 500
    counts = run_deutsch_jozsa(n=2, oracle_type="constant_zero", shots=shots)
    classification = classify_deutsch_jozsa(counts, n=2)
    
    assert classification == "constant", \
        f"Expected 'constant', got '{classification}'"


def test_deutsch_jozsa_balanced():
    """Test that Deutsch–Jozsa correctly identifies balanced oracles."""
    shots = 500
    counts = run_deutsch_jozsa(n=2, oracle_type="balanced_parity", shots=shots)
    classification = classify_deutsch_jozsa(counts, n=2)
    
    assert classification == "balanced", \
        f"Expected 'balanced', got '{classification}'"


def test_bernstein_vazirani_recovery():
    """Test that Bernstein–Vazirani recovers the secret bitstring."""
    shots = 500
    secret = "1011"
    counts = run_bernstein_vazirani(secret=secret, shots=shots)
    
    # Most frequent outcome should be the secret
    if counts:
        recovered = max(counts.items(), key=lambda item: item[1])[0]
    else:
        recovered = ""
    
    assert recovered == secret, \
        f"Expected to recover '{secret}', got '{recovered}'"


def test_bernstein_vazirani_high_confidence():
    """Test that BV algorithm has high confidence in the recovered secret."""
    shots = 1000
    secret = "101"
    counts = run_bernstein_vazirani(secret=secret, shots=shots)
    
    secret_count = counts.get(secret, 0)
    secret_prob = secret_count / shots
    
    # Expect > 90% confidence in the secret
    assert secret_prob > 0.9, \
        f"Secret '{secret}' probability is {secret_prob:.3f}, expected > 0.9"
