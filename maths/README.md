# `maths`

Small, dependency-free helpers for number theory, combinatorics, descriptive
statistics, vectors and matrices, geometry, simulations, and matrix I/O.

```python
from maths import combinations, distance, mean, primes_up_to

print(combinations(5, 2))
print(mean([10, 20, 30]))
print(distance((0, 0), (3, 4)))
print(primes_up_to(15))
```

Inputs are validated by each function. The submodules (`algebra`,
`statistics`, `geometry`, and others) can be imported directly when a more
focused namespace is clearer.
