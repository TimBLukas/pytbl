import random
from typing import List, TypeVar

T = TypeVar('T')

def weighted_choice(items: List[T], weights: List[float]) -> T:
    """Pick one item with given probabilities"""
    if not items:
        raise ValueError("Items cannot be empty")
    if len(items) != len(weights):
        raise ValueError("Items and weights must be the same length")
        
    return random.choices(items, weights=weights, k=1)[0]

def monte_carlo_pi(num_samples: int = 1000) -> float:
    """Estimate pi using Monte Carlo simulation"""
    if num_samples <= 0:
        raise ValueError("Number of samples must be positive")
        
    inside_circle = 0
    for _ in range(num_samples):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        if x*x + y*y <= 1.0:
            inside_circle += 1
            
    return 4 * inside_circle / num_samples
