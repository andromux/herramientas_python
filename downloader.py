#!/usr/bin/env python3
"""
Script para descargar archivos con soporte para tokens de GitHub
Uso: python script.py [-t] [-h/--help] <URL>
"""

import argparse
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
import time

# Colores para la ayuda
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Token de GitHub (reemplaza con tu token personal)
GITHUB_TOKEN = "TOKEN_REEMPLAZALO_POR_EL_TUYO"

def print_colored_help():
    """Imprime ayuda colorida y legible"""
    help_text = f"""
{Colors.BOLD}{Colors.HEADER}🔽 Descargador de Archivos con Soporte GitHub{Colors.ENDC}

{Colors.BOLD}USO:{Colors.ENDC}
    {Colors.OKCYAN}python script.py [-t] [-h/--help] <URL>{Colors.ENDC}

{Colors.BOLD}OPCIONES:{Colors.ENDC}
    {Colors.OKGREEN}-t, --token{Colors.ENDC}     Usar token de GitHub para descargas privadas
    {Colors.OKGREEN}-h, --help{Colors.ENDC}      Mostrar esta ayuda
    {Colors.OKGREEN}-o, --output{Colors.ENDC}    Especificar archivo de salida (opcional)

{Colors.BOLD}EJEMPLOS:{Colors.ENDC}
    {Colors.WARNING}# Descarga normal{Colors.ENDC}
    python script.py https://ejemplo.com/archivo.zip
    
    {Colors.WARNING}# Descarga con token de GitHub{Colors.ENDC}
    python script.py -t https://github.com/usuario/repo/releases/download/v1.0/archivo.exe
    
    {Colors.WARNING}# Especificar archivo de salida{Colors.ENDC}
    python script.py -o mi_archivo.zip https://ejemplo.com/descarga.zip

{Colors.BOLD}CARACTERÍSTICAS:{Colors.ENDC}
    • ✅ Reanudación de descargas (--continue)
    • ✅ Reintentos automáticos
    • ✅ Timeout configurable
    • ✅ Barra de progreso
    • ✅ Soporte para tokens de GitHub

{Colors.OKBLUE}Nota: Para usar con GitHub privado, edita el GITHUB_TOKEN en el script{Colors.ENDC}
"""
    print(help_text)

def format_bytes(bytes_size):
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def progress_hook(block_num, block_size, total_size):
    """Hook para mostrar progreso de descarga"""
    if total_size <= 0:
        return
    
    downloaded = block_num * block_size
    if downloaded > total_size:
        downloaded = total_size
    
    percent = (downloaded / total_size) * 100
    bar_length = 50
    filled_length = int(bar_length * downloaded // total_size)
    
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'\r{Colors.OKGREEN}[{bar}] {percent:.1f}% ({format_bytes(downloaded)}/{format_bytes(total_size)}){Colors.ENDC}', end='')
    
    if downloaded >= total_size:
        print()  # Nueva línea al completar

def download_file(url, use_token=False, output_file=None, max_retries=3):
    """
    Descarga un archivo con opciones avanzadas
    
    Args:
        url (str): URL del archivo a descargar
        use_token (bool): Si usar token de GitHub
        output_file (str): Nombre del archivo de salida (opcional)
        max_retries (int): Número máximo de reintentos
    """
    
    # Preparar URL con token si es necesario
    if use_token and 'github.com' in url:
        if GITHUB_TOKEN == "TOKEN_REEMPLAZALO_POR_EL_TUYO":
            print(f"{Colors.FAIL}❌ Error: Debes configurar tu token de GitHub en el script{Colors.ENDC}")
            return False
        
        # Insertar token en la URL de GitHub
        url = url.replace('https://github.com', f'https://{GITHUB_TOKEN}@github.com')
        print(f"{Colors.OKCYAN}🔐 Usando token de GitHub para descarga privada{Colors.ENDC}")
    
    # Determinar nombre del archivo
    if not output_file:
        parsed_url = urllib.parse.urlparse(url)
        output_file = os.path.basename(parsed_url.path) or 'downloaded_file'
    
    print(f"{Colors.OKBLUE}📥 Descargando: {Colors.ENDC}{url}")
    print(f"{Colors.OKBLUE}📁 Guardando como: {Colors.ENDC}{output_file}")
    
    # Configurar headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            # Crear request con headers
            req = urllib.request.Request(url, headers=headers)
            
            # Verificar si el archivo ya existe para reanudación
            resume_pos = 0
            if os.path.exists(output_file):
                resume_pos = os.path.getsize(output_file)
                if resume_pos > 0:
                    headers['Range'] = f'bytes={resume_pos}-'
                    req.add_header('Range', f'bytes={resume_pos}-')
                    print(f"{Colors.WARNING}⏯️  Reanudando descarga desde {format_bytes(resume_pos)}{Colors.ENDC}")
            
            # Realizar descarga
            print(f"{Colors.OKCYAN}🔄 Iniciando descarga... (Intento {attempt + 1}/{max_retries}){Colors.ENDC}")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get('content-length', 0))
                if resume_pos > 0:
                    total_size += resume_pos
                
                print(f"{Colors.OKGREEN}📊 Tamaño total: {format_bytes(total_size)}{Colors.ENDC}")
                
                # Abrir archivo en modo append si se reanuda
                mode = 'ab' if resume_pos > 0 else 'wb'
                with open(output_file, mode) as f:
                    downloaded = resume_pos
                    block_size = 8192
                    
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        
                        f.write(buffer)
                        downloaded += len(buffer)
                        
                        # Mostrar progreso
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            bar_length = 50
                            filled_length = int(bar_length * downloaded // total_size)
                            bar = '█' * filled_length + '-' * (bar_length - filled_length)
                            print(f'\r{Colors.OKGREEN}[{bar}] {percent:.1f}% ({format_bytes(downloaded)}/{format_bytes(total_size)}){Colors.ENDC}', end='')
            
            print(f"\n{Colors.OKGREEN}✅ Descarga completada: {output_file}{Colors.ENDC}")
            return True
            
        except urllib.error.HTTPError as e:
            if e.code == 416:  # Range not satisfiable
                print(f"\n{Colors.WARNING}⚠️  El archivo ya está completamente descargado{Colors.ENDC}")
                return True
            else:
                print(f"\n{Colors.FAIL}❌ Error HTTP {e.code}: {e.reason}{Colors.ENDC}")
        except urllib.error.URLError as e:
            print(f"\n{Colors.FAIL}❌ Error de conexión: {e.reason}{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error inesperado: {str(e)}{Colors.ENDC}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 10
            print(f"{Colors.WARNING}⏳ Esperando {wait_time} segundos antes del siguiente intento...{Colors.ENDC}")
            time.sleep(wait_time)
    
    print(f"{Colors.FAIL}❌ Descarga fallida después de {max_retries} intentos{Colors.ENDC}")
    return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(add_help=False)  # Deshabilitamos la ayuda por defecto
    
    parser.add_argument('url', nargs='?', help='URL del archivo a descargar')
    parser.add_argument('-t', '--token', action='store_true', help='Usar token de GitHub')
    parser.add_argument('-h', '--help', action='store_true', help='Mostrar ayuda')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    
    args = parser.parse_args()
    
    # Mostrar ayuda personalizada
    if args.help or not args.url:
        print_colored_help()
        return
    
    # Validar URL
    if not args.url.startswith(('http://', 'https://')):
        print(f"{Colors.FAIL}❌ Error: La URL debe comenzar con http:// o https://{Colors.ENDC}")
        return
    
    # Realizar descarga
    success = download_file(args.url, args.token, args.output)
    
    if success:
        print(f"{Colors.BOLD}{Colors.OKGREEN}🎉 ¡Descarga exitosa!{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}{Colors.FAIL}💥 Descarga fallida{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
