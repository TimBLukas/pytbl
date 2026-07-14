import json
import csv
from typing import List, Union

Matrix = List[List[Union[int, float]]]

def write_matrix(path: str, matrix: Matrix, fmt: str = "json") -> None:
    """Export matrix to json or csv"""
    if fmt == "json":
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(matrix, f)
    elif fmt == "csv":
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(matrix)
    else:
        raise ValueError("Unsupported format, use 'json' or 'csv'")

def read_matrix(path: str, fmt: str = "json") -> Matrix:
    """Import matrix from json or csv"""
    if fmt == "json":
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif fmt == "csv":
        matrix = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                matrix.append([float(x) if '.' in x else int(x) for x in row])
        return matrix
    else:
        raise ValueError("Unsupported format, use 'json' or 'csv'")
