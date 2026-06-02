# -------------------------------------------
# STandard Library imports
# -------------------------------------------
import math
from typing import List, Dict, Union, Optional


# -------------------------------------------
# Private Helper functions & Chaches
# -------------------------------------------

_FACTORIAL_CACHE: Dict[int, int] = {0: 1, 1: 1}
_FIBONACCI_CACHE: Dict[int, int] = {0: 0, 1: 1}
_PRIIME_SIEVE_CACHE: Dict[int, List[int]] = {}


def _sieve_of_eratosthenes(limit: n) -> List[int]:
    """
    Generate all primes up to a limit using the Sieve of Erastosthenes

    Args:
        limit: Upper bound (inclusive)

    Returns:
        List of primes <= limit
    """
    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False

    for p in range(2, int(limit**0.5) + 1):
        if is_prime[p]:
            for multiple in range(p * p, limit + 1, p):
                is_prime[multiple] = False

    return [i for i, prime in enumerate(is_prime) if prime]


# -------------------------------------------
# Basic arithmetic & Number theory
# -------------------------------------------


def factorial(n: int) -> int:
    """
    Compute n! (factorial) with memoisation

    Args:
        n: Non-negative integer

    Returns:
        n! (factorial of n)

    Raises:
        ValueError: If n is negative

    Example:
        >>> factorial(5)
        120
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    if n not in _FACTORIAL_CACHE:
        _FACTORIAL_CACHE[n] = n * factorial(n - 1)

    return _FACTORIAL_CACHE[n]


def fibonacci(n: int) -> int:
    """
    Compute the n-th Fibonacci number (F_0 = 0, F_1 = 1) with memoisation

    Args:
        n: Non-negative integer

    Returns:
        Fibonacci number F_n

    Raises:
        ValueError: If n is negative

    Example:
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError("Fibonacci Index must be Non-negative")

    if n not in _FIBONACCI_CACHE:
        _FIBONACCI_CACHE[n] = fibonacci(n - 1) + fibonacci(n - 2)

    return _FIBONACCI_CACHE[n]


def gcd(a: int, b: int) -> int:
    """
    Greatest Common Divisor (Euclidean Algorithm)

    Args:
        a: First integer
        b: Second Integer

    Returns:
        GCD of a and b

    Example:
        >>> gcd(48, 18)
        6
    """
    # This is the Euclidean algorithm
    # if a == 0:
    #     return b

    # return gcd(b % a, a)
    # For speed an clarity the build in function is used (for implementation see comment above)
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """
    Least common multiple

    Args:
        a: First integer
        b: Second integer

    Returns:
        LCM of a and b

    Example:
        >>> lcm(12, 18)
        36
    """
    return abs(a * b) // gcd(a, b) if a and b else 0


def is_prime(n: int) -> bool:
    """
    Primality test using 6k +- 1 optimisation

    Args:
        n: Integer to test

    Returns:
        True if n is prime, False otherwise

    Example:
        >>> is_prime(17)
        True
        >>> is_prime(100)
        False
    """
    if n < 2:
        return False

    if n in (2, 3):
        return True

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False

        i += 6
    return True


def primes_up_to(limit: int) -> List[int]:
    """
    Return all primes <= limit using a cached sieve of Eratostenes.

    Args:
        limit: Upper bound (inclusive)

    Returns:
        List of primes

    Example:
        >>> primes_up_to(20)
        [2, 3, 5,  7, 11, 13, 17, 19]
    """
    if limit < 2:
        return []

    if limit not in _PRIIME_SIEVE_CACHE:
        _PRIIME_SIEVE_CACHE[limit] = _sieve_of_eratosthenes(limit)

    return _PRIIME_SIEVE_CACHE[limit]


def prime_factors(n: int) -> Dict[int, int]:
    """
    Return the prime factorisation of n as a dictionary {prime: exponent}

    Args:
        n: Integer >= 0 

    Returns:
        Dictionary mapping prime factors to their exponents

    Raises:
        ValueError: If n <= 0

    Example:
        >>> prime_factors(12)
        {2: 2, 3: 1}
    """
    if n <= 0:
        raise ValueError("Prime factorisation is defiiined only for positive Integers")

    factors = {}

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    p = 3
    while p*p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p

        p += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def divisors(n: int) -> List[int]:
    """
    Return all positive divisors of n, sorted in ascending order

    Args:
        n: Positive integer

    Returns:
        List of divisors

    Raises:
        ValueError("n must to be > 0")

    Example:
        >>> divisors(12)
        [1, 2, 3, 4, 6, 12]
    """
    if n <= 0:
        raise ValueError("n must be positive")
    divisors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)

    return sorted(divisors)


def binomial(n: int, k: int) -> int:
    """
    Binomial coefficient C(n, k) = n! / (k! * (n-k)!)

    Args:
        n: Total number of items
        k: Number of chosen items

    Returns:
        Binomial coefficient

    Raises:
        ValueError: If k < 0 or k > n

    Example:
        >>> binomial(5, 2)
        10
    """
    if k < 0 or k > n:
        raise ValueError("k must be between 0 and n (inclusive")

    k = min(k, n - k)
    result = 1

    for i in range(1, k + 1):
        result = result * (n - k + i) // i

    return result


def permutations(n: int, r: int) -> int:
    """
    Number of permutations P(n, r) = n! / (n - r)!

    Args:
        n: total number of items
        r: Number of items to arrange

    Returns:
        Number of permutations

    Raises:
        ValueError: if r < 0 or r > n

    Example:
        >>> permutations(5, 2)
        20
    """
    if r < 0 or r > n:
        raise ValueError("r must be between 0 and n (inclusive)")
    return factorial(n) // factorial(n - r)


def combinations(n, r):
    """alias for binomial"""
    pass


#
# Statistics
#


def mean(data):
    """arithmetic mean"""
    pass


def median(data):
    """median"""
    pass


def mode(data):
    """A list of common values"""
    pass


def variance(data, sample=True):
    """varaince (population or sample)"""
    pass


def stddev(data, sample=True):
    """standard deviation"""
    pass


def correlation(x, y):
    """Pearson correlation coefficient"""
    pass


# -------------------------------------------
# Linea Algebra
# -------------------------------------------


def dot_product(v1, v2):
    """vector dot product"""
    pass


def vector_add(v1, v2):
    """element-wise addition"""
    pass


def vector_sub(v1, v2):
    """elment-wise subtraction"""
    pass


def scalar_mul(v1, v2):
    """multiply vector by scalar"""
    pass


def norm(v, order=2):
    """LP norm (1=Manhatten, 2=Euclidean)"""
    pass


def matrix_multiply(A, B):
    """matrix mulitplication"""
    pass


def transpose(matrix):
    """matrix transpose"""
    pass


def identity(n):
    """identity matrix"""
    pass


def determinant_2x2(m):
    """determinant for 2x2 matrices"""
    pass


# -------------------------------------------
# Geometry
# -------------------------------------------


def distance(p1, p2):
    """Euclidean distance (2D)"""
    pass


def circle_area(radius):
    """Area of a circle by its radius"""
    pass


def circle_circumference(radius):
    """circumference of a circle by its radius"""
    pass


def rectange_area(width, height):
    """area of a rectangle by its width and height"""
    pass


def triangle_area(base, height):
    """area of a triangle by its base and height"""
    pass


#
# Random simulation
#


def weighted_choice(items, weights):
    """pick one item with given probabilities"""
    pass


def monte_carlo_pi(num_samples=1000):
    """estimate pi"""
    pass


#
# file i/o
#


def write_matrix(path, matrix, fmt="json"):
    """export matrix to json or csv"""
    pass


def read_matrix(path, fmt="json"):
    """import matrix from json or csv"""
    pass

