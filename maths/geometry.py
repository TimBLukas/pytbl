import math
from typing import List, Tuple, Union

Number = Union[int, float]

Point2D = Tuple[Number, Number]
Point3D = Tuple[Number, Number, Number]


def _validate_non_negative(*values: Number) -> None:
    if any(v < 0 for v in values):
        raise ValueError("Dimensions cannot be negative")


# ---------------------------------------------------------------------
# Distance
# ---------------------------------------------------------------------

def distance(p1: Point2D, p2: Point2D) -> float:
    """Euclidean distance in 2D."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def distance_3d(p1: Point3D, p2: Point3D) -> float:
    """Euclidean distance in 3D."""
    return math.sqrt(
        (p2[0] - p1[0]) ** 2 +
        (p2[1] - p1[1]) ** 2 +
        (p2[2] - p1[2]) ** 2
    )


def midpoint(p1: Point2D, p2: Point2D) -> Point2D:
    """Midpoint of two points."""
    return (
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2,
    )


def slope(p1: Point2D, p2: Point2D) -> float:
    """Slope of the line through two points."""
    if p1[0] == p2[0]:
        raise ValueError("Vertical line has undefined slope")

    return (p2[1] - p1[1]) / (p2[0] - p1[0])


# ---------------------------------------------------------------------
# Circle
# ---------------------------------------------------------------------

def circle_area(radius: Number) -> float:
    _validate_non_negative(radius)
    return math.pi * radius ** 2


def circle_circumference(radius: Number) -> float:
    _validate_non_negative(radius)
    return 2 * math.pi * radius


# ---------------------------------------------------------------------
# Rectangle
# ---------------------------------------------------------------------

def rectangle_area(width: Number, height: Number) -> float:
    _validate_non_negative(width, height)
    return width * height


def rectangle_perimeter(width: Number, height: Number) -> float:
    _validate_non_negative(width, height)
    return 2 * (width + height)


def rectangle_diagonal(width: Number, height: Number) -> float:
    _validate_non_negative(width, height)
    return math.hypot(width, height)


# ---------------------------------------------------------------------
# Triangle
# ---------------------------------------------------------------------

def triangle_area(base: Number, height: Number) -> float:
    _validate_non_negative(base, height)
    return 0.5 * base * height


def triangle_perimeter(a: Number, b: Number, c: Number) -> float:
    _validate_non_negative(a, b, c)

    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("Invalid triangle")

    return a + b + c


def triangle_area_heron(a: Number, b: Number, c: Number) -> float:
    """Area from three sides using Heron's formula."""
    p = triangle_perimeter(a, b, c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


# ---------------------------------------------------------------------
# Sphere
# ---------------------------------------------------------------------

def sphere_volume(radius: Number) -> float:
    _validate_non_negative(radius)
    return (4 / 3) * math.pi * radius ** 3


def sphere_surface_area(radius: Number) -> float:
    _validate_non_negative(radius)
    return 4 * math.pi * radius ** 2


# ---------------------------------------------------------------------
# Cylinder
# ---------------------------------------------------------------------

def cylinder_volume(radius: Number, height: Number) -> float:
    _validate_non_negative(radius, height)
    return math.pi * radius ** 2 * height


def cylinder_surface_area(radius: Number, height: Number) -> float:
    _validate_non_negative(radius, height)
    return 2 * math.pi * radius * (radius + height)


# ---------------------------------------------------------------------
# Cone
# ---------------------------------------------------------------------

def cone_volume(radius: Number, height: Number) -> float:
    _validate_non_negative(radius, height)
    return math.pi * radius ** 2 * height / 3


def cone_surface_area(radius: Number, height: Number) -> float:
    _validate_non_negative(radius, height)
    slant = math.sqrt(radius ** 2 + height ** 2)
    return math.pi * radius * (radius + slant)


# ---------------------------------------------------------------------
# Cube
# ---------------------------------------------------------------------

def cube_volume(side: Number) -> float:
    _validate_non_negative(side)
    return side ** 3


def cube_surface_area(side: Number) -> float:
    _validate_non_negative(side)
    return 6 * side ** 2


# ---------------------------------------------------------------------
# Rectangular Prism
# ---------------------------------------------------------------------

def rectangular_prism_volume(
    length: Number,
    width: Number,
    height: Number,
) -> float:
    _validate_non_negative(length, width, height)
    return length * width * height


def rectangular_prism_surface_area(
    length: Number,
    width: Number,
    height: Number,
) -> float:
    _validate_non_negative(length, width, height)

    return 2 * (
        length * width +
        length * height +
        width * height
    )


# ---------------------------------------------------------------------
# Polygon
# ---------------------------------------------------------------------

def polygon_perimeter(points: List[Point2D]) -> float:
    """Perimeter of a closed polygon."""
    if len(points) < 3:
        raise ValueError("Polygon needs at least 3 points")

    total = 0.0

    for i in range(len(points)):
        total += distance(
            points[i],
            points[(i + 1) % len(points)]
        )

    return total


def polygon_area(points: List[Point2D]) -> float:
    """
    Area using the Shoelace formula.
    """
    if len(points) < 3:
        raise ValueError("Polygon needs at least 3 points")

    area = 0.0

    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]

        area += x1 * y2 - x2 * y1

    return abs(area) / 2