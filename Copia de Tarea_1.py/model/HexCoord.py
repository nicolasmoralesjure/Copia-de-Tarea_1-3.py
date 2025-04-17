from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import deque

@dataclass(frozen=True)
class HexCoord:
    """Coordenadas axiales optimizadas para Catan"""
    q: int  # columna (eje x)
    r: int  # fila (eje y)
    
    def __add__(self, other):
        return HexCoord(self.q + other.q, self.r + other.r)