#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir todas las referencias de imágenes locales en HTML a CDN jsdelivr
Convierte rutas locales a: https://cdn.jsdelivr.net/gh/Chakielzero/imagenes@main/imagen.webp
Uso: python html_cdn_converter.py archivo.html
"""

import re
import sys
import os
from pathlib import Path

# URL base del CDN jsdelivr
CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/Chakielzero/imagenes@main/"

def convert_html_images_to_cdn(file_path):
    """
    Convierte todas las referencias de imágenes locales en un archivo HTML a CDN jsdelivr
    
    Args:
        file_path (str): Ruta al archivo HTML
    """
    
    try:
        # Leer el archivo HTML
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Patrones para detectar diferentes tipos de referencias de imágenes locales
        patterns = [
            # src="ruta/imagen.extension" o src="imagen.extension" (atributo src general)
            {
                'pattern': r'(src\s*=\s*["\'])([^"\']*?)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)(["\'])',
                'type': 'src attribute',
                'groups': (1, 2, 3)  # (prefix, image_path, suffix)
            },
            # style="background-image: url('imagen.extension')"
            {
                'pattern': r'(background-image\s*:\s*url\s*\(\s*["\']?)([^"\']*?)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)(["\']?\s*\))',
                'type': 'background-image',
                'groups': (1, 2, 3)
            },
            # CSS url() sin comillas: url(imagen.extension)
            {
                'pattern': r'(url\s*\(\s*)([^)]*?)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)(\s*\))',
                'type': 'CSS url()',
                'groups': (1, 2, 3)
            },
            # poster="imagen.extension" (para videos)
            {
                'pattern': r'(poster\s*=\s*["\'])([^"\']*?)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)(["\'])',
                'type': 'poster attribute',
                'groups': (1, 2, 3)
            },
            # data-src="imagen.extension" (lazy loading)
            {
                'pattern': r'(data-src\s*=\s*["\'])([^"\']*?)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)(["\'])',
                'type': 'data-src attribute',
                'groups': (1, 2, 3)
            },
            # srcset="imagen.extension" (responsive images)
            {
                'pattern': r'(srcset\s*=\s*["\'][^"\']*?)([^"\'\/\s,]+)\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)([^"\']*["\'])',
                'type': 'srcset attribute',
                'groups': (1, 2, 3)
            }
        ]
        
        converted_images = []
        updated_content = content
        
        for pattern_info in patterns:
            pattern = pattern_info['pattern']
            pattern_type = pattern_info['type']
            groups = pattern_info['groups']
            
            matches = list(re.finditer(pattern, updated_content, re.IGNORECASE))
            
            # Procesar matches en orden inverso para evitar problemas de índices
            for match in reversed(matches):
                prefix = match.group(groups[0])
                image_path = match.group(groups[1])
                suffix = match.group(groups[2])
                
                # Solo procesar imágenes locales
                if is_local_path(image_path):
                    # Extraer solo el nombre del archivo (sin ruta ni extensión)
                    filename = Path(image_path).stem
                    
                    # Crear nueva URL del CDN (siempre .webp)
                    new_cdn_url = f"{CDN_BASE_URL}{filename}.webp"
                    
                    # Reemplazar en el contenido
                    old_full = match.group(0)
                    new_full = prefix + new_cdn_url + suffix
                    
                    # Para srcset, necesitamos manejar múltiples imágenes
                    if pattern_type == 'srcset attribute':
                        # En srcset podría haber múltiples imágenes, pero procesamos una a la vez
                        updated_content = updated_content[:match.start()] + new_full + updated_content[match.end():]
                    else:
                        updated_content = updated_content[:match.start()] + new_full + updated_content[match.end():]
                    
                    # Registrar la conversión
                    original_extension = get_original_extension(old_full)
                    converted_images.append({
                        'original': image_path + original_extension,
                        'new': new_cdn_url,
                        'type': pattern_type,
                        'full_match': old_full.strip()
                    })
        
        # Crear backup del archivo original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        
        # Escribir el contenido actualizado
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        return True, converted_images, backup_path
        
    except Exception as e:
        return False, [], str(e)

def is_local_path(path):
    """
    Determina si una ruta es local (no es una URL externa)
    
    Args:
        path (str): Ruta a verificar
        
    Returns:
        bool: True si es ruta local, False si es URL externa
    """
    # Limpiar espacios
    path = path.strip()
    
    # Ignorar URLs externas
    if path.startswith(('http://', 'https://', '//', 'data:', 'blob:')):
        return False
    
    # Ignorar rutas que empiecen con / (rutas absolutas del servidor)
    if path.startswith('/') and not path.startswith('./'):
        return False
    
    # Ignorar si ya es una URL de jsdelivr
    if 'jsdelivr.net' in path or 'github.com' in path:
        return False
    
    return True

def get_original_extension(full_match):
    """
    Extrae la extensión original de una coincidencia completa
    
    Args:
        full_match (str): Cadena completa que contiene la imagen
        
    Returns:
        str: Extensión original encontrada
    """
    extensions = ['.webp', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg']
    full_match_lower = full_match.lower()
    
    for ext in extensions:
        if ext in full_match_lower:
            return ext
    return '.webp'  # Default

def show_conversion_summary(converted_images):
    """Muestra un resumen de las conversiones realizadas"""
    
    if not converted_images:
        print("ℹ️  No se encontraron imágenes locales para convertir.")
        return
    
    print(f"\n📊 Resumen de conversiones:")
    print("=" * 70)
    
    # Agrupar por tipo
    by_type = {}
    for img in converted_images:
        img_type = img['type']
        if img_type not in by_type:
            by_type[img_type] = []
        by_type[img_type].append(img)
    
    for img_type, images in by_type.items():
        print(f"\n🔧 {img_type.upper()}:")
        for i, img in enumerate(images[:3], 1):  # Mostrar máximo 3 ejemplos por tipo
            print(f"   {i}. {img['original']}")
            print(f"      → {img['new']}")
        
        if len(images) > 3:
            print(f"   ... y {len(images) - 3} más")
    
    print(f"\n✨ Total de imágenes convertidas: {len(converted_images)}")
    print(f"🌐 Todas ahora apuntan a: {CDN_BASE_URL}")

def find_html_files(directory='.'):
    """Encuentra todos los archivos HTML en el directorio"""
    html_files = []
    for file in os.listdir(directory):
        if file.endswith(('.html', '.htm')) and not file.endswith('.backup'):
            html_files.append(file)
    return html_files

def main():
    """Función principal del script"""
    
    print("🌐 Script de conversión de imágenes HTML a CDN jsdelivr")
    print("=" * 60)
    print(f"🔗 CDN Base: {CDN_BASE_URL}")
    
    # Verificar argumentos
    if len(sys.argv) > 2:
        print("❌ Uso incorrecto.")
        print("📖 Uso: python html_cdn_converter.py [archivo.html]")
        print("📖 Si no especificas archivo, procesará todos los .html del directorio")
        sys.exit(1)
    
    current_dir = os.getcwd()
    
    # Determinar qué archivos procesar
    if len(sys.argv) == 2:
        # Archivo específico
        file_path = sys.argv[1]
        
        if not os.path.exists(file_path):
            print(f"❌ Error: El archivo '{file_path}' no existe.")
            sys.exit(1)
        
        files_to_process = [file_path]
    else:
        # Buscar todos los archivos HTML
        html_files = find_html_files(current_dir)
        
        if not html_files:
            print("❌ No se encontraron archivos HTML en el directorio actual.")
            sys.exit(1)
        
        print("📁 Archivos HTML encontrados:")
        for i, file in enumerate(html_files, 1):
            print(f"   {i}. {file}")
        
        files_to_process = html_files
    
    # Mostrar configuración
    print(f"\n🔍 Configuración:")
    print(f"   Archivos a procesar: {len(files_to_process)}")
    print(f"   Directorio: {current_dir}")
    print(f"   Repositorio: Chakielzero/imagenes@main")
    print(f"   Conversión: imágenes locales → CDN jsdelivr (.webp)")
    
    confirm = input(f"\n¿Continuar con la conversión a CDN? (s/n): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        sys.exit(0)
    
    # Procesar archivos
    total_files_processed = 0
    total_images_converted = 0
    
    for file_path in files_to_process:
        print(f"\n🔄 Procesando: {file_path}")
        print("-" * 50)
        
        success, converted_images, backup_path = convert_html_images_to_cdn(file_path)
        
        if success:
            if converted_images:
                print(f"✅ {file_path} procesado exitosamente")
                print(f"💾 Backup creado: {backup_path}")
                show_conversion_summary(converted_images)
                total_images_converted += len(converted_images)
                total_files_processed += 1
            else:
                print(f"ℹ️  {file_path}: No se encontraron imágenes locales para convertir")
        else:
            print(f"❌ Error procesando {file_path}: {backup_path}")
    
    # Resumen final
    print(f"\n🎉 Procesamiento completado!")
    print("=" * 50)
    print(f"📁 Archivos procesados: {total_files_processed}")
    print(f"🖼️  Imágenes convertidas: {total_images_converted}")
    print(f"💾 Se crearon backups (.backup) de todos los archivos modificados")
    print(f"🌐 CDN: https://cdn.jsdelivr.net/gh/Chakielzero/imagenes@main/")
    
    if total_images_converted > 0:
        print(f"\n🌟 ¡Conversión completada! Todas las imágenes locales ahora usan CDN jsdelivr")
        print(f"⚡ Las imágenes se cargarán más rápido desde el CDN global")

if __name__ == "__main__":
    main()
