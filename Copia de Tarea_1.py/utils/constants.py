from typing import Dict, List

# Distribución esperada de materiales
MATERIAL_DISTRIBUTION: Dict[str, int] = {
    "wood": 4,
    "wool": 4,
    "cereal": 4,
    "clay": 3,
    "mineral": 3,
    "desert": 1
}

# Distribución esperada de puertos
PORT_DISTRIBUTION: Dict[str, int] = {
    "generic": 4,
    "wood": 1,
    "wool": 1,
    "cereal": 1,
    "clay": 1,
    "mineral": 1
}

# Orden de numeración de los terrenos
NUMBER_ORDER: List[int] = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]