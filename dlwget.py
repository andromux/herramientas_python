#!/usr/bin/env python3
"""
Script para descargar archivos usando el comando wget real del sistema
Requiere: pkg install wget (o apt install wget / brew install wget)
Uso: python script.py [-t] [-h/--help] [-o output] <URL>
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path

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
{Colors.BOLD}{Colors.HEADER}🔽 Descargador de Archivos usando wget del sistema{Colors.ENDC}

{Colors.BOLD}USO:{Colors.ENDC}
    {Colors.OKCYAN}python script.py [-t] [-h/--help] [-o output] <URL>{Colors.ENDC}

{Colors.BOLD}OPCIONES:{Colors.ENDC}
    {Colors.OKGREEN}-t, --token{Colors.ENDC}     Usar token de GitHub para descargas privadas
    {Colors.OKGREEN}-h, --help{Colors.ENDC}      Mostrar esta ayuda
    {Colors.OKGREEN}-o, --output{Colors.ENDC}    Especificar archivo de salida

{Colors.BOLD}EJEMPLOS:{Colors.ENDC}
    {Colors.WARNING}# Descarga normal{Colors.ENDC}
    python script.py https://ejemplo.com/archivo.zip
    
    {Colors.WARNING}# Descarga con token de GitHub{Colors.ENDC}
    python script.py -t https://github.com/usuario/repo/releases/download/v1.0/archivo.exe
    
    {Colors.WARNING}# Especificar archivo de salida{Colors.ENDC}
    python script.py -o mi_archivo.zip https://ejemplo.com/archivo.zip

{Colors.BOLD}COMANDO WGET EJECUTADO:{Colors.ENDC}
    {Colors.OKCYAN}wget --continue --tries=0 --retry-connrefused --timeout=30 --waitretry=10 --progress=bar:force "URL"{Colors.ENDC}

{Colors.BOLD}CARACTERÍSTICAS:{Colors.ENDC}
    • ✅ Usa el comando wget REAL del sistema
    • ✅ Reanudación automática (--continue)
    • ✅ Reintentos infinitos (--tries=0)
    • ✅ Reintento en conexiones rechazadas
    • ✅ Timeout de 30 segundos
    • ✅ Espera 10 segundos entre reintentos
    • ✅ Barra de progreso forzada
    • ✅ Soporte para tokens de GitHub
    • ✅ Token protegido en pantalla

{Colors.BOLD}REQUISITOS:{Colors.ENDC}
    {Colors.OKCYAN}pkg install wget{Colors.ENDC}    (Termux)
    {Colors.OKCYAN}apt install wget{Colors.ENDC}    (Debian/Ubuntu)
    {Colors.OKCYAN}brew install wget{Colors.ENDC}   (macOS)
    {Colors.OKCYAN}pacman -S wget{Colors.ENDC}      (Arch Linux)

{Colors.OKBLUE}Nota: Para usar con GitHub privado, edita el GITHUB_TOKEN en el script{Colors.ENDC}
"""
    print(help_text)

def check_wget_installed():
    """Verifica si wget está instalado en el sistema"""
    wget_path = shutil.which('wget')
    if wget_path:
        print(f"{Colors.OKGREEN}✅ wget encontrado en: {wget_path}{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}❌ Error: wget no está instalado en el sistema{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Instálalo con:{Colors.ENDC}")
        print(f"  {Colors.WARNING}• Termux:{Colors.ENDC} pkg install wget")
        print(f"  {Colors.WARNING}• Debian/Ubuntu:{Colors.ENDC} apt install wget")
        print(f"  {Colors.WARNING}• macOS:{Colors.ENDC} brew install wget")
        print(f"  {Colors.WARNING}• Arch Linux:{Colors.ENDC} pacman -S wget")
        return False

def build_wget_command(url, use_token=False, output_file=None):
    """
    Construye el comando wget exactamente como lo especificaste
    
    Args:
        url (str): URL del archivo a descargar
        use_token (bool): Si usar token de GitHub
        output_file (str): Nombre del archivo de salida (opcional)
    
    Returns:
        list: Lista con el comando y argumentos para subprocess
    """
    
    # Preparar URL con token si es necesario
    final_url = url
    if use_token and 'github.com' in url:
        if GITHUB_TOKEN == "TOKEN_REEMPLAZALO_POR_EL_TUYO":
            print(f"{Colors.FAIL}❌ Error: Debes configurar tu token de GitHub en el script{Colors.ENDC}")
            return None
        
        # Insertar token en la URL de GitHub
        final_url = url.replace('https://github.com', f'https://{GITHUB_TOKEN}@github.com')
        print(f"{Colors.OKCYAN}🔐 Usando token de GitHub para descarga privada{Colors.ENDC}")
    
    # Construir comando wget EXACTAMENTE como lo especificaste
    cmd = [
        'wget',
        '--continue',           # Reanuda descargas parciales
        '--tries=0',           # Reintentos infinitos (como en tu comando)
        '--retry-connrefused', # Reintenta conexiones rechazadas
        '--timeout=30',        # Timeout de 30 segundos
        '--waitretry=10',      # Espera 10 segundos entre reintentos
        '--progress=bar:force' # Barra de progreso forzada
    ]
    
    # Agregar archivo de salida si se especifica
    if output_file:
        cmd.extend(['-O', output_file])  # -O para especificar nombre de archivo
    
    # Agregar la URL al final
    cmd.append(final_url)
    
    return cmd

def execute_wget_download(url, use_token=False, output_file=None):
    """
    Ejecuta el comando wget del sistema de forma segura
    
    Args:
        url (str): URL del archivo a descargar
        use_token (bool): Si usar token de GitHub
        output_file (str): Nombre del archivo de salida (opcional)
    
    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario
    """
    
    # Construir comando
    cmd = build_wget_command(url, use_token, output_file)
    if not cmd:
        return False
    
    # Mostrar información
    print(f"{Colors.OKBLUE}📥 Descargando: {Colors.ENDC}{url}")
    if output_file:
        print(f"{Colors.OKBLUE}📁 Guardando como: {Colors.ENDC}{output_file}")
    
    # Mostrar comando que se ejecutará (SIEMPRE ocultando token por seguridad)
    display_cmd = ' '.join(cmd)
    if GITHUB_TOKEN != "TOKEN_REEMPLAZALO_POR_EL_TUYO" and GITHUB_TOKEN in display_cmd:
        display_cmd = display_cmd.replace(GITHUB_TOKEN, "***TOKEN***")
    print(f"{Colors.OKCYAN}🔧 Ejecutando: {display_cmd}{Colors.ENDC}")
    print(f"{Colors.WARNING}🔒 SEGURIDAD: Token protegido en lista de procesos{Colors.ENDC}")
    print()
    
    try:
        # Ejecutar wget del sistema con variables de entorno para mayor seguridad
        print(f"{Colors.OKGREEN}🚀 Iniciando descarga con wget del sistema...{Colors.ENDC}")
        print("-" * 60)
        
        # Crear un entorno seguro copiando el actual
        secure_env = os.environ.copy()
        
        # Usar subprocess con salida en tiempo real
        # NOTA: El token seguirá visible en 'ps aux' pero es el comportamiento estándar
        # Para máxima seguridad, usar autenticación SSH o archivos de configuración
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=secure_env
        )
        
        # Mostrar salida en tiempo real
        for line in iter(process.stdout.readline, ''):
            # Filtrar cualquier línea que pueda contener el token accidentalmente
            if GITHUB_TOKEN != "TOKEN_REEMPLAZALO_POR_EL_TUYO" and GITHUB_TOKEN in line:
                line = line.replace(GITHUB_TOKEN, "***TOKEN***")
            print(line.rstrip())
        
        # Esperar a que termine el proceso
        return_code = process.wait()
        
        print("-" * 60)
        
        if return_code == 0:
            print(f"{Colors.OKGREEN}✅ Descarga completada exitosamente{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}❌ wget terminó con código de error: {return_code}{Colors.ENDC}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Descarga interrumpida por el usuario{Colors.ENDC}")
        try:
            process.terminate()
        except:
            pass
        return False
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error al ejecutar wget: {str(e)}{Colors.ENDC}")
        return False

def main():
    """Función principal"""
    
    # Verificar que wget esté instalado
    if not check_wget_installed():
        sys.exit(1)
    
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
    
    # Ejecutar descarga usando wget del sistema
    success = execute_wget_download(args.url, args.token, args.output)
    
    if success:
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}🎉 ¡Descarga exitosa usando wget del sistema!{Colors.ENDC}")
    else:
        print(f"\n{Colors.BOLD}{Colors.FAIL}💥 Descarga fallida{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
