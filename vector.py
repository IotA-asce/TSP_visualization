"""Lightweight 2D vector helper."""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import NotImplementedType


@dataclass(frozen=True)
class Vector:
    x: float
    y: float

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __add__(self, other: object) -> Vector | NotImplementedType:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: object) -> Vector | NotImplementedType:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: object) -> Vector | NotImplementedType:
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)
        return NotImplemented

    def __rmul__(self, other: object) -> Vector | NotImplementedType:
        return self.__mul__(other)

    def __truediv__(self, scalar: object) -> Vector | NotImplementedType:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def magnitude(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def normalize(self) -> Vector:
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize zero vector")
        return Vector(self.x / mag, self.y / mag)

    def dot_product(self, other: Vector) -> float:
        return self.x * other.x + self.y * other.y

    def angle(self, other: Vector) -> float:
        dot = self.dot_product(other)
        mag_product = self.magnitude() * other.magnitude()
        if mag_product == 0:
            raise ValueError("Cannot calculate angle with zero vector")
        # Clamp value to [-1, 1] to avoid domain errors due to floating point noise
        val = max(-1.0, min(1.0, dot / mag_product))
        return math.acos(val)

    def distance(self, other: Vector) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx**2 + dy**2) ** 0.5

    def get_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
