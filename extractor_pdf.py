import PyPDF2
import os
from pathlib import Path

def extraer_paginas_pdf(archivo_pdf, paginas_deseadas, carpeta_salida=None):
    """
    Extrae páginas específicas de un PDF y las guarda como archivos individuales.
    
    Args:
        archivo_pdf (str): Ruta del archivo PDF original
        paginas_deseadas (list): Lista de números de página a extraer (1-indexado)
        carpeta_salida (str): Carpeta donde guardar los archivos (opcional)
    """
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_pdf):
        print(f"Error: El archivo {archivo_pdf} no existe.")
        return
    
    # Crear carpeta de salida si no existe
    if carpeta_salida is None:
        carpeta_salida = "paginas_extraidas"
    
    Path(carpeta_salida).mkdir(exist_ok=True)
    
    # Obtener el nombre base del archivo sin extensión
    nombre_base = Path(archivo_pdf).stem
    
    try:
        # Abrir el PDF
        with open(archivo_pdf, 'rb') as archivo:
            lector_pdf = PyPDF2.PdfReader(archivo)
            total_paginas = len(lector_pdf.pages)
            
            print(f"PDF cargado: {archivo_pdf}")
            print(f"Total de páginas: {total_paginas}")
            
            # Extraer cada página solicitada
            for num_pagina in paginas_deseadas:
                # Convertir a índice 0-based
                indice_pagina = num_pagina - 1
                
                # Verificar que la página existe
                if indice_pagina < 0 or indice_pagina >= total_paginas:
                    print(f"Advertencia: La página {num_pagina} no existe en el PDF.")
                    continue
                
                # Crear un nuevo PDF con solo esta página
                escritor_pdf = PyPDF2.PdfWriter()
                escritor_pdf.add_page(lector_pdf.pages[indice_pagina])
                
                # Nombre del archivo de salida
                nombre_archivo = f"{nombre_base}_pagina_{num_pagina}.pdf"
                ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
                
                # Guardar la página
                with open(ruta_salida, 'wb') as archivo_salida:
                    escritor_pdf.write(archivo_salida)
                
                print(f"Página {num_pagina} extraída: {ruta_salida}")
    
    except Exception as e:
        print(f"Error al procesar el PDF: {str(e)}")

def main():
    # Configuración
    archivo_pdf = "mi_libro.pdf"  # Cambia por la ruta de tu PDF
    paginas_a_extraer = [80, 81, 83]  # Lista de páginas que quieres extraer
    carpeta_destino = "paginas_extraidas"  # Carpeta donde se guardarán
    
    print("=== Extractor de Páginas PDF ===")
    print(f"Archivo origen: {archivo_pdf}")
    print(f"Páginas a extraer: {paginas_a_extraer}")
    print(f"Carpeta destino: {carpeta_destino}")
    print("-" * 40)
    
    # Ejecutar extracción
    extraer_paginas_pdf(archivo_pdf, paginas_a_extraer, carpeta_destino)
    
    print("-" * 40)
    print("Extracción completada.")

# Versión interactiva
def version_interactiva():
    """Versión interactiva para usar desde la línea de comandos"""
    print("=== Extractor de Páginas PDF (Modo Interactivo) ===")
    
    # Solicitar archivo PDF
    archivo_pdf = input("Ingresa la ruta del archivo PDF: ").strip()
    
    # Solicitar páginas
    print("Ingresa los números de página separados por comas (ej: 80,81,83):")
    entrada_paginas = input("Páginas: ").strip()
    
    try:
        paginas = [int(p.strip()) for p in entrada_paginas.split(',')]
    except ValueError:
        print("Error: Formato de páginas inválido.")
        return
    
    # Solicitar carpeta de salida (opcional)
    carpeta = input("Carpeta de salida (presiona Enter para usar 'paginas_extraidas'): ").strip()
    if not carpeta:
        carpeta = "paginas_extraidas"
    
    # Ejecutar extracción
    extraer_paginas_pdf(archivo_pdf, paginas, carpeta)

if __name__ == "__main__":
    # Puedes cambiar entre main() y version_interactiva()
    main()
    
    # Para usar la versión interactiva, comenta la línea anterior y descomenta:
    # version_interactiva()
