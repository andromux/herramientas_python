#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor HTTP Moderno y Avanzado
Versión mejorada del http.server de Python con funcionalidades adicionales
"""

import argparse
import contextlib
import datetime
import http.server
import json
import os
import socket
import socketserver
import sys
import threading
import time
import urllib.parse
from pathlib import Path


class Colors:
    """Códigos de color ANSI para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'


def colored_print(text, color=Colors.ENDC, bold=False):
    """Imprime texto con colores"""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.ENDC}")


def get_local_ip():
    """Obtiene la IP local del dispositivo"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


class ModernHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP mejorado con logging colorizado y funcionalidades adicionales"""
    
    def __init__(self, *args, enable_cors=False, enable_json=False, custom_headers=None, **kwargs):
        self.enable_cors = enable_cors
        self.enable_json = enable_json
        self.custom_headers = custom_headers or {}
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Logging colorizado con timestamps"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = format % args
        
        # Colorear según el código de estado
        if "200" in message:
            color = Colors.OKGREEN
        elif "404" in message:
            color = Colors.WARNING
        elif any(code in message for code in ["500", "501", "502"]):
            color = Colors.FAIL
        else:
            color = Colors.OKCYAN
            
        colored_print(f"[{timestamp}] {self.address_string()} - {message}", color)
    
    def end_headers(self):
        """Añade headers personalizados y CORS si está habilitado"""
        if self.enable_cors:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        # Headers personalizados
        for header, value in self.custom_headers.items():
            self.send_header(header, value)
            
        super().end_headers()
    
    def do_OPTIONS(self):
        """Maneja preflight requests para CORS"""
        if self.enable_cors:
            self.send_response(200)
            self.end_headers()
        else:
            super().do_OPTIONS()
    
    def do_GET(self):
        """GET mejorado con soporte para endpoints especiales"""
        if self.enable_json and self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def handle_api_request(self):
        """Maneja requests a endpoints de API simple"""
        if self.path == '/api/status':
            self.send_json_response({
                'status': 'ok',
                'timestamp': datetime.datetime.now().isoformat(),
                'server': 'Servidor HTTP Moderno Python'
            })
        elif self.path == '/api/info':
            self.send_json_response({
                'directory': self.directory,
                'files_count': len(list(Path(self.directory).rglob('*'))),
                'server_time': datetime.datetime.now().isoformat()
            })
        else:
            self.send_json_response({'error': 'Endpoint no encontrado'}, 404)
    
    def send_json_response(self, data, status=200):
        """Envía respuesta JSON"""
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-length', str(len(json_data.encode())))
        self.end_headers()
        self.wfile.write(json_data.encode())


class ModernHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Servidor HTTP moderno con threading"""
    daemon_threads = True
    allow_reuse_address = True
    
    def __init__(self, *args, **kwargs):
        self.start_time = datetime.datetime.now()
        super().__init__(*args, **kwargs)


def create_handler_class(directory, enable_cors, enable_json, custom_headers):
    """Factory para crear clase handler con configuración"""
    class ConfiguredHandler(ModernHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            kwargs.update({
                'directory': directory,
                'enable_cors': enable_cors,
                'enable_json': enable_json,
                'custom_headers': custom_headers
            })
            super().__init__(*args, **kwargs)
    
    return ConfiguredHandler


def print_banner():
    """Imprime banner de inicio"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║           🚀 SERVIDOR HTTP MODERNO PYTHON 🚀              ║
║                   Versión Avanzada                        ║
╚═══════════════════════════════════════════════════════════╝
    """
    colored_print(banner, Colors.HEADER, bold=True)


def print_server_info(host, port, directory, local_ip):
    """Imprime información del servidor"""
    colored_print("\n📋 INFORMACIÓN DEL SERVIDOR:", Colors.OKBLUE, bold=True)
    colored_print(f"  • Directorio: {directory}", Colors.OKCYAN)
    colored_print(f"  • Puerto: {port}", Colors.OKCYAN)
    colored_print(f"  • Host: {host}", Colors.OKCYAN)
    
    colored_print("\n🌐 URLS DE ACCESO:", Colors.OKBLUE, bold=True)
    colored_print(f"  • Local:      http://localhost:{port}/", Colors.OKGREEN)
    colored_print(f"  • Red Local:  http://{local_ip}:{port}/", Colors.OKGREEN)
    
    colored_print("\n🔧 ENDPOINTS ESPECIALES:", Colors.OKBLUE, bold=True)
    colored_print(f"  • Estado API: http://{local_ip}:{port}/api/status", Colors.WARNING)
    colored_print(f"  • Info API:   http://{local_ip}:{port}/api/info", Colors.WARNING)
    
    colored_print("\n⚡ Para detener el servidor presiona Ctrl+C", Colors.GRAY)
    colored_print("=" * 60, Colors.GRAY)


def custom_help_formatter(prog):
    """Formatter personalizado para argparse con colores"""
    return argparse.RawDescriptionHelpFormatter(prog, max_help_position=35, width=100)


def create_parser():
    """Crea el parser de argumentos con ayuda colorizada"""
    description = f"""{Colors.HEADER}{Colors.BOLD}🚀 SERVIDOR HTTP MODERNO PYTHON{Colors.ENDC}

{Colors.OKCYAN}Un servidor HTTP avanzado basado en el módulo http.server de Python
con funcionalidades modernas, logging colorizado y endpoints de API.{Colors.ENDC}

{Colors.OKBLUE}{Colors.BOLD}CARACTERÍSTICAS:{Colors.ENDC}
  • Threading automático para múltiples conexiones
  • Logging colorizado con timestamps
  • Soporte CORS opcional
  • Endpoints de API simples
  • Headers HTTP personalizados
  • Detección automática de IP local
  • Interfaz de ayuda mejorada

{Colors.OKGREEN}{Colors.BOLD}EJEMPLOS DE USO:{Colors.ENDC}
  {Colors.GRAY}# Servidor básico en puerto 8000{Colors.ENDC}
  python servidor.py

  {Colors.GRAY}# Puerto personalizado con CORS{Colors.ENDC}
  python servidor.py -p 3000 --cors

  {Colors.GRAY}# Directorio específico con API habilitada{Colors.ENDC}
  python servidor.py -d /home/user/web --api

  {Colors.GRAY}# Servidor completo con todas las opciones{Colors.ENDC}
  python servidor.py -p 8080 -b 0.0.0.0 -d ./public --cors --api --header "X-Server: MiServidor"
"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=custom_help_formatter,
        add_help=False  # Deshabilitamos help automático para personalizarlo
    )
    
    # Grupo de ayuda personalizado
    help_group = parser.add_argument_group(
        f'{Colors.BOLD}{Colors.HEADER}AYUDA Y INFORMACIÓN{Colors.ENDC}'
    )
    help_group.add_argument(
        '-h', '--help',
        action='help',
        help=f'{Colors.OKCYAN}Muestra este mensaje de ayuda y sale{Colors.ENDC}'
    )
    
    # Grupo de configuración básica
    basic_group = parser.add_argument_group(
        f'{Colors.BOLD}{Colors.OKBLUE}CONFIGURACIÓN BÁSICA{Colors.ENDC}'
    )
    basic_group.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        metavar='PUERTO',
        help=f'{Colors.OKCYAN}Puerto del servidor (default: 8000){Colors.ENDC}'
    )
    basic_group.add_argument(
        '-b', '--bind',
        default='',
        metavar='IP',
        help=f'{Colors.OKCYAN}IP de bind (default: todas las interfaces){Colors.ENDC}'
    )
    basic_group.add_argument(
        '-d', '--directory',
        default=os.getcwd(),
        metavar='DIR',
        help=f'{Colors.OKCYAN}Directorio a servir (default: directorio actual){Colors.ENDC}'
    )
    
    # Grupo de funcionalidades avanzadas
    advanced_group = parser.add_argument_group(
        f'{Colors.BOLD}{Colors.WARNING}FUNCIONALIDADES AVANZADAS{Colors.ENDC}'
    )
    advanced_group.add_argument(
        '--cors',
        action='store_true',
        help=f'{Colors.OKCYAN}Habilita headers CORS para desarrollo web{Colors.ENDC}'
    )
    advanced_group.add_argument(
        '--api',
        action='store_true',
        help=f'{Colors.OKCYAN}Habilita endpoints de API simples (/api/status, /api/info){Colors.ENDC}'
    )
    advanced_group.add_argument(
        '--header',
        action='append',
        metavar='HEADER',
        help=f'{Colors.OKCYAN}Añade header HTTP personalizado (formato: "Nombre: Valor"){Colors.ENDC}'
    )
    advanced_group.add_argument(
        '--no-colors',
        action='store_true',
        help=f'{Colors.OKCYAN}Deshabilita colores en la salida{Colors.ENDC}'
    )
    
    return parser


def parse_custom_headers(header_list):
    """Parsea headers personalizados desde argumentos"""
    headers = {}
    if header_list:
        for header in header_list:
            if ':' in header:
                name, value = header.split(':', 1)
                headers[name.strip()] = value.strip()
            else:
                colored_print(f"⚠️  Header inválido ignorado: {header}", Colors.WARNING)
    return headers


def main():
    """Función principal"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Deshabilitar colores si se solicita
    if args.no_colors:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Mostrar banner
    print_banner()
    
    # Validar directorio
    if not os.path.isdir(args.directory):
        colored_print(f"❌ Error: El directorio '{args.directory}' no existe", Colors.FAIL, bold=True)
        sys.exit(1)
    
    # Parsear headers personalizados
    custom_headers = parse_custom_headers(args.header)
    
    # Configurar servidor
    try:
        # Determinar familia de direcciones
        server_class = ModernHTTPServer
        if args.bind:
            server_class.address_family, addr = http.server._get_best_family(args.bind, args.port)
        else:
            addr = ('', args.port)
        
        # Crear handler class configurado
        handler_class = create_handler_class(
            args.directory, 
            args.cors, 
            args.api, 
            custom_headers
        )
        
        # Crear y configurar servidor
        with server_class(addr, handler_class) as httpd:
            host, port = httpd.socket.getsockname()[:2]
            local_ip = get_local_ip()
            
            # Mostrar información
            print_server_info(host or 'all interfaces', port, args.directory, local_ip)
            
            # Iniciar servidor
            colored_print("\n🚀 Servidor iniciado correctamente!", Colors.OKGREEN, bold=True)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                colored_print("\n\n⏹️  Deteniendo servidor...", Colors.WARNING, bold=True)
                colored_print("✅ Servidor detenido correctamente", Colors.OKGREEN)
                sys.exit(0)
                
    except OSError as e:
        if e.errno == 48:  # Address already in use
            colored_print(f"❌ Error: El puerto {args.port} ya está en uso", Colors.FAIL, bold=True)
            colored_print("💡 Prueba con otro puerto usando -p <puerto>", Colors.WARNING)
        else:
            colored_print(f"❌ Error del sistema: {e}", Colors.FAIL, bold=True)
        sys.exit(1)
    except Exception as e:
        colored_print(f"❌ Error inesperado: {e}", Colors.FAIL, bold=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
