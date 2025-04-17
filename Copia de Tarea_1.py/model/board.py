import json
import random
from collections import deque
from typing import Dict, List, Optional
from model.exceptions import InvalidBoardException
from model.port import Port
from model.tile import Tile
from model.HexCoord import HexCoord
from utils.constants import MATERIAL_DISTRIBUTION, PORT_DISTRIBUTION, NUMBER_ORDER

class Board:
    def __init__(self):
        self.tiles: List[Tile] = []
        self.ports: List[Port] = []
        self.robber_position: Optional[Tile] = None
        self.hex_grid: Dict[HexCoord, Tile] = {}
        self.tile_coords: Dict[Tile, HexCoord] = {}

    def load_from_json(self, file_path: str) -> None:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if len(data.get("tiles", [])) != 19:
            raise InvalidBoardException("El mapa debe contener exactamente 19 tiles.")
    
    # Excluir el desierto al contar los tiles
        non_desert_tiles = [tile for tile in data.get("tiles", []) if tile.get("material") != "desert"]
        if len(non_desert_tiles) != 18:  # 18 tiles sin contar el desierto
            raise InvalidBoardException("El mapa debe contener exactamente 18 tiles (excluyendo el desierto).")
        
        self._create_randomized_tiles(data['tiles'])
        self._create_ports(data['ports'])
        self._assign_random_numbers()
        self._validate_board()
        self._validate_board2()


    def _create_randomized_tiles(self, tiles_data: List[Dict]) -> None:
        self.tiles = [Tile(tile['id'], tile['material'], tile['edges']) for tile in tiles_data]

    def _create_ports(self, ports_data: List[Dict]) -> None:
        #Crea los objetos Port a partir de los datos del JSON
        self.ports = [Port(port['id'], port['material']) for port in ports_data]

    def _assign_random_numbers(self) -> None:
        #Asigna números aleatorios a los terrenos (excepto desierto)
        # Filtrar tiles que deben llevar número
        number_tiles = [t for t in self.tiles if t.material != 'desert']
        
        # Mezclar los números disponibles
        shuffled_numbers = NUMBER_ORDER.copy()
        random.shuffle(shuffled_numbers)
        
        # Asignar números
        for i, tile in enumerate(number_tiles):
            if i < len(shuffled_numbers):
                tile.set_number(shuffled_numbers[i])
        
        # Establecer posición del ladrón
        desert = next((t for t in self.tiles if t.material == 'desert'), None)
        if desert:
            self.robber_position = desert


    def construir_tablero_con_hex_coords(self):
        """Construye el tablero físico respetando los edges usando coordenadas axiales hexagonales"""

        HEX_DIRECTIONS = {
            'top-left': HexCoord(0, -1),
            'top-right': HexCoord(1, -1),
            'right': HexCoord(1, 0),
            'bottom-right': HexCoord(0, 1),
            'bottom-left': HexCoord(-1, 1),
            'left': HexCoord(-1, 0),
        }

        # 1. Encontrar el desierto
        desert = next((t for t in self.tiles if t.material == "desert"), None)
        if not desert:
            raise InvalidBoardException("No se encontró el tile del desierto")

        # 2. Inicializar estructuras
        self.hex_grid = {}
        self.tile_coords = {}

        center = HexCoord(0, 0)
        self.hex_grid[center] = desert
        self.tile_coords[desert] = center

        queue = deque([desert])

        while queue:
            current = queue.popleft()
            current_coord = self.tile_coords[current]

            for direction, neighbor_id in current.edges.items():
                neighbor_tile = self.find_tile_by_id(neighbor_id)
                if not neighbor_tile:
                    continue

                if neighbor_tile in self.tile_coords:
                    continue

                offset = HEX_DIRECTIONS[direction]
                neighbor_coord = current_coord + offset

                self.hex_grid[neighbor_coord] = neighbor_tile
                self.tile_coords[neighbor_tile] = neighbor_coord
                queue.append(neighbor_tile)

        #3 Ordenar los tiles para que la imagen los dibuje correctamente
        self.tiles = [tile for coord, tile in sorted(self.hex_grid.items(), key=lambda x: (x[0].r, x[0].q))]

        #4 . Crear un diccionario para los puertos
        self.port_positions = {}  # key: port_id → value: (tile_id, direction)
        for tile in self.tiles:
            for direction, neighbor_id in tile.edges.items():
                if neighbor_id.startswith("p"):
                    self.port_positions[neighbor_id] = (tile.id, direction)

    def _validate_board(self) -> None:
        """Valida que el tablero cumpla con todas las reglas"""
        self._validate_desert_position()
        self._validate_edge_consistency()
        self._validate_material_distribution()
        self._validate_port_distribution()
        self._validate_adjacent_ports()
        self._validate_board2()
    
    def _validate_desert_position(self) -> None:
        """Valida que el desierto esté en el centro"""
        desert_tiles = [tile for tile in self.tiles if tile.material == "desert"]
        
        desert = desert_tiles[0]
    
    def _validate_edge_consistency(self) -> None:
        """Valida que las conexiones entre terrenos sean consistentes"""
        for tile in self.tiles:
            for direction, adjacent_id in tile.edges.items():
                adjacent_tile = self.find_tile_by_id(adjacent_id)
                
    def _validate_material_distribution(self) -> None:
        """Valida la distribución correcta de materiales"""
        material_counts = {}
        for tile in self.tiles:
            material_counts[tile.material] = material_counts.get(tile.material, 0) + 1

    def _validate_port_distribution(self) -> None:
        """Valida la distribución correcta de puertos"""
        port_counts = {"generic": 0}
        for port in self.ports:
            if port.material == "generic":
                port_counts["generic"] += 1
            else:
                port_counts[port.material] = port_counts.get(port.material, 0) + 1

    def _validate_adjacent_ports(self) -> None:
        """Valida que no haya puertos colindantes"""
        port_edges = set()
        
        for tile in self.tiles:
            for edge_id in tile.edges.values():
                if any(port.id == edge_id for port in self.ports):
                    port_edges.add(edge_id)
        
    def _get_reverse_direction(self, direction: str) -> str:
        """Obtiene la dirección inversa para validar conexiones"""
        direction_pairs = {
            "top-left": "bottom-right",
            "top-right": "bottom-left",
            "right": "left",
            "left": "right",
            "bottom-left": "top-right",
            "bottom-right": "top-left"
        }
        return direction_pairs.get(direction, direction)
    
    def find_tile_by_id(self, tile_id: str) -> Optional[Tile]:
        """Encuentra un terreno por su ID"""
        for tile in self.tiles:
            if tile.id == tile_id:
                return tile
        return None
    
    def _validate_board2(self):
        errors = []

        # Verificar que haya exactamente 19 tiles
        if len(self.tiles) != 19:
            errors.append(f"Se esperaban 19 tiles, pero se encontraron {len(self.tiles)}.")

        # Verificar que haya exactamente 1 desierto
        desert_tiles = [t for t in self.tiles if t.material == "desert"]
        if len(desert_tiles) != 1:
            errors.append(f"Debe haber exactamente 1 tile de desierto, se encontraron {len(desert_tiles)}.")

        # Verificar que todos los edges apunten a IDs válidos
        valid_ids = set(t.id for t in self.tiles) | set(p.id for p in self.ports)
        for tile in self.tiles:
            for direction, target_id in tile.edges.items():
                if target_id not in valid_ids:
                    errors.append(f"El tile '{tile.id}' tiene un edge inválido hacia '{target_id}'.")

        # Verificar que cada tile tenga id, material y edges
        for tile in self.tiles:
            if not hasattr(tile, "id") or not hasattr(tile, "material") or not hasattr(tile, "edges"):
                errors.append(f"Tile con datos incompletos: {vars(tile)}")

        # Si hay errores, lanzar excepción
        if errors:
            raise InvalidBoardException("Errores al validar el tablero:\n" + "\n".join(errors))

    def __repr__(self) -> str:
        return f"Board(tiles={len(self.tiles)}, ports={len(self.ports)})"
    
