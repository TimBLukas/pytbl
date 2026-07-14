import math
from typing import List, Dict

_FIBONACCI_CACHE: Dict[int, int] = {0: 0, 1: 1}
_PRIIME_SIEVE_CACHE: Dict[int, List[int]] = {}

def _sieve_of_eratosthenes(limit: int) -> List[int]:
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(limit**0.5) + 1):
        if is_prime[p]:
            for multiple in range(p * p, limit + 1, p):
                is_prime[multiple] = False
    return [i for i, prime in enumerate(is_prime) if prime]

def fibonacci(n: int) -> int:
    """Compute the n-th Fibonacci number with memoisation"""
    if n < 0:
        raise ValueError("Fibonacci Index must be Non-negative")
    if n not in _FIBONACCI_CACHE:
        _FIBONACCI_CACHE[n] = fibonacci(n - 1) + fibonacci(n - 2)
    return _FIBONACCI_CACHE[n]

def gcd(a: int, b: int) -> int:
    """Greatest Common Divisor (Euclidean Algorithm)"""
    return math.gcd(a, b)

def lcm(a: int, b: int) -> int:
    """Least common multiple"""
    return abs(a * b) // gcd(a, b) if a and b else 0

def is_prime(n: int) -> bool:
    """Primality test using 6k +- 1 optimisation"""
    if n < 2: return False
    if n in (2, 3): return True
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def primes_up_to(limit: int) -> List[int]:
    """Return all primes <= limit using a cached sieve."""
    if limit < 2: return []
    if limit not in _PRIIME_SIEVE_CACHE:
        _PRIIME_SIEVE_CACHE[limit] = _sieve_of_eratosthenes(limit)
    return _PRIIME_SIEVE_CACHE[limit]

def prime_factors(n: int) -> Dict[int, int]:
    """Return the prime factorisation of n as {prime: exponent}"""
    if n <= 0: raise ValueError("Prime factorisation is defined only for positive Integers")
    factors = {}
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
    p = 3
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def divisors(n: int) -> List[int]:
    """Return all positive divisors of n, sorted in ascending order"""
    if n <= 0: raise ValueError("n must be positive")
    divisors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return sorted(divisors)
