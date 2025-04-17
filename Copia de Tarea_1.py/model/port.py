class Port:
    def __init__(self, port_id: str, material: str):
        self.id = port_id
        self.material = material
    
    @property
    def ratio(self) -> str:
        return "3:1" if self.material == "generic" else "2:1"
    
    def __repr__(self) -> str:
        return f"Port(id={self.id}, material={self.material}, ratio={self.ratio})"