### 1. Preparar Termux
```bash
# Actualizar sistema
pkg update && pkg upgrade -y

# Instalar dependencias
pkg install python yt-dlp jq ffmpeg
```


# Mover a PATH (opcional)
```bash
mv ~/ytdl-manager $PREFIX/bin/
```

## 🎯 Uso Básico

### Agregar Canales para Monitoreo
```bash
# Agregar canal de midudev
ytdl-manager add https://youtube.com/@midudev

# Agregar canal de MoureDev
ytdl-manager add https://youtube.com/@mouredev

# Verificar canales agregados
ytdl-manager list
```

### Verificar Nuevos Videos
```bash
# Verificar todos los canales
ytdl-manager check

# Verificar solo un canal específico
ytdl-manager check midudev
```

### Descargar Videos
```bash
# Descargar último video de todos los canales
ytdl-manager download

# Descargar solo de un canal específico
ytdl-manager download midudev

# Descargar en calidad específica
ytdl-manager download --quality 720p --format mp4

# Descargar solo audio
ytdl-manager download --audio-only
```

## 📁 Estructura de Archivos

Después de usar el script, tendrás esta estructura:

```
$HOME/
├── .idyt/                          # Configuración
│   ├── channels.conf               # Lista de canales
│   └── .idyt.log                  # Log de actividades
├── midudev/                       # Videos de midudev
│   ├── Tutorial React 2024.mp4
│   └── JavaScript Moderno.mp4
└── mouredev/                      # Videos de MoureDev
    ├── Python para Principiantes.mp4
    └── Algoritmos Explicados.mp4
```

## 🔧 Comandos Principales

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `add <url>` | Agregar canal | `ytdl-manager add https://youtube.com/@midudev` |
| `remove <canal>` | Remover canal | `ytdl-manager remove midudev` |
| `list` | Listar canales | `ytdl-manager list` |
| `check [canal]` | Verificar nuevos videos | `ytdl-manager check` |
| `download [canal]` | Descargar últimos videos | `ytdl-manager download` |
| `status` | Estado del sistema | `ytdl-manager status` |
| `history [canal]` | Historial de descargas | `ytdl-manager history midudev` |

## ⚙️ Opciones Avanzadas

### Calidades Disponibles
```bash
# Mejor calidad disponible (por defecto)
ytdl-manager download --quality best

# 720p
ytdl-manager download --quality 720p

# 1080p
ytdl-manager download --quality 1080p

# Peor calidad (para ahorrar espacio)
ytdl-manager download --quality worst
```

### Formatos de Video
```bash
# MP4 (recomendado)
ytdl-manager download --format mp4

# WebM
ytdl-manager download --format webm

# MKV
ytdl-manager download --format mkv
```

### Solo Audio
```bash
# Descargar solo audio en MP3
ytdl-manager download --audio-only
```

## 📊 Monitoreo y Control

### Ver Estado General
```bash
ytdl-manager status
```
**Salida esperada:**
```
Estado del sistema:
===================
Canales monitoreados: 2
Videos descargados: 15
Espacio usado en midudev: 2.3G
Espacio usado en mouredev: 1.8G
Última actividad: [2024-07-28 10:30:15] Descargado: midudev - React Hooks Explained
```

### Ver Historial
```bash
# Historial completo
ytdl-manager history

# Historial de un canal específico
ytdl-manager history midudev
```

### Limpiar Sistema
```bash
# Limpiar archivos temporales y rotar logs
ytdl-manager clean
```

## 🔄 Flujo de Trabajo Diario

### 1. Configuración Inicial (Solo una vez)
```bash
# Agregar tus canales favoritos
ytdl-manager add https://youtube.com/@midudev
ytdl-manager add https://youtube.com/@mouredev
ytdl-manager add https://youtube.com/@faztcode

# Verificar que se agregaron
ytdl-manager list
```

### 2. Rutina Diaria
```bash
# Verificar si hay nuevos videos
ytdl-manager check

# Si hay nuevos videos, descargarlos
ytdl-manager download --quality 720p --format mp4

# Ver qué se descargó
ytdl-manager status
```

### 3. Mantenimiento Semanal
```bash
# Limpiar archivos temporales
ytdl-manager clean

# Verificar espacio usado
ytdl-manager status

# Actualizar yt-dlp
ytdl-manager update
```

## 🤖 Automatización con Cron

### Configurar Descargas Automáticas
```bash
# Editar crontab
crontab -e

# Agregar estas líneas para descargas automáticas:
# Verificar nuevos videos cada 6 horas
0 */6 * * * /data/data/com.termux/files/usr/bin/ytdl-manager download --quality 720p

# Limpiar archivos temporales diariamente
0 2 * * * /data/data/com.termux/files/usr/bin/ytdl-manager clean
```

## 🛠️ Solución de Problemas

### Errores Comunes

**Error: "No se puede acceder al canal"**
```bash
# Verificar conectividad
ping google.com

# Actualizar yt-dlp
ytdl-manager update

# Verificar URL del canal manualmente
yt-dlp --list-formats https://youtube.com/@midudev
```

**Error: "Faltan dependencias"**
```bash
# Reinstalar dependencias
pkg install yt-dlp jq ffmpeg python
```

**Error: "No space left on device"**
```bash
# Verificar espacio
df -h

# Limpiar descargas antiguas
rm -rf ~/canal_antiguo/

# Cambiar calidad a menor resolución
ytdl-manager download --quality 720p
```

### Comandos de Diagnóstico
```bash
# Verificar dependencias
which yt-dlp jq python

# Ver logs detallados
tail -f ~/.idyt/.idyt.log

# Probar descarga manual
yt-dlp --list-formats https://youtube.com/@midudev

# Verificar configuración
cat ~/.idyt/channels.conf
```

## 💡 Tips y Trucos

### 1. Configuración Óptima para Termux
```bash
# En ~/.bashrc agregar:
alias ytdl='ytdl-manager'
alias ytcheck='ytdl-manager check'
alias ytdown='ytdl-manager download --quality 720p'
alias ytstatus='ytdl-manager status'
```

### 2. Gestión de Espacio
```bash
# Descargar solo en 720p para ahorrar espacio
ytdl-manager download --quality 720p

# Solo audio para podcasts/charlas
ytdl-manager download --audio-only

# Configurar límite de videos por canal
# (modificar script para agregar --max-downloads 5)
```

### 3. Organización Avanzada
```bash
# Crear carpetas por fecha
mkdir -p ~/Downloads/"$(date +%Y-%m)"

# Usar nombres de archivo personalizados
# (modificar template en el script)
```

### 4. Monitoreo Eficiente
```bash
# Script para notificaciones
#!/bin/bash
NEW_VIDEOS=$(ytdl-manager check | grep "Nuevo video")
if [ -n "$NEW_VIDEOS" ]; then
    echo "¡Nuevos videos disponibles!" 
    ytdl-manager download --quality 720p
fi
```

## 📚 Ejemplos Prácticos

### Ejemplo 1: Setup para Desarrollador
```bash
# Canales de programación
ytdl-manager add https://youtube.com/@midudev
ytdl-manager add https://youtube.com/@mouredev  
ytdl-manager add https://youtube.com/@faztcode

# Descargar en buena calidad
ytdl-manager download --quality 720p --format mp4
```

### Ejemplo 2: Setup para Podcasts
```bash
# Canales de podcasts/charlas
ytdl-manager add https://youtube.com/@channel1
ytdl-manager add https://youtube.com/@channel2

# Solo audio para ahorrar espacio
ytdl-manager download --audio-only
```

### Ejemplo 3: Monitoreo Específico
```bash
# Solo verificar un canal importante
ytdl-manager check midudev

# Descargar solo de ese canal
ytdl-manager download midudev --quality 1080p
```

---

## 🎉 ¡Listo para Usar!

Con esta guía ya puedes:
- ✅ Monitorear automáticamente tus canales favoritos
- ✅ Descargar solo los videos nuevos
- ✅ Organizar descargas por canal
- ✅ Controlar calidad y formato
- ✅ Mantener un historial completo
- ✅ Automatizar el proceso

**Comando de inicio rápido:**
```bash
ytdl-manager add https://youtube.com/@midudev && ytdl-manager download --quality 720p
```
