#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar rutas locales de imágenes a rutas CDN jsdelivr
Uso: python cdn_updater.py archivo.js
"""

import re
import sys
import os

def update_img_src_to_cdn(file_path, console_name):
    """
    Actualiza las rutas imgSrc en un archivo JavaScript para usar CDN jsdelivr
    
    Args:
        file_path (str): Ruta al archivo JavaScript
        console_name (str): Nombre de la consola (ej: ps2, nintendo3ds, etc.)
    """
    
    # URL base del CDN jsdelivr
    cdn_base_url = f"https://cdn.jsdelivr.net/gh/Chakielzero/imagenes@main/{console_name}/"
    
    try:
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Patrón regex para encontrar imgSrc con rutas locales
        # Busca: imgSrc: "assets/img/nombre.extension" o imgSrc: "ruta/nombre.extension"
        pattern = r'imgSrc:\s*["\']([^"\']*[/\\])?([^"\'\\]+)\.([^"\']+)["\']'
        
        def replace_img_src(match):
            # match.group(1) = ruta (puede ser None)
            # match.group(2) = nombre del archivo sin extensión
            # match.group(3) = extensión original
            
            filename = match.group(2)  # Solo el nombre del archivo
            new_url = f'{cdn_base_url}{filename}.webp'
            return f'imgSrc: "{new_url}"'
        
        # Aplicar el reemplazo
        updated_content = re.sub(pattern, replace_img_src, content)
        
        # Crear backup del archivo original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        
        # Escribir el contenido actualizado
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print(f"✅ Archivo actualizado exitosamente: {file_path}")
        print(f"📁 Backup creado en: {backup_path}")
        print(f"🌐 CDN base URL: {cdn_base_url}")
        
        # Mostrar algunos ejemplos de cambios
        show_changes_preview(content, updated_content)
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

def show_changes_preview(original_content, updated_content):
    """Muestra una vista previa de los cambios realizados"""
    
    # Encontrar las líneas imgSrc en el contenido original y actualizado
    original_imgs = re.findall(r'imgSrc:\s*["\'][^"\']+["\']', original_content)
    updated_imgs = re.findall(r'imgSrc:\s*["\'][^"\']+["\']', updated_content)
    
    if original_imgs and updated_imgs:
        print("\n📝 Vista previa de cambios:")
        print("-" * 50)
        
        # Mostrar hasta 3 ejemplos
        for i in range(min(3, len(original_imgs))):
            if i < len(updated_imgs):
                print(f"Antes:  {original_imgs[i]}")
                print(f"Después: {updated_imgs[i]}")
                print()

def main():
    """Función principal del script"""
    
    print("🔄 Script de actualización de rutas a CDN jsdelivr")
    print("=" * 50)
    
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("❌ Uso incorrecto.")
        print("📖 Uso: python cdn_updater.py archivo.js")
        print("📖 Ejemplo: python cdn_updater.py listas.js")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        print(f"❌ Error: El archivo '{file_path}' no existe.")
        sys.exit(1)
    
    # Solicitar el nombre de la consola
    print(f"📁 Archivo a procesar: {file_path}")
    console_name = input("🎮 Ingresa el nombre de la consola (ej: ps2, nintendo3ds, psp, etc.): ").strip()
    
    if not console_name:
        print("❌ Error: Debes ingresar un nombre de consola.")
        sys.exit(1)
    
    # Confirmar la operación
    print(f"\n🔍 Configuración:")
    print(f"   Archivo: {file_path}")
    print(f"   Consola: {console_name}")
    print(f"   CDN URL: https://cdn.jsdelivr.net/gh/Chakielzero/imagenes@main/{console_name}/")
    
    confirm = input("\n¿Continuar con la actualización? (s/n): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        sys.exit(0)
    
    # Procesar el archivo
    update_img_src_to_cdn(file_path, console_name)

if __name__ == "__main__":
    main()
