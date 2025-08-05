#!/usr/bin/env python3
"""
Font Converter CLI - Convierte fuentes TTF a WOFF2
Autor: Claude
Uso: python font_converter.py [opciones]

Requiere:
- fonttools (instalar con: pip install fonttools brotli)
"""

import os
import argparse
import glob
from pathlib import Path
from fontTools.ttLib import TTFont


def convert_ttf_to_woff2(input_file, output_file=None, optimize=True):
    """
    Convierte un archivo TTF a WOFF2 con optimización opcional.
    
    Args:
        input_file (str): Ruta al archivo TTF de entrada
        output_file (str, optional): Ruta de salida para el archivo WOFF2
        optimize (bool): Aplicar optimizaciones adicionales
        
    Returns:
        tuple: (ruta de salida, tamaño original, tamaño nuevo, porcentaje reducido)
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"No se encontró el archivo: {input_file}")
    
    # Determinar el nombre del archivo de salida si no se proporciona
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.woff2'
    
    # Obtener el tamaño original
    original_size = os.path.getsize(input_file)
    
    # Cargar la fuente
    font = TTFont(input_file)
    
    # Aplicar optimizaciones si se solicita
    if optimize:
        # Eliminar tablas innecesarias para web
        for table in ['FFTM', 'DSIG']:
            if table in font:
                del font[table]
    
    # Guardar como WOFF2
    font.flavor = 'woff2'
    font.save(output_file)
    
    # Obtener el tamaño nuevo
    new_size = os.path.getsize(output_file)
    
    # Calcular el porcentaje de reducción
    reduction = 100 - (new_size / original_size * 100)
    
    return (output_file, original_size, new_size, reduction)


def process_files(input_pattern, output_dir=None, optimize=True, recursive=False):
    """
    Procesa múltiples archivos TTF basados en el patrón proporcionado.
    
    Args:
        input_pattern (str): Patrón glob para seleccionar archivos (*.ttf)
        output_dir (str, optional): Directorio para los archivos de salida
        optimize (bool): Aplicar optimizaciones adicionales
        recursive (bool): Buscar archivos recursivamente
    """
    # Manejar la búsqueda recursiva
    if recursive:
        files = []
        for root, _, _ in os.walk(os.path.dirname(input_pattern) or '.'):
            base_pattern = os.path.basename(input_pattern)
            files.extend(glob.glob(os.path.join(root, base_pattern)))
    else:
        files = glob.glob(input_pattern)
    
    if not files:
        print(f"No se encontraron archivos que coincidan con: {input_pattern}")
        return
    
    total_original = 0
    total_new = 0
    
    print(f"\n{'Archivo':<40} {'Original':<10} {'WOFF2':<10} {'Reducción':<10}")
    print("-" * 75)
    
    for input_file in files:
        if output_dir:
            output_file = os.path.join(
                output_dir, 
                os.path.basename(os.path.splitext(input_file)[0]) + '.woff2'
            )
        else:
            output_file = None
            
        try:
            result = convert_ttf_to_woff2(input_file, output_file, optimize)
            output_path, orig_size, new_size, reduction = result
            
            total_original += orig_size
            total_new += new_size
            
            # Formatear tamaños en KB
            orig_kb = orig_size / 1024
            new_kb = new_size / 1024
            
            # Mostrar resultado
            print(f"{os.path.basename(input_file):<40} {orig_kb:.2f} KB {new_kb:.2f} KB {reduction:.2f}%")
        
        except Exception as e:
            print(f"Error al procesar {input_file}: {str(e)}")
    
    # Mostrar resumen
    if len(files) > 1:
        total_reduction = 100 - (total_new / total_original * 100)
        print("-" * 75)
        print(f"Total: {len(files)} archivos, {total_original/1024:.2f} KB → {total_new/1024:.2f} KB ({total_reduction:.2f}% reducción)")


def main():
    parser = argparse.ArgumentParser(
        description="Conversor de fuentes TTF a WOFF2 optimizado para web"
    )
    
    parser.add_argument(
        "input", 
        help="Archivo TTF o patrón (ej: *.ttf) para convertir"
    )
    
    parser.add_argument(
        "-o", "--output", 
        help="Archivo de salida o directorio para guardar los archivos WOFF2"
    )
    
    parser.add_argument(
        "-d", "--directory",
        help="Directorio para guardar los archivos WOFF2 convertidos",
    )
    
    parser.add_argument(
        "--no-optimize", 
        action="store_true",
        help="Desactivar optimizaciones adicionales"
    )
    
    parser.add_argument(
        "-r", "--recursive", 
        action="store_true",
        help="Buscar archivos recursivamente en subdirectorios"
    )

    args = parser.parse_args()
    
    # Determinar si estamos procesando un solo archivo o múltiples
    is_pattern = '*' in args.input or '?' in args.input or os.path.isdir(args.input)
    
    if is_pattern:
        # Si es un directorio, añadir *.ttf
        if os.path.isdir(args.input):
            input_pattern = os.path.join(args.input, "*.ttf")
        else:
            input_pattern = args.input
            
        # Procesar múltiples archivos
        process_files(
            input_pattern, 
            args.directory or args.output, 
            not args.no_optimize,
            args.recursive
        )
    else:
        # Procesar un solo archivo
        try:
            if args.directory:
                output = os.path.join(
                    args.directory, 
                    os.path.basename(os.path.splitext(args.input)[0]) + '.woff2'
                )
            else:
                output = args.output
                
            result = convert_ttf_to_woff2(args.input, output, not args.no_optimize)
            output_path, orig_size, new_size, reduction = result
            
            print(f"\nConversión exitosa: {args.input} → {output_path}")
            print(f"Tamaño original: {orig_size / 1024:.2f} KB")
            print(f"Tamaño WOFF2: {new_size / 1024:.2f} KB")
            print(f"Reducción: {reduction:.2f}%")
            
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
