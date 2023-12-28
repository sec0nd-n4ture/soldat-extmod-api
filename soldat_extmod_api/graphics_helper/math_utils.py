import math
from math import sin, cos, radians

def lerpf(a: float, b: float, step: float) -> float:
    return (1 - step) * a + step * b

def npot(x):
    x -= 1
    x |= x >> 1
    x |= x >> 2
    x |= x >> 4
    x |= x >> 8
    x |= x >> 16
    return max(2, x + 1)