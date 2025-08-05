# Instrucciones de uso

Conversor de fuentes TTF a formato WOFF2 optimizado para web. Aquí te explico cómo usarlo:

## Requisitos previos

Necesitas instalar:
- Python 3
- La biblioteca fonttools y brotli, que puedes instalar con:
  ```
  pip install fonttools brotli
  ```

## Uso básico

El script puede utilizarse de la siguiente manera:

```bash
python woff2.py <archivo_o_patron_ttf> [opciones]
```

### Ejemplos de uso:

**Convertir un solo archivo:**
```bash
python woff2.py ruta/al/archivo.ttf
```

**Convertir todos los archivos TTF en un directorio:**
```bash
python woff2.py "directorio/*.ttf"
```

**Especificar un directorio de salida:**
```bash
python woff2.py "archivos/*.ttf" -d directorio_salida
```

**Convertir archivos recursivamente en subdirectorios:**
```bash
python woff2.py "directorio/*.ttf" -r
```

## Opciones disponibles

- `-o, --output` - Especifica el archivo de salida o directorio para guardar los archivos WOFF2
- `-d, --directory` - Directorio para guardar los archivos WOFF2 convertidos
- `--no-optimize` - Desactiva las optimizaciones adicionales
- `-r, --recursive` - Busca archivos TTF recursivamente en subdirectorios

## Funcionamiento

El script realiza las siguientes operaciones:
1. Busca los archivos TTF según el patrón especificado
2. Convierte cada archivo a formato WOFF2
3. Aplica optimizaciones eliminando tablas innecesarias para web (a menos que se use --no-optimize)
4. Muestra información sobre el tamaño original, nuevo y el porcentaje de reducción

El programa mostrará un resumen de los resultados de la conversión, incluyendo los tamaños de archivo y el porcentaje de reducción logrado.