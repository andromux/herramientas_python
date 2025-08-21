#!/usr/bin/env python3
import os
import subprocess
from functools import wraps

# ---------------- DECORADOR ----------------
def safe_action(func):
    """Decorador para capturar errores y evitar crasheos."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[!] Error en {func.__name__}: {e}")
    return wrapper

# ---------------- CLASE PRINCIPAL ----------------
class SwapManager:
    def __init__(self, swap_dir=None):
        # Ruta de swaps de nvim/vim
        self.swap_dir = swap_dir or os.path.expanduser("~/.local/state/nvim/swap")

    @safe_action
    def listar_swaps(self):
        """Lista los archivos .swp encontrados."""
        if not os.path.exists(self.swap_dir):
            print("No existe el directorio de swap.")
            return []
        archivos = [f for f in os.listdir(self.swap_dir) if f.endswith(".swp")]
        if not archivos:
            print("✅ No hay archivos .swp huérfanos.")
        else:
            print("Archivos swap encontrados:")
            for i, f in enumerate(archivos, 1):
                print(f" {i}. {f}")
        return archivos

    @safe_action
    def recuperar(self, archivo, original):
        """Intenta recuperar un archivo desde su swap."""
        print(f"🔄 Recuperando {original} desde {archivo}...")
        subprocess.run(["nvim", "-r", original])

    @safe_action
    def eliminar(self, archivo):
        """Elimina un archivo .swp."""
        ruta = os.path.join(self.swap_dir, archivo)
        if os.path.exists(ruta):
            os.remove(ruta)
            print(f"🗑️ Eliminado: {ruta}")
        else:
            print(f"No se encontró {ruta}")

# ---------------- MAIN ----------------
def main():
    manager = SwapManager()
    archivos = manager.listar_swaps()
    if not archivos:
        return

    while True:
        print("\nOpciones:")
        print(" 1) Recuperar un archivo")
        print(" 2) Eliminar un archivo .swp")
        print(" 3) Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            idx = int(input("Número del swap a recuperar: ")) - 1
            if 0 <= idx < len(archivos):
                swapfile = archivos[idx]
                # El nombre original está codificado en el nombre del swap
                original = swapfile.replace("%", "/").replace(".swp", "")
                original = original.replace("home", "/home", 1)  # Ajuste simple
                manager.recuperar(os.path.join(manager.swap_dir, swapfile), original)
        elif opcion == "2":
            idx = int(input("Número del swap a eliminar: ")) - 1
            if 0 <= idx < len(archivos):
                manager.eliminar(archivos[idx])
        elif opcion == "3":
            print("👋 Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()

