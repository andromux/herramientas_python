from bs4 import BeautifulSoup

# Abre el archivo HTML
with open('index.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parsear el HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Preparar las líneas del archivo
lines = html_content.splitlines()

# Estructura para almacenar los resultados
headers_info = {f'h{i}': [] for i in range(1, 7)}

# Procesar cada tipo de encabezado
for tag in headers_info:
    for element in soup.find_all(tag):
        text = element.get_text(strip=True)
        found_line = "?"
        for i, line in enumerate(lines):
            if text in line:
                found_line = i + 1
                break
        headers_info[tag].append({'line': found_line, 'text': text})

# Mostrar resultados
for tag, items in headers_info.items():
    print(f"{tag.upper()}: {len(items)} encontrados")
    if items:
        for item in items:
            print(f"  Línea {item['line']}: {item['text']}")
    else:
        print("  No se encontraron encabezados de este tipo.")
