import math
from collections import Counter
from typing import List, Tuple, Union

Number = Union[int, float]


def _validate_non_empty(data: List[Number]) -> None:
    if not data:
        raise ValueError("data must not be empty")


def mean(data: List[Number]) -> float:
    """Arithmetic mean."""
    _validate_non_empty(data)
    return sum(data) / len(data)


def weighted_mean(values: List[Number], weights: List[Number]) -> float:
    """Weighted arithmetic mean."""
    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    if not values:
        raise ValueError("values must not be empty")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("sum of weights must not be zero")

    return sum(v * w for v, w in zip(values, weights)) / total_weight


def median(data: List[Number]) -> float:
    """Median."""
    _validate_non_empty(data)

    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2

    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2

    return float(sorted_data[mid])


def mode(data: List[Number]) -> List[Number]:
    """
    Mode(s).

    Returns an empty list if there is no mode
    (i.e. every value occurs exactly once).
    """
    _validate_non_empty(data)

    counts = Counter(data)
    max_count = max(counts.values())

    if max_count == 1:
        return []

    return sorted([k for k, v in counts.items() if v == max_count])


def minimum(data: List[Number]) -> Number:
    """Minimum value."""
    _validate_non_empty(data)
    return min(data)


def maximum(data: List[Number]) -> Number:
    """Maximum value."""
    _validate_non_empty(data)
    return max(data)


def data_range(data: List[Number]) -> Number:
    """Range (max - min)."""
    _validate_non_empty(data)
    return max(data) - min(data)


def variance(data: List[Number], sample: bool = True) -> float:
    """Variance."""
    n = len(data)

    if sample:
        if n < 2:
            raise ValueError("sample variance requires at least 2 data points")
        divisor = n - 1
    else:
        if n < 1:
            raise ValueError("population variance requires at least 1 data point")
        divisor = n

    mu = mean(data)
    return sum((x - mu) ** 2 for x in data) / divisor


def stddev(data: List[Number], sample: bool = True) -> float:
    """Standard deviation."""
    return math.sqrt(variance(data, sample))


def covariance(
    x: List[Number],
    y: List[Number],
    sample: bool = True,
) -> float:
    """Covariance."""
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    n = len(x)

    if sample:
        if n < 2:
            raise ValueError("sample covariance requires at least 2 points")
        divisor = n - 1
    else:
        if n < 1:
            raise ValueError("population covariance requires at least 1 point")
        divisor = n

    mx = mean(x)
    my = mean(y)

    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / divisor


def correlation(x: List[Number], y: List[Number]) -> float:
    """Pearson correlation coefficient."""
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    if len(x) < 2:
        raise ValueError("correlation requires at least 2 data points")

    sx = stddev(x)
    sy = stddev(y)

    if sx == 0 or sy == 0:
        raise ValueError(
            "correlation is undefined when one variable is constant"
        )

    return covariance(x, y) / (sx * sy)


def geometric_mean(data: List[Number]) -> float:
    """Geometric mean."""
    _validate_non_empty(data)

    if any(x <= 0 for x in data):
        raise ValueError("geometric mean requires all values to be positive")

    product = math.prod(data)
    return product ** (1 / len(data))


def harmonic_mean(data: List[Number]) -> float:
    """Harmonic mean."""
    _validate_non_empty(data)

    if any(x <= 0 for x in data):
        raise ValueError("harmonic mean requires all values to be positive")

    return len(data) / sum(1 / x for x in data)


def percentile(data: List[Number], p: float) -> float:
    """
    Linear-interpolated percentile.

    p must be in [0, 100].
    """
    _validate_non_empty(data)

    if not 0 <= p <= 100:
        raise ValueError("percentile must be between 0 and 100")

    values = sorted(data)

    if len(values) == 1:
        return float(values[0])

    pos = (len(values) - 1) * (p / 100)
    lower = math.floor(pos)
    upper = math.ceil(pos)

    if lower == upper:
        return float(values[lower])

    weight = pos - lower

    return (
        values[lower] * (1 - weight)
        + values[upper] * weight
    )


def quartiles(data: List[Number]) -> Tuple[float, float, float]:
    """Returns (Q1, Q2, Q3)."""
    return (
        percentile(data, 25),
        percentile(data, 50),
        percentile(data, 75),
    )


def interquartile_range(data: List[Number]) -> float:
    """Interquartile range (IQR)."""
    q1, _, q3 = quartiles(data)
    return q3 - q1


def coefficient_of_variation(
    data: List[Number],
    sample: bool = True,
) -> float:
    """Coefficient of variation."""
    mu = mean(data)

    if mu == 0:
        raise ValueError("mean must not be zero")

    return stddev(data, sample) / mu


def z_score(x: Number, data: List[Number]) -> float:
    """Z-score of a value relative to a dataset."""
    s = stddev(data)

    if s == 0:
        raise ValueError("standard deviation must not be zero")

    return (x - mean(data)) / s