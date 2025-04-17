from PIL import Image, ImageDraw, ImageFont
import math
from typing import List, Dict, Tuple
from model.tile import Tile
from model.port import Port
from model.HexCoord import HexCoord

class ImageView:
    def __init__(self):
        self.tile_size = 80
        self._init_fonts()
        
        self.colors = {
            "wood": "#5E2605",
            "wool": "#4CAF50", 
            "cereal": "#FFD700",
            "clay": "#B22222",
            "mineral": "#778899",
            "desert": "#F5DEB3"
        }
        
        # Mapeo de posiciones ajustado para distribución perfecta
        self.tile_positions = {
            # Fila superior (3 tiles)
            "c01" : (3, 0), "w01": (2, 0), "c02": (1, 0),
            
            # Segunda fila (4 tiles)
            "y01": (3.5, 1), "w02": (2.5, 1), "o01": (1.5, 1), "o02": (0.5, 1),
            
            # Fila central (5 tiles)
            "o03": (4, 2), "y02": (3, 2), "d": (2, 2), "m01": (1, 2), "o04": (0, 2),
            
            # Cuarta fila (4 tiles)
            "w03": (3.5, 3), "m02": (2.5, 3), "y03": (1.5, 3), "w04": (0.5, 3),
            
            # Fila inferior (3 tiles)
            "c03": (3, 4), "c04": (2, 4), "m03": (1, 4)
        }

        # Posiciones de los puertos relativas a los tiles
        self.port_positions = {
            "p01": ("c01", "top-right"),
            "p02": ("c02", "top-left"),
            "p03": ("y01", "left"),
            "p04": ("o02", "right"),
            "p05": ("o04", "top-left"),
            "p06": ("o03", "left"),
            "p07": ("w04", "top-right"),
            "p08": ("c03", "bottom-left"),
            "p09": ("c04", "bottom-right")
        }

    def _init_fonts(self):
        try:
            self.font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
        except:
            self.font = None
            self.small_font = None
    
    def _draw_robber(self, draw, x, y):
        # Dibuja un círculo negro para representar al ladrón
        size = 15
        draw.ellipse(
            (x - size, y - size, x + size, y + size),
            fill="black",
            outline="white"
        )

        # Letra R encima
        draw.text((x, y), "R", fill="white", anchor="mm", font=self.font)

    def generate_board_image(self, tile_coords, port_positions, robber_position):
        from PIL import Image, ImageDraw
        import math

        width, height = 1200, 900
        image = Image.new("RGB", (width, height), "#4682B4")
        draw = ImageDraw.Draw(image)

        center_x = width // 2
        center_y = height // 2

        # Desplazamientos horizontales por fila para formar la estructura hexagonal
        offset_map = {
            -2: -2,
            -1: -1,
            0: 0,
            1: 1,
            2: 2
        }

        # Dibujar los hexágonos (tiles)
        for tile, coord in tile_coords.items():
            q, r = coord.q, coord.r

            dx = offset_map.get(r, 0) * self.tile_size * 0.75
            x = center_x + q * self.tile_size * 1.5 + dx
            y = center_y + r * self.tile_size * math.sqrt(3)

            self._draw_hexagon(draw, x, y, tile)

            if tile == robber_position:
                self._draw_robber(draw, x, y)

        # Dibujar los puertos
        for port_id, (tile_id, edge) in port_positions.items():
            tile = next((t for t in tile_coords if t.id == tile_id), None)
            if tile is None:
                continue

            coord = tile_coords[tile]
            r = coord.r
            dx = offset_map.get(r, 0) * self.tile_size * 0.75
            x = center_x + coord.q * self.tile_size * 1.5 + dx
            y = center_y + coord.r * self.tile_size * math.sqrt(3)

            self._draw_port(draw, port_id, edge, x, y)

        # Leyenda y retorno de imagen
        self._draw_legend(draw, width, height)
        return image
    
    def _draw_hexagon(self, draw, x, y, tile):
        size = self.tile_size
        color = self.colors.get(tile.material, "#FFFFFF")
        
        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6 + math.pi/6
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill=color, outline="#000000", width=3)
        
        if tile.number and self.font:
            draw.text((x, y), str(tile.number), fill="#000000", font=self.font, anchor="mm")
        
        if self.small_font:
            draw.text((x - size/2 + 10, y - size/2 + 10), tile.id, fill="#00000080", font=self.small_font)


    def _draw_port(self, draw, port_id, edge, x, y):
        import math

        angle_map = {
            "top-left": -150,
            "top-right": -30,
            "right": 30,
            "bottom-right": 90,
            "bottom-left": 150,
            "left": -90
        }

        angle_deg = angle_map.get(edge, 0)
        angle_rad = math.radians(angle_deg)

        # Distancia desde el centro del hexágono hacia afuera
        port_distance = self.tile_size + 10
        px = x + port_distance * math.cos(angle_rad)
        py = y + port_distance * math.sin(angle_rad)

        # Dibujar un triángulo como símbolo del puerto
        triangle = [
            (px, py),
            (px + 5 * math.cos(angle_rad + math.pi / 2), py + 5 * math.sin(angle_rad + math.pi / 2)),
            (px + 5 * math.cos(angle_rad - math.pi / 2), py + 5 * math.sin(angle_rad - math.pi / 2))
        ]
        draw.polygon(triangle, fill="orange")
        # Dibujar el ID del puerto encima
        draw.text((px, py - 10), port_id, fill="black", anchor="mm", font=self.small_font)


    # def _draw_port(self, draw, port: Port, tile_id: str, edge: str, center_x: float, center_y: float):
    #     #Dibuja un puerto en la posición correcta respecto a un tile
    #     if tile_id not in self.tile_positions:
    #         return
            
    #     col, row = self.tile_positions[tile_id]
    #     x = center_x + (col - 2) * self.tile_size * 1.5
    #     y = center_y + (row - 2) * self.tile_size * math.sqrt(3)
        
    #     # Posicionamiento según el borde del tile
    #     angle_map = {
    #         "top-left": 2 * math.pi * 1 / 6 + math.pi/6,
    #         "top-right": 2 * math.pi * 0 / 6 + math.pi/6,
    #         "right": 2 * math.pi * 5 / 6 + math.pi/6,
    #         "bottom-right": 2 * math.pi * 4 / 6 + math.pi/6,
    #         "bottom-left": 2 * math.pi * 3 / 6 + math.pi/6,
    #         "left": 2 * math.pi * 2 / 6 + math.pi/6
    #     }
        
    #     angle = angle_map.get(edge, 0)
    #     port_x = x + (self.tile_size + 15) * math.cos(angle)
    #     port_y = y + (self.tile_size + 15) * math.sin(angle)
        
    #     # Dibujar icono de puerto (triángulo)
    #     draw.polygon([
    #         (port_x, port_y - 10),
    #         (port_x - 8, port_y + 8),
    #         (port_x + 8, port_y + 8)
    #     ], fill="#8B4513", outline="#000000")
        
    #     # Texto del puerto
    #     if self.small_font:
    #         ratio = "3:1" if port.material == "generic" else f"2:1 {port.material[:3]}"
    #         draw.text(
    #             (port_x, port_y + 15), ratio,
    #             fill="#FFFFFF", font=self.small_font, anchor="mt"
    #         )

            
    def _draw_robber(self, draw, x, y):
        robber_size = self.tile_size / 3
        draw.ellipse(
            [x - robber_size, y - robber_size, x + robber_size, y + robber_size],
            fill="#000000", outline="#FFFFFF", width=2
        )
        if self.font:
            draw.text((x, y), "R", fill="#FFFFFF", font=self.font, anchor="mm")

    def _draw_legend(self, draw, width, height):
        if not self.font: return
        
        legend_x = width - 250  # Leyenda más a la derecha
        legend_y = height // 4
        box_size = 30
        
        # Título
        draw.text(
            (legend_x, legend_y - 40), "LEYENDA",
            fill="#FFFFFF", font=self.font
        )
        
        # Recursos
        for i, (material, color) in enumerate(self.colors.items()):
            y_pos = legend_y + i * (box_size + 15)
            draw.rectangle(
                [legend_x, y_pos, legend_x + box_size, y_pos + box_size],
                fill=color, outline="#000000", width=2
            )
            draw.text(
                (legend_x + box_size + 15, y_pos + box_size/2),
                material.capitalize(),
                fill="#FFFFFF",
                font=self.font,
                anchor="lm"
            )
    
    def save_image(self, image: Image.Image, filename: str = "catan_board.png"):
        image.save(filename, quality=95)
        print(f"Tablero guardado como {filename}")
    
    def show_image(self, image: Image.Image):
        image.show()