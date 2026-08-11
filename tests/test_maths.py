"""Tests for the maths package."""

import csv
import json
import math
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from maths import algebra, combinatorics, geometry, io, number_theory, simulation, statistics


class TestCombinatorics(unittest.TestCase):
    """Cover combinatorics helpers."""

    def test_factorial_and_combinations(self) -> None:
        self.assertEqual(combinatorics.factorial(0), 1)
        self.assertEqual(combinatorics.factorial(5), 120)
        self.assertEqual(combinatorics.binomial(5, 2), 10)
        self.assertEqual(combinatorics.permutations(5, 2), 20)
        self.assertEqual(combinatorics.combinations(6, 3), 20)

    def test_combinatorics_errors(self) -> None:
        with self.assertRaises(ValueError):
            combinatorics.factorial(-1)
        with self.assertRaises(ValueError):
            combinatorics.binomial(3, 4)
        with self.assertRaises(ValueError):
            combinatorics.permutations(3, 4)


class TestNumberTheory(unittest.TestCase):
    """Cover number theory helpers."""

    def test_number_theory_basics(self) -> None:
        self.assertEqual(number_theory.fibonacci(10), 55)
        self.assertEqual(number_theory.gcd(24, 18), 6)
        self.assertEqual(number_theory.lcm(12, 18), 36)
        self.assertTrue(number_theory.is_prime(29))
        self.assertFalse(number_theory.is_prime(30))
        self.assertEqual(number_theory.primes_up_to(10), [2, 3, 5, 7])
        self.assertEqual(number_theory.prime_factors(84), {2: 2, 3: 1, 7: 1})
        self.assertEqual(number_theory.divisors(12), [1, 2, 3, 4, 6, 12])

    def test_number_theory_errors(self) -> None:
        with self.assertRaises(ValueError):
            number_theory.fibonacci(-1)
        with self.assertRaises(ValueError):
            number_theory.prime_factors(0)
        with self.assertRaises(ValueError):
            number_theory.divisors(0)


class TestAlgebra(unittest.TestCase):
    """Cover vector and matrix helpers."""

    def test_vector_and_matrix_operations(self) -> None:
        self.assertEqual(algebra.dot_product([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(algebra.vector_add([1, 2], [3, 4]), [4, 6])
        self.assertEqual(algebra.vector_sub([5, 7], [2, 3]), [3, 4])
        self.assertEqual(algebra.scalar_mul([1, 2], 3), [3, 6])
        self.assertAlmostEqual(algebra.norm([3, 4]), 5.0)
        self.assertAlmostEqual(algebra.norm([1, 2, 2]), 3.0, places=7)
        self.assertEqual(algebra.matrix_multiply([[1, 2]], [[3], [4]]), [[11]])
        self.assertEqual(algebra.transpose([[1, 2], [3, 4]]), [[1, 3], [2, 4]])
        self.assertEqual(algebra.identity(2), [[1.0, 0.0], [0.0, 1.0]])
        self.assertEqual(algebra.determinant_2x2([[1, 2], [3, 4]]), -2)
        self.assertEqual(algebra.cross_product([1, 0, 0], [0, 1, 0]), [0, 0, 1])
        self.assertEqual(algebra.matrix_add([[1, 2]], [[3, 4]]), [[4, 6]])
        self.assertEqual(algebra.matrix_sub([[5, 7]], [[2, 3]]), [[3, 4]])
        self.assertEqual(algebra.trace([[1, 2], [3, 4]]), 5)

    def test_algebra_errors(self) -> None:
        with self.assertRaises(ValueError):
            algebra.dot_product([1], [1, 2])
        with self.assertRaises(ValueError):
            algebra.matrix_multiply([[1, 2]], [[1, 2]])
        with self.assertRaises(ValueError):
            algebra.determinant_2x2([[1, 2, 3], [4, 5, 6]])
        with self.assertRaises(ValueError):
            algebra.cross_product([1, 2], [3, 4])


class TestStatistics(unittest.TestCase):
    """Cover statistical helpers."""

    def test_descriptive_statistics(self) -> None:
        data = [1, 2, 2, 3, 4]
        self.assertEqual(statistics.mean(data), 2.4)
        self.assertEqual(statistics.weighted_mean([1, 2, 3], [1, 1, 2]), 2.25)
        self.assertEqual(statistics.median(data), 2.0)
        self.assertEqual(statistics.mode(data), [2])
        self.assertEqual(statistics.minimum(data), 1)
        self.assertEqual(statistics.maximum(data), 4)
        self.assertEqual(statistics.data_range(data), 3)
        self.assertAlmostEqual(statistics.variance([1, 2, 3], sample=False), 2 / 3)
        self.assertAlmostEqual(statistics.stddev([1, 2, 3], sample=False), math.sqrt(2 / 3))
        self.assertAlmostEqual(statistics.covariance([1, 2, 3], [1, 2, 3], sample=False), 2 / 3)
        self.assertAlmostEqual(statistics.correlation([1, 2, 3], [1, 2, 3]), 1.0)
        self.assertAlmostEqual(statistics.geometric_mean([1, 4]), 2.0)
        self.assertAlmostEqual(statistics.harmonic_mean([1, 2, 4]), 12 / 7)
        self.assertEqual(statistics.percentile([1, 2, 3, 4], 50), 2.5)
        self.assertEqual(statistics.quartiles([1, 2, 3, 4]), (1.75, 2.5, 3.25))
        self.assertEqual(statistics.interquartile_range([1, 2, 3, 4]), 1.5)
        self.assertAlmostEqual(statistics.coefficient_of_variation([1, 2, 3], sample=False), math.sqrt(2 / 3) / 2)
        self.assertAlmostEqual(statistics.z_score(3, [1, 2, 3]), 1.0)

    def test_statistics_errors(self) -> None:
        with self.assertRaises(ValueError):
            statistics.mean([])
        with self.assertRaises(ValueError):
            statistics.weighted_mean([1], [0])
        with self.assertRaises(ValueError):
            statistics.percentile([1, 2], 200)
        with self.assertRaises(ValueError):
            statistics.correlation([1], [1])


class TestGeometry(unittest.TestCase):
    """Cover geometry helpers."""

    def test_geometry_formulas(self) -> None:
        self.assertAlmostEqual(geometry.distance((0, 0), (3, 4)), 5.0)
        self.assertAlmostEqual(geometry.distance_3d((0, 0, 0), (1, 2, 2)), 3.0)
        self.assertEqual(geometry.midpoint((0, 0), (2, 4)), (1.0, 2.0))
        self.assertEqual(geometry.slope((0, 0), (2, 4)), 2.0)
        self.assertAlmostEqual(geometry.circle_area(2), math.pi * 4)
        self.assertAlmostEqual(geometry.circle_circumference(2), 4 * math.pi)
        self.assertEqual(geometry.rectangle_area(3, 4), 12)
        self.assertEqual(geometry.rectangle_perimeter(3, 4), 14)
        self.assertAlmostEqual(geometry.rectangle_diagonal(3, 4), 5.0)
        self.assertEqual(geometry.triangle_area(3, 4), 6.0)
        self.assertEqual(geometry.triangle_perimeter(3, 4, 5), 12)
        self.assertAlmostEqual(geometry.triangle_area_heron(3, 4, 5), 6.0)
        self.assertAlmostEqual(geometry.sphere_volume(1), 4 / 3 * math.pi)
        self.assertAlmostEqual(geometry.sphere_surface_area(1), 4 * math.pi)
        self.assertAlmostEqual(geometry.cylinder_volume(1, 2), 2 * math.pi)
        self.assertAlmostEqual(geometry.cylinder_surface_area(1, 2), 6 * math.pi)
        self.assertAlmostEqual(geometry.cone_volume(1, 3), math.pi)
        self.assertAlmostEqual(geometry.cube_volume(3), 27)
        self.assertAlmostEqual(geometry.cube_surface_area(3), 54)
        self.assertEqual(geometry.rectangular_prism_volume(2, 3, 4), 24)
        self.assertEqual(geometry.rectangular_prism_surface_area(2, 3, 4), 52)
        self.assertAlmostEqual(geometry.polygon_perimeter([(0, 0), (4, 0), (4, 3)]), 12.0)
        self.assertEqual(geometry.polygon_area([(0, 0), (4, 0), (4, 3)]), 6.0)

    def test_geometry_errors(self) -> None:
        with self.assertRaises(ValueError):
            geometry.slope((1, 1), (1, 4))
        with self.assertRaises(ValueError):
            geometry.triangle_perimeter(1, 2, 3)
        with self.assertRaises(ValueError):
            geometry.circle_area(-1)
        with self.assertRaises(ValueError):
            geometry.polygon_area([(0, 0), (1, 1)])


class TestSimulation(unittest.TestCase):
    """Cover simulation helpers."""

    def test_weighted_choice_and_monte_carlo(self) -> None:
        with patch.object(random, "choices", return_value=["b"]) as mocked:
            self.assertEqual(simulation.weighted_choice(["a", "b"], [1.0, 2.0]), "b")
            mocked.assert_called_once()

        with patch.object(random, "uniform", side_effect=[0.0, 0.0, 1.0, 1.0]):
            self.assertEqual(simulation.monte_carlo_pi(2), 2.0)

    def test_simulation_errors(self) -> None:
        with self.assertRaises(ValueError):
            simulation.weighted_choice([], [])
        with self.assertRaises(ValueError):
            simulation.weighted_choice(["a"], [])
        with self.assertRaises(ValueError):
            simulation.monte_carlo_pi(0)


class TestMatrixIO(unittest.TestCase):
    """Cover matrix import and export helpers."""

    def test_matrix_io_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            matrix = [[1, 2], [3, 4]]

            json_path = root / "matrix.json"
            csv_path = root / "matrix.csv"

            io.write_matrix(str(json_path), matrix, fmt="json")
            io.write_matrix(str(csv_path), matrix, fmt="csv")

            self.assertEqual(io.read_matrix(str(json_path), fmt="json"), matrix)
            self.assertEqual(io.read_matrix(str(csv_path), fmt="csv"), matrix)

            with self.assertRaises(ValueError):
                io.write_matrix(str(root / "bad.txt"), matrix, fmt="txt")
            with self.assertRaises(ValueError):
                io.read_matrix(str(root / "bad.txt"), fmt="txt")
