import math
from typing import List, Union

Vector = List[Union[int, float]]
Matrix = List[List[Union[int, float]]]

def dot_product(v1: Vector, v2: Vector) -> float:
    """Vector dot product"""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return sum(a * b for a, b in zip(v1, v2))

def vector_add(v1: Vector, v2: Vector) -> Vector:
    """Element-wise addition"""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return [a + b for a, b in zip(v1, v2)]

def vector_sub(v1: Vector, v2: Vector) -> Vector:
    """Element-wise subtraction"""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return [a - b for a, b in zip(v1, v2)]

def scalar_mul(v: Vector, s: Union[int, float]) -> Vector:
    """Multiply vector by scalar"""
    return [a * s for a in v]

def norm(v: Vector, order: int = 2) -> float:
    """Lp norm (1=Manhattan, 2=Euclidean)"""
    if order == 1:
        return sum(abs(x) for x in v)
    elif order == 2:
        return math.sqrt(sum(x * x for x in v))
    else:
        return sum(abs(x) ** order for x in v) ** (1 / order)

def matrix_multiply(A: Matrix, B: Matrix) -> Matrix:
    """Matrix multiplication"""
    if not A or not B: return []
    if len(A[0]) != len(B):
        raise ValueError("Number of columns in A must equal number of rows in B")
        
    rows_A = len(A)
    cols_B = len(B[0])
    
    result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(len(B)))
            
    return result

def transpose(matrix: Matrix) -> Matrix:
    """Matrix transpose"""
    if not matrix: return []
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def identity(n: int) -> Matrix:
    """Identity matrix of size n"""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def determinant_2x2(m: Matrix) -> float:
    """Determinant for 2x2 matrices"""
    if len(m) != 2 or len(m[0]) != 2:
        raise ValueError("Matrix must be 2x2")
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]

def cross_product(v1: Vector, v2: Vector) -> Vector:
    """3D vector cross product"""
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product is only defined for 3D vectors")
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def matrix_add(A: Matrix, B: Matrix) -> Matrix:
    """Element-wise matrix addition"""
    if not A or not B: return []
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Matrices must have the same dimensions")
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def matrix_sub(A: Matrix, B: Matrix) -> Matrix:
    """Element-wise matrix subtraction"""
    if not A or not B: return []
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Matrices must have the same dimensions")
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def trace(matrix: Matrix) -> float:
    """Sum of diagonal elements of a square matrix"""
    if not matrix or len(matrix) != len(matrix[0]):
        raise ValueError("Matrix must be square to calculate trace")
    return sum(matrix[i][i] for i in range(len(matrix)))
