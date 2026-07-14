from typing import Dict

_FACTORIAL_CACHE: Dict[int, int] = {0: 1, 1: 1}

def factorial(n: int) -> int:
    """Compute n! (factorial) with memoisation"""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n not in _FACTORIAL_CACHE:
        _FACTORIAL_CACHE[n] = n * factorial(n - 1)
    return _FACTORIAL_CACHE[n]

def binomial(n: int, k: int) -> int:
    """Binomial coefficient C(n, k) = n! / (k! * (n-k)!)"""
    if k < 0 or k > n:
        raise ValueError("k must be between 0 and n (inclusive)")
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result

def permutations(n: int, r: int) -> int:
    """Number of permutations P(n, r) = n! / (n - r)!"""
    if r < 0 or r > n:
        raise ValueError("r must be between 0 and n (inclusive)")
    return factorial(n) // factorial(n - r)

def combinations(n: int, r: int) -> int:
    """Number of combinations, alias for binomial"""
    return binomial(n, r)
