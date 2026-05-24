#
# Basic arithmetic & Number theory
#


def factorial(n: int):
    """memoised factorial"""
    pass


def fibonacci(n: int):
    """memoised fibonacci number"""
    pass


def gcd(a, b):
    """greates common divisor"""
    pass


def lcm(a, b):
    """least common multiple"""
    pass


def is_prime(n: int):
    """primality test"""
    pass


def primes_up_to(limit: int):
    """sieve of Eraaatosthenes (cached)"""
    pass


def prime_factors(n: int):
    """dictionary of prime -> exponent"""
    pass


def divisors(n):
    """A list of all positive divisors"""
    pass


def binomial(n, k):
    """Binoial coefficient C(n,k)"""
    pass


def permutations(n, r):
    """number of permutations P(n,r)"""
    pass


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


#
# Linea Algebra
#


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


#
# Geometry
#


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
