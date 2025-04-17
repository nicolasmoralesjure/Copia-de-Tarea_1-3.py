# main.py
import sys
import os
from pathlib import Path
from view.image_view import ImageView
from model.board import Board
from model.exceptions import InvalidBoardException
import json

# Asegurar que Python encuentre los módulos
sys.path.append(str(Path(__file__).parent))

def main():
    try:
        board = Board()
        # Usar ruta absoluta para el archivo JSON
        json_path = os.path.join(os.path.dirname(__file__), "mapa1-2.json")
        board.load_from_json(json_path)
        board.construir_tablero_con_hex_coords()  # Asegúrate de construir el tablero antes de usar port_positions
        print("Mapa cargado y validado correctamente!")
        print(board)
        
        print("\nTerrenos:")
        for tile in board.tiles:
            
            print(f"- {tile.id}: {tile.material} {f'(Número: {tile.number})' if tile.number else ''}")
        
        print("\nPuertos:")
        for port in board.ports:
            print(f"- {port.id}: {port.material} (Ratio: {port.ratio})")
        
        print(f"\nPosición del ladrón: {board.robber_position.id if board.robber_position else 'N/A'}")
    
    except FileNotFoundError:
        print("Error: Archivo no encontrado")
        return  # Termina el programa
    except json.JSONDecodeError:
        print("Error: Formato JSON inválido")
        return  # Termina el programa
    except InvalidBoardException as e:
        if "19 tiles" in str(e):  # Verifica si el mensaje de la excepción menciona los 19 tiles
            print("Error: El mapa no es válido porque tiene una cantidad distinta de 19 tiles.")
        else:
            print(f"Error en el tablero: {str(e)}")
        return  # Termina el programa
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return  # Termina el programa

    # Generar y mostrar imagen
    image_view = ImageView()
    board_image = image_view.generate_board_image(board.tile_coords, board.port_positions, board.robber_position)
    image_view.show_image(board_image)
    image_view.save_image(board_image)

if __name__ == "__main__":
    main()

MAPA_PATH = "Copia de Tarea_1.py/mapa1-2.json"