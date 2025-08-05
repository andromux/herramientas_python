#!/usr/bin/env python3
"""
Video to GIF Converter for Termux
Convierte videos a GIF con opciones de calidad personalizables
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_info(video_path):
    """Obtiene información básica del video"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
            '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def convert_to_gif(input_file, output_file, options):
    """Convierte el video a GIF usando FFmpeg"""
    
    # Comando base de FFmpeg
    cmd = ['ffmpeg', '-i', input_file]
    
    # Aplicar opciones de tiempo si se especifican
    if options.get('start_time'):
        cmd.extend(['-ss', str(options['start_time'])])
    
    if options.get('duration'):
        cmd.extend(['-t', str(options['duration'])])
    
    # Configurar filtros de video
    filters = []
    
    # Escalar el video si es necesario
    if options.get('width') or options.get('height'):
        width = options.get('width', -1)
        height = options.get('height', -1)
        filters.append(f"scale={width}:{height}")
    
    # Configurar FPS
    fps = options.get('fps', 10)
    filters.append(f"fps={fps}")
    
    # Aplicar filtros
    if filters:
        cmd.extend(['-vf', ','.join(filters)])
    
    # Configurar calidad y optimización
    cmd.extend([
        '-gifflags', '+transdiff',
        '-y',  # Sobrescribir archivo de salida
        output_file
    ])
    
    return cmd

def main():
    parser = argparse.ArgumentParser(
        description='Convierte videos a GIF con opciones de calidad personalizables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python video2gif.py video.mp4
  python video2gif.py video.mp4 -o output.gif --width 480 --fps 15
  python video2gif.py video.mp4 --quality high --start 10 --duration 5
  python video2gif.py video.mp4 --quality low --preset fast
        """
    )
    
    # Argumentos principales
    parser.add_argument('input', help='Archivo de video de entrada')
    parser.add_argument('-o', '--output', help='Archivo GIF de salida (opcional)')
    
    # Opciones de calidad predefinidas
    parser.add_argument('--quality', choices=['low', 'medium', 'high', 'custom'],
                       default='medium', help='Nivel de calidad predefinido')
    
    # Opciones de tiempo
    parser.add_argument('--start', type=float, help='Tiempo de inicio en segundos')
    parser.add_argument('--duration', type=float, help='Duración en segundos')
    
    # Opciones de dimensiones
    parser.add_argument('--width', type=int, help='Ancho en píxeles')
    parser.add_argument('--height', type=int, help='Alto en píxeles')
    
    # Opciones de frame rate
    parser.add_argument('--fps', type=int, help='Frames por segundo (FPS)')
    
    # Presets de velocidad
    parser.add_argument('--preset', choices=['fast', 'balanced', 'quality'],
                       default='balanced', help='Preset de velocidad vs calidad')
    
    # Opciones adicionales
    parser.add_argument('--preview', action='store_true',
                       help='Mostrar comando FFmpeg sin ejecutar')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar salida detallada')
    
    args = parser.parse_args()
    
    # Verificar si FFmpeg está instalado
    if not check_ffmpeg():
        print("❌ Error: FFmpeg no está instalado.")
        print("📦 Para instalar en Termux:")
        print("   pkg install ffmpeg")
        sys.exit(1)
    
    # Verificar archivo de entrada
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: El archivo '{args.input}' no existe.")
        sys.exit(1)
    
    # Verificar que el archivo sea un video
    if not get_video_info(str(input_path)):
        print(f"❌ Error: '{args.input}' no parece ser un archivo de video válido.")
        sys.exit(1)
    
    # Generar nombre de salida si no se especifica
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.gif')
    
    # Configurar opciones basadas en calidad predefinida
    options = {}
    
    if args.quality == 'low':
        options.update({
            'width': 320,
            'fps': 8
        })
    elif args.quality == 'medium':
        options.update({
            'width': 480,
            'fps': 12
        })
    elif args.quality == 'high':
        options.update({
            'width': 720,
            'fps': 15
        })
    
    # Aplicar opciones personalizadas (sobrescriben las predefinidas)
    if args.width:
        options['width'] = args.width
    if args.height:
        options['height'] = args.height
    if args.fps:
        options['fps'] = args.fps
    if args.start:
        options['start_time'] = args.start
    if args.duration:
        options['duration'] = args.duration
    
    # Mostrar información de configuración
    print("🎬 Configuración de conversión:")
    print(f"   📁 Entrada: {input_path}")
    print(f"   💾 Salida: {output_path}")
    print(f"   🎯 Calidad: {args.quality}")
    if options.get('width'):
        print(f"   📐 Ancho: {options['width']}px")
    if options.get('height'):
        print(f"   📏 Alto: {options['height']}px")
    print(f"   🎞️  FPS: {options.get('fps', 10)}")
    if options.get('start_time'):
        print(f"   ⏰ Inicio: {options['start_time']}s")
    if options.get('duration'):
        print(f"   ⏱️  Duración: {options['duration']}s")
    
    # Generar comando FFmpeg
    cmd = convert_to_gif(str(input_path), str(output_path), options)
    
    # Mostrar preview del comando si se solicita
    if args.preview:
        print("\n🔍 Comando FFmpeg que se ejecutaría:")
        print(' '.join(cmd))
        return
    
    # Ejecutar conversión
    print("\n🚀 Iniciando conversión...")
    
    try:
        if args.verbose:
            print("📝 Comando FFmpeg:")
            print(' '.join(cmd))
            print("\n📊 Progreso:")
            subprocess.run(cmd, check=True)
        else:
            # Ejecutar con salida mínima
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"\n✅ ¡Conversión completada!")
        print(f"💾 Archivo guardado: {output_path}")
        
        # Mostrar tamaños de archivo
        input_size = input_path.stat().st_size / (1024 * 1024)
        output_size = output_path.stat().st_size / (1024 * 1024)
        
        print(f"📊 Tamaño original: {input_size:.2f} MB")
        print(f"📊 Tamaño GIF: {output_size:.2f} MB")
        print(f"📉 Reducción: {((input_size - output_size) / input_size * 100):.1f}%")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la conversión:")
        if args.verbose:
            print(f"Código de error: {e.returncode}")
            if e.stderr:
                print(f"Error: {e.stderr}")
        else:
            print("Use --verbose para ver detalles del error")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Conversión cancelada por el usuario")
        # Limpiar archivo parcial si existe
        if output_path.exists():
            output_path.unlink()
        sys.exit(1)

if __name__ == '__main__':
    main()
