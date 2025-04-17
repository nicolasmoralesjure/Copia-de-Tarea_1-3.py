from typing import Dict, Optional

class Tile:
    def __init__(self, tile_id: str, material: str, edges: Dict[str, str]):
        self.id = tile_id
        self.material = material
        self.edges = edges
        self.number: Optional[int] = None
        self.has_robber: bool = (material == "desert")
    
    def __repr__(self) -> str:
        return f"Tile(id={self.id}, material={self.material}, number={self.number})"
    
    def set_number(self, number: int) -> None:
        if self.material == "desert":
            self.number = None
        else:
            self.number = number