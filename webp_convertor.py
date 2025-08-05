#!/usr/bin/env python3
"""
Script para convertir todas las imágenes JPG y PNG a formato WebP
manteniendo las originales y creando nuevas versiones con extensión .webp
"""

import os
import subprocess
import sys
from pathlib import Path

def check_cwebp():
    """Verifica si cwebp está instalado"""
    try:
        subprocess.run(['cwebp', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_to_webp(input_path, output_path, quality=85):
    """Convierte una imagen a WebP usando cwebp"""
    try:
        cmd = ['cwebp', str(input_path), '-q', str(quality), '-o', str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Obtener tamaños para mostrar ahorro
            original_size = input_path.stat().st_size
            webp_size = output_path.stat().st_size
            reduction = ((original_size - webp_size) / original_size) * 100
            
            print(f"✓ {input_path.name} → {output_path.name}")
            print(f"  Tamaño original: {original_size:,} bytes")
            print(f"  Tamaño WebP: {webp_size:,} bytes")
            print(f"  Reducción: {reduction:.1f}%")
            print()
            return True
        else:
            print(f"✗ Error convirtiendo {input_path.name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error procesando {input_path.name}: {e}")
        return False

def main():
    """Función principal"""
    
    # Verificar si cwebp está instalado
    if not check_cwebp():
        print("❌ Error: cwebp no está instalado")
        print("Instálalo con:")
        print("  Ubuntu/Debian: sudo apt install webp")
        print("  macOS: brew install webp")
        print("  Windows: descarga desde https://developers.google.com/speed/webp/download")
        sys.exit(1)
    
    # Directorio actual
    current_dir = Path('.')
    
    # Extensiones a convertir
    extensions = ['.jpg', '.jpeg', '.png']
    
    # Encontrar todas las imágenes
    images_to_convert = []
    for ext in extensions:
        images_to_convert.extend(current_dir.glob(f'*{ext}'))
        images_to_convert.extend(current_dir.glob(f'*{ext.upper()}'))
    
    if not images_to_convert:
        print("❌ No se encontraron imágenes JPG o PNG para convertir")
        sys.exit(1)
    
    print(f"📸 Se encontraron {len(images_to_convert)} imágenes para convertir")
    print("=" * 50)
    
    successful_conversions = 0
    total_original_size = 0
    total_webp_size = 0
    
    for image_path in images_to_convert:
        # Crear nombre del archivo WebP
        webp_path = image_path.with_suffix('.webp')
        
        # Verificar si ya existe la versión WebP
        if webp_path.exists():
            print(f"⏭️  {webp_path.name} ya existe, saltando...")
            continue
        
        # Convertir a WebP
        if convert_to_webp(image_path, webp_path):
            successful_conversions += 1
            total_original_size += image_path.stat().st_size
            total_webp_size += webp_path.stat().st_size
    
    # Mostrar resumen
    print("=" * 50)
    print(f"✅ Conversiones completadas: {successful_conversions}/{len(images_to_convert)}")
    
    if successful_conversions > 0:
        total_reduction = ((total_original_size - total_webp_size) / total_original_size) * 100
        print(f"📊 Ahorro total: {total_original_size - total_webp_size:,} bytes ({total_reduction:.1f}%)")
        print(f"📦 Tamaño original total: {total_original_size:,} bytes")
        print(f"📦 Tamaño WebP total: {total_webp_size:,} bytes")

if __name__ == "__main__":
    main()
