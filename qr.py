#!/usr/bin/env python3
"""
Generador de códigos QR desde línea de comandos
Uso: python qr.py <enlace_o_texto> [nombre_archivo]
"""

import sys
import qrcode
from PIL import Image
import os
from datetime import datetime

def generar_qr(texto, nombre_archivo=None):
    """
    Genera un código QR y lo guarda como PNG
    
    Args:
        texto (str): El texto o enlace a codificar
        nombre_archivo (str): Nombre del archivo de salida (opcional)
    """
    try:
        # Configuración del QR
        qr = qrcode.QRCode(
            version=1,  # Controla el tamaño (1 es el más pequeño)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # ~7% corrección de errores
            box_size=10,  # Tamaño de cada "caja" del QR
            border=4,     # Grosor del borde
        )
        
        # Agregar datos al QR
        qr.add_data(texto)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Determinar nombre del archivo
        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"qr_{timestamp}.png"
        elif not nombre_archivo.endswith('.png'):
            nombre_archivo += '.png'
        
        # Guardar imagen
        img.save(nombre_archivo)
        
        # Información sobre el archivo generado
        tamaño_archivo = os.path.getsize(nombre_archivo)
        tamaño_kb = tamaño_archivo / 1024
        
        print(f"✅ QR generado exitosamente:")
        print(f"   📁 Archivo: {nombre_archivo}")
        print(f"   📏 Tamaño: {tamaño_kb:.1f} KB ({tamaño_archivo} bytes)")
        print(f"   📝 Contenido: {texto[:50]}{'...' if len(texto) > 50 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al generar QR: {str(e)}")
        return False

def mostrar_ayuda():
    """Muestra información de uso del script"""
    print("🔳 Generador de Códigos QR")
    print("\nUso:")
    print("  python qr.py <enlace_o_texto> [nombre_archivo]")
    print("\nEjemplos:")
    print("  python qr.py https://google.com")
    print("  python qr.py https://github.com mi_qr")
    print("  python qr.py \"Mi texto personalizado\" texto_qr.png")
    print("\nNotas:")
    print("  • Si no especificas nombre, se genera automáticamente")
    print("  • La extensión .png se agrega automáticamente si no la incluyes")
    print("  • Usa comillas para textos con espacios")

def main():
    """Función principal del script"""
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar al menos un enlace o texto")
        mostrar_ayuda()
        sys.exit(1)
    
    # Manejar argumentos especiales
    if sys.argv[1] in ['-h', '--help', 'help']:
        mostrar_ayuda()
        sys.exit(0)
    
    # Obtener argumentos
    texto = sys.argv[1]
    nombre_archivo = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validar que el texto no esté vacío
    if not texto.strip():
        print("❌ Error: El texto no puede estar vacío")
        sys.exit(1)
    
    # Generar QR
    if generar_qr(texto, nombre_archivo):
        print("\n💡 Tip: Puedes ver la imagen con 'termux-open <archivo.png>'")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
