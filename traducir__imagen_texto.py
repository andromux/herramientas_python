#!/usr/bin/env python3
"""
Traductor de Texto en Imágenes - Versión Termux Android
Script para extraer texto de imágenes usando OCR y traducirlo automáticamente.
Optimizado para funcionar en Termux (Android).
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    from googletrans import Translator
    from colorama import init, Fore, Style, Back
except ImportError as e:
    print(f"Error: Falta instalar una dependencia: {e}")
    print("\nPara Termux, instala las dependencias con:")
    print("pkg update && pkg upgrade")
    print("pkg install python tesseract")
    print("pip install pytesseract pillow googletrans==4.0.0rc1 colorama")
    sys.exit(1)

# Detectar si estamos en Termux
IS_TERMUX = os.path.exists('/data/data/com.termux')

# Configurar ruta de tesseract para Termux
if IS_TERMUX:
    # En Termux, tesseract está en $PREFIX/bin/
    tesseract_path = os.path.join(os.environ.get('PREFIX', '/data/data/com.termux/files/usr'), 'bin', 'tesseract')
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Inicializar colorama para Windows
init(autoreset=True)

class ImageTranslator:
    def __init__(self):
        self.translator = Translator()
        
    def extract_text_from_image(self, image_path):
        """Extrae texto de una imagen usando OCR"""
        try:
            # Abrir la imagen
            image = Image.open(image_path)
            
            # Configurar pytesseract para mejor reconocimiento
            # Puedes ajustar estos parámetros según tus necesidades
            custom_config = r'--oem 3 --psm 6'
            
            # Extraer texto
            text = pytesseract.image_to_string(image, config=custom_config, lang='spa+eng')
            
            return text.strip()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"No se pudo encontrar el archivo: {image_path}")
        except Exception as e:
            raise Exception(f"Error al procesar la imagen: {str(e)}")
    
    def translate_text(self, text, source_lang='auto', dest_lang='es'):
        """Traduce el texto usando Google Translate"""
        try:
            if not text:
                return "No se encontró texto para traducir."
            
            # Detectar y traducir
            result = self.translator.translate(text, src=source_lang, dest=dest_lang)
            
            return {
                'original': text,
                'translated': result.text,
                'detected_lang': result.src,
                'target_lang': dest_lang
            }
            
        except Exception as e:
            raise Exception(f"Error al traducir el texto: {str(e)}")
    
    def save_to_file(self, content, output_path):
        """Guarda el contenido en un archivo"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Error al guardar el archivo: {str(e)}")

def print_colored_help():
    """Muestra el menú de ayuda con colores"""
    help_text = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║                    TRADUCTOR DE IMÁGENES                     ║
║                     📱 Versión Termux                        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}{Style.BRIGHT}DESCRIPCIÓN:{Style.RESET_ALL}
  Este script extrae texto de imágenes usando OCR y lo traduce automáticamente.
  Optimizado para funcionar en Termux (Android).

{Fore.GREEN}{Style.BRIGHT}USO:{Style.RESET_ALL}
  {Fore.YELLOW}python traductor_imagen.py imagen.png [opciones]{Style.RESET_ALL}

{Fore.GREEN}{Style.BRIGHT}ARGUMENTOS REQUERIDOS:{Style.RESET_ALL}
  {Fore.WHITE}imagen{Style.RESET_ALL}                 Ruta de la imagen a procesar

{Fore.GREEN}{Style.BRIGHT}OPCIONES:{Style.RESET_ALL}
  {Fore.CYAN}-o, --output{Style.RESET_ALL}          Archivo de salida (ej: -o texto.txt)
  {Fore.CYAN}-t, --terminal{Style.RESET_ALL}        Mostrar resultado solo en terminal
  {Fore.CYAN}-sl, --source-lang{Style.RESET_ALL}    Idioma origen (default: auto)
  {Fore.CYAN}-dl, --dest-lang{Style.RESET_ALL}      Idioma destino (default: es)
  {Fore.CYAN}-h, --help{Style.RESET_ALL}            Mostrar esta ayuda

{Fore.GREEN}{Style.BRIGHT}IDIOMAS SOPORTADOS:{Style.RESET_ALL}
  {Fore.MAGENTA}es{Style.RESET_ALL} - Español    {Fore.MAGENTA}en{Style.RESET_ALL} - Inglés     {Fore.MAGENTA}fr{Style.RESET_ALL} - Francés
  {Fore.MAGENTA}de{Style.RESET_ALL} - Alemán     {Fore.MAGENTA}it{Style.RESET_ALL} - Italiano   {Fore.MAGENTA}pt{Style.RESET_ALL} - Portugués
  {Fore.MAGENTA}ja{Style.RESET_ALL} - Japonés    {Fore.MAGENTA}ko{Style.RESET_ALL} - Coreano    {Fore.MAGENTA}zh{Style.RESET_ALL} - Chino

{Fore.GREEN}{Style.BRIGHT}EJEMPLOS:{Style.RESET_ALL}
  {Fore.YELLOW}# Traducir imagen desde almacenamiento interno{Style.RESET_ALL}
  python traductor_imagen.py /sdcard/Download/imagen.png -t

  {Fore.YELLOW}# Guardar traducción en archivo{Style.RESET_ALL}
  python traductor_imagen.py imagen.png -o resultado.txt

  {Fore.YELLOW}# Traducir de inglés a español{Style.RESET_ALL}
  python traductor_imagen.py imagen.png -sl en -dl es -t

{Fore.GREEN}{Style.BRIGHT}INSTALACIÓN EN TERMUX:{Style.RESET_ALL}
  {Fore.YELLOW}# Actualizar Termux{Style.RESET_ALL}
  pkg update && pkg upgrade
  
  {Fore.YELLOW}# Instalar dependencias del sistema{Style.RESET_ALL}
  pkg install python tesseract
  
  {Fore.YELLOW}# Instalar paquetes de Python{Style.RESET_ALL}
  pip install pytesseract pillow googletrans==4.0.0rc1 colorama

{Fore.GREEN}{Style.BRIGHT}ACCESO AL ALMACENAMIENTO:{Style.RESET_ALL}
  {Fore.YELLOW}# Para acceder a archivos del teléfono{Style.RESET_ALL}
  termux-setup-storage
  
  {Fore.YELLOW}# Las imágenes estarán en:{Style.RESET_ALL}
  /sdcard/Download/     - Descargas
  /sdcard/Pictures/     - Fotos
  /sdcard/DCIM/Camera/  - Cámara

{Fore.GREEN}{Style.BRIGHT}RUTAS COMUNES EN ANDROID:{Style.RESET_ALL}
  {Fore.RED}•{Style.RESET_ALL} Almacenamiento interno: /sdcard/
  {Fore.RED}•{Style.RESET_ALL} Descargas: /sdcard/Download/
  {Fore.RED}•{Style.RESET_ALL} Fotos: /sdcard/Pictures/
  {Fore.RED}•{Style.RESET_ALL} Cámara: /sdcard/DCIM/Camera/

{Fore.RED}{Style.BRIGHT}NOTAS IMPORTANTES:{Style.RESET_ALL}
  • Ejecuta 'termux-setup-storage' para acceder a archivos del teléfono
  • Necesitas conexión a internet para la traducción
  • El OCR funciona mejor con imágenes claras y texto legible
"""
    print(help_text)

def print_result(result, terminal_only=False, output_file=None):
    """Imprime o guarda el resultado"""
    
    # Formatear el contenido
    content = f"""
{Fore.GREEN}{Style.BRIGHT}═══════════════════════════════════════════════════════════════
                        RESULTADO DE TRADUCCIÓN
═══════════════════════════════════════════════════════════════{Style.RESET_ALL}

{Fore.CYAN}{Style.BRIGHT}IDIOMA DETECTADO:{Style.RESET_ALL} {result['detected_lang'].upper()}
{Fore.CYAN}{Style.BRIGHT}IDIOMA DESTINO:{Style.RESET_ALL} {result['target_lang'].upper()}

{Fore.YELLOW}{Style.BRIGHT}TEXTO ORIGINAL:{Style.RESET_ALL}
{result['original']}

{Fore.GREEN}{Style.BRIGHT}TEXTO TRADUCIDO:{Style.RESET_ALL}
{result['translated']}

{Fore.GREEN}{Style.BRIGHT}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}
"""
    
    # Contenido para archivo (sin colores)
    file_content = f"""
═══════════════════════════════════════════════════════════════
                        RESULTADO DE TRADUCCIÓN
═══════════════════════════════════════════════════════════════

IDIOMA DETECTADO: {result['detected_lang'].upper()}
IDIOMA DESTINO: {result['target_lang'].upper()}

TEXTO ORIGINAL:
{result['original']}

TEXTO TRADUCIDO:
{result['translated']}

═══════════════════════════════════════════════════════════════
"""
    
    # Mostrar en terminal
    if terminal_only or output_file:
        print(content)
    
    # Guardar en archivo si se especifica
    if output_file:
        translator = ImageTranslator()
        translator.save_to_file(file_content, output_file)
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ Resultado guardado en: {output_file}{Style.RESET_ALL}")

def main():
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('imagen', nargs='?', help='Ruta de la imagen a procesar')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('-t', '--terminal', action='store_true', 
                       help='Mostrar resultado solo en terminal')
    parser.add_argument('-sl', '--source-lang', default='auto', 
                       help='Idioma origen (default: auto)')
    parser.add_argument('-dl', '--dest-lang', default='es', 
                       help='Idioma destino (default: es)')
    parser.add_argument('-h', '--help', action='store_true', 
                       help='Mostrar ayuda')
    
    args = parser.parse_args()
    
    # Mostrar ayuda personalizada
    if args.help or not args.imagen:
        print_colored_help()
        return
    
    # Verificar que el archivo existe
    if not os.path.exists(args.imagen):
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error: No se encuentra el archivo '{args.imagen}'{Style.RESET_ALL}")
        return
    
    # Verificar que al menos se especifique terminal o output
    if not args.terminal and not args.output:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error: Debes especificar -t (terminal) o -o (output){Style.RESET_ALL}")
        return
    
    try:
        print(f"{Fore.CYAN}{Style.BRIGHT}🔍 Procesando imagen: {args.imagen}{Style.RESET_ALL}")
        
        # Mostrar información sobre Termux si es necesario
        if IS_TERMUX:
            print(f"{Fore.BLUE}📱 Ejecutándose en Termux Android{Style.RESET_ALL}")
            
            # Verificar si el usuario ha configurado acceso al almacenamiento
            if not os.path.exists('/sdcard') and '/sdcard/' in args.imagen:
                print(f"{Fore.YELLOW}⚠️  Para acceder a archivos del teléfono, ejecuta: termux-setup-storage{Style.RESET_ALL}")
        
        # Crear instancia del traductor
        translator = ImageTranslator()
        
        # Extraer texto
        print(f"{Fore.YELLOW}📷 Extrayendo texto de la imagen...{Style.RESET_ALL}")
        text = translator.extract_text_from_image(args.imagen)
        
        if not text:
            print(f"{Fore.RED}{Style.BRIGHT}✗ No se encontró texto en la imagen{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Asegúrate de que la imagen tenga texto claro y legible{Style.RESET_ALL}")
            return
        
        # Traducir texto
        print(f"{Fore.YELLOW}🌐 Traduciendo texto...{Style.RESET_ALL}")
        result = translator.translate_text(text, args.source_lang, args.dest_lang)
        
        # Mostrar/guardar resultado
        print_result(result, args.terminal, args.output)
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ ¡Proceso completado exitosamente!{Style.RESET_ALL}")
        
    except FileNotFoundError as e:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error de archivo: {e}{Style.RESET_ALL}")
        if IS_TERMUX:
            print(f"{Fore.YELLOW}💡 Si el archivo está en el teléfono, ejecuta: termux-setup-storage{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Error: {e}{Style.RESET_ALL}")
        if IS_TERMUX:
            print(f"{Fore.YELLOW}💡 Verifica que tesseract esté instalado: pkg install tesseract{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}💡 Asegúrate de tener Tesseract OCR instalado en tu sistema{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
