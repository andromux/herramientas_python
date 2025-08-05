#!/usr/bin/env python3
"""
Conversor de Markdown a HTML
Convierte archivos Markdown (.md) a HTML con estructura completa.

Uso: python markdown_to_html.py archivo.md salida.html
"""

import sys
import re
import os
from pathlib import Path
from typing import List, Tuple


class MarkdownToHTML:
    """Conversor robusto de Markdown a HTML."""
    
    def __init__(self):
        """Inicializa el conversor con patrones regex para elementos Markdown."""
        self.patterns = {
            # Encabezados (H1-H6)
            'headers': [
                (re.compile(r'^#{6}\s+(.+)$', re.MULTILINE), r'<h6>\1</h6>'),
                (re.compile(r'^#{5}\s+(.+)$', re.MULTILINE), r'<h5>\1</h5>'),
                (re.compile(r'^#{4}\s+(.+)$', re.MULTILINE), r'<h4>\1</h4>'),
                (re.compile(r'^#{3}\s+(.+)$', re.MULTILINE), r'<h3>\1</h3>'),
                (re.compile(r'^#{2}\s+(.+)$', re.MULTILINE), r'<h2>\1</h2>'),
                (re.compile(r'^#{1}\s+(.+)$', re.MULTILINE), r'<h1>\1</h1>'),
            ],
            # Texto en negrita y cursiva
            'bold_italic': re.compile(r'\*\*\*(.+?)\*\*\*'),
            'bold': re.compile(r'\*\*(.+?)\*\*'),
            'italic': re.compile(r'\*(.+?)\*'),
            # Enlaces
            'links': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            # Imágenes
            'images': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
            # Código inline
            'inline_code': re.compile(r'`([^`]+)`'),
            # Líneas horizontales
            'horizontal_rule': re.compile(r'^---+$', re.MULTILINE),
            # Citas
            'blockquote': re.compile(r'^>\s+(.+)$', re.MULTILINE),
            # Listas no ordenadas
            'unordered_list': re.compile(r'^[\*\-\+]\s+(.+)$', re.MULTILINE),
            # Listas ordenadas
            'ordered_list': re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE),
        }
    
    def read_file(self, file_path: str) -> str:
        """
        Lee el contenido del archivo Markdown.
        
        Args:
            file_path: Ruta del archivo Markdown
            
        Returns:
            Contenido del archivo como string
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            UnicodeDecodeError: Si hay problemas de codificación
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo '{file_path}' no se encontró.")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Error de codificación en el archivo '{file_path}': {e}")
    
    def process_code_blocks(self, content: str) -> Tuple[str, List[str]]:
        """
        Procesa bloques de código para evitar conflictos con otros patrones.
        
        Args:
            content: Contenido Markdown
            
        Returns:
            Tupla con contenido procesado y lista de bloques de código
        """
        code_blocks = []
        code_block_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        
        def replace_code_block(match):
            language = match.group(1) if match.group(1) else ''
            code_content = match.group(2)
            placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
            
            if language:
                html_block = f'<pre><code class="language-{language}">{self.escape_html(code_content)}</code></pre>'
            else:
                html_block = f'<pre><code>{self.escape_html(code_content)}</code></pre>'
            
            code_blocks.append(html_block)
            return placeholder
        
        processed_content = code_block_pattern.sub(replace_code_block, content)
        return processed_content, code_blocks
    
    def restore_code_blocks(self, content: str, code_blocks: List[str]) -> str:
        """
        Restaura los bloques de código procesados.
        
        Args:
            content: Contenido con placeholders
            code_blocks: Lista de bloques de código HTML
            
        Returns:
            Contenido con bloques de código restaurados
        """
        for i, block in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            content = content.replace(placeholder, block)
        return content
    
    def escape_html(self, text: str) -> str:
        """
        Escapa caracteres HTML especiales.
        
        Args:
            text: Texto a escapar
            
        Returns:
            Texto con caracteres escapados
        """
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def process_lists(self, content: str) -> str:
        """
        Procesa listas ordenadas y no ordenadas.
        
        Args:
            content: Contenido Markdown
            
        Returns:
            Contenido con listas convertidas a HTML
        """
        lines = content.split('\n')
        result = []
        in_ul = False
        in_ol = False
        
        for line in lines:
            # Lista no ordenada
            if re.match(r'^[\*\-\+]\s+', line):
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append('<ul>')
                    in_ul = True
                item_text = re.sub(r'^[\*\-\+]\s+', '', line)
                result.append(f'  <li>{item_text}</li>')
            
            # Lista ordenada
            elif re.match(r'^\d+\.\s+', line):
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append('<ol>')
                    in_ol = True
                item_text = re.sub(r'^\d+\.\s+', '', line)
                result.append(f'  <li>{item_text}</li>')
            
            # Línea normal
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)
        
        # Cerrar listas abiertas
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def convert_to_html(self, markdown_content: str) -> str:
        """
        Convierte contenido Markdown a HTML.
        
        Args:
            markdown_content: Contenido en formato Markdown
            
        Returns:
            Contenido convertido a HTML
        """
        # Procesar bloques de código primero
        content, code_blocks = self.process_code_blocks(markdown_content)
        
        # Procesar listas
        content = self.process_lists(content)
        
        # Aplicar patrones de conversión
        
        # Encabezados (del más específico al menos específico)
        for pattern, replacement in self.patterns['headers']:
            content = pattern.sub(replacement, content)
        
        # Texto en negrita, cursiva y negrita+cursiva
        content = self.patterns['bold_italic'].sub(r'<strong><em>\1</em></strong>', content)
        content = self.patterns['bold'].sub(r'<strong>\1</strong>', content)
        content = self.patterns['italic'].sub(r'<em>\1</em>', content)
        
        # Enlaces
        content = self.patterns['links'].sub(r'<a href="\2">\1</a>', content)
        
        # Imágenes
        content = self.patterns['images'].sub(r'<img src="\2" alt="\1">', content)
        
        # Código inline
        content = self.patterns['inline_code'].sub(r'<code>\1</code>', content)
        
        # Líneas horizontales
        content = self.patterns['horizontal_rule'].sub('<hr>', content)
        
        # Citas
        content = self.patterns['blockquote'].sub(r'<blockquote>\1</blockquote>', content)
        
        # Procesar párrafos
        content = self.process_paragraphs(content)
        
        # Restaurar bloques de código
        content = self.restore_code_blocks(content, code_blocks)
        
        return content
    
    def process_paragraphs(self, content: str) -> str:
        """
        Convierte texto en párrafos HTML.
        
        Args:
            content: Contenido HTML parcialmente procesado
            
        Returns:
            Contenido con párrafos procesados
        """
        lines = content.split('\n')
        result = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # Línea vacía o elemento HTML
            if not line or line.startswith('<'):
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph).strip()
                    if paragraph_text:
                        result.append(f'<p>{paragraph_text}</p>')
                    current_paragraph = []
                
                if line:
                    result.append(line)
            else:
                current_paragraph.append(line)
        
        # Procesar último párrafo si existe
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph).strip()
            if paragraph_text:
                result.append(f'<p>{paragraph_text}</p>')
        
        return '\n'.join(result)
    
    def create_html_document(self, html_content: str, title: str = "Documento") -> str:
        """
        Crea un documento HTML completo.
        
        Args:
            html_content: Contenido HTML del body
            title: Título del documento
            
        Returns:
            Documento HTML completo
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 20px;
            font-style: italic;
        }}
        
        ul, ol {{
            padding-left: 20px;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    def save_html(self, html_content: str, output_path: str) -> None:
        """
        Guarda el contenido HTML en un archivo.
        
        Args:
            html_content: Contenido HTML completo
            output_path: Ruta del archivo de salida
            
        Raises:
            IOError: Si no se puede escribir el archivo
        """
        try:
            # Crear directorio si no existe
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
                
            print(f"✅ Archivo HTML generado exitosamente: {output_path}")
            
        except IOError as e:
            raise IOError(f"Error al escribir el archivo '{output_path}': {e}")
    
    def convert_file(self, input_path: str, output_path: str) -> None:
        """
        Convierte un archivo Markdown a HTML.
        
        Args:
            input_path: Ruta del archivo Markdown de entrada
            output_path: Ruta del archivo HTML de salida
        """
        try:
            # Validar archivo de entrada
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"El archivo '{input_path}' no existe.")
            
            if not input_path.lower().endswith('.md'):
                print("⚠️  Advertencia: El archivo no tiene extensión .md")
            
            # Leer archivo Markdown
            print(f"📖 Leyendo archivo: {input_path}")
            markdown_content = self.read_file(input_path)
            
            # Convertir a HTML
            print("🔄 Convirtiendo Markdown a HTML...")
            html_content = self.convert_to_html(markdown_content)
            
            # Crear documento HTML completo
            title = Path(input_path).stem
            full_html = self.create_html_document(html_content, title)
            
            # Guardar archivo HTML
            self.save_html(full_html, output_path)
            
        except Exception as e:
            print(f"❌ Error durante la conversión: {e}")
            sys.exit(1)


def main():
    """Función principal del script."""
    if len(sys.argv) != 3:
        print("Uso: python markdown_to_html.py <archivo.md> <salida.html>")
        print("\nEjemplo:")
        print("  python markdown_to_html.py documento.md index.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Crear instancia del conversor
    converter = MarkdownToHTML()
    
    # Realizar conversión
    converter.convert_file(input_file, output_file)


if __name__ == "__main__":
    main()
