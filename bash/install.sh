#!/bin/bash

# Script de instalación para YouTube Channel Downloader CLI

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== YouTube Channel Downloader CLI - Instalador ===${NC}"
echo

# Verificar si estamos en Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}Advertencia: Este script está optimizado para Termux${NC}"
fi

echo -e "${BLUE}1. Actualizando paquetes...${NC}"
pkg update && pkg upgrade -y

echo -e "${BLUE}2. Instalando dependencias...${NC}"
pkg install -y python yt-dlp jq ffmpeg

echo -e "${BLUE}3. Verificando instalación...${NC}"
if command -v yt-dlp &> /dev/null && command -v jq &> /dev/null; then
    echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}✗ Error en la instalación de dependencias${NC}"
    exit 1
fi

echo -e "${BLUE}4. Descargando script principal...${NC}"
INSTALL_DIR="$PREFIX/bin"
SCRIPT_NAME="ytdl-manager"

# Descargar el script directamente (método recomendado)
curl -L -o "$INSTALL_DIR/$SCRIPT_NAME" "https://raw.githubusercontent.com/tu-usuario/tu-repo/main/ytdl-manager.sh"

# Verificar si la descarga falló y crear el script localmente
if [ $? -ne 0 ] || [ ! -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo -e "${YELLOW}Descarga falló, creando script localmente...${NC}"
    
    # Crear script local simplificado
    cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'EOF'
#!/bin/bash

# YouTube Channel Auto Downloader CLI
CONFIG_DIR="$HOME/.idyt"
LOG_FILE="$CONFIG_DIR/.idyt.log"
CHANNELS_FILE="$CONFIG_DIR/channels.conf"
DOWNLOADS_DIR="$HOME"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$CONFIG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

show_help() {
    cat << HELP
${BLUE}YouTube Channel Auto Downloader CLI${NC}

${YELLOW}COMANDOS:${NC}
    add <url>        - Agregar canal
    remove <name>    - Remover canal  
    list            - Listar canales
    check [name]    - Verificar nuevos videos
    download [name] - Descargar videos
    status          - Estado del sistema
    history [name]  - Historial
    clean           - Limpiar temporales
    update          - Actualizar yt-dlp

${YELLOW}OPCIONES:${NC}
    -q, --quality <calidad>  - 720p, 1080p, best, worst
    -f, --format <formato>   - mp4, webm, mkv
    -a, --audio-only        - Solo audio
    -h, --help              - Ayuda

${YELLOW}EJEMPLOS:${NC}
    $0 add https://youtube.com/@midudev
    $0 download --quality 720p
HELP
}

check_dependencies() {
    local missing=()
    command -v yt-dlp &> /dev/null || missing+=("yt-dlp")
    command -v jq &> /dev/null || missing+=("jq")
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Faltan dependencias: ${missing[*]}${NC}"
        echo "Instala con: pkg install yt-dlp jq"
        exit 1
    fi
}

get_channel_name() {
    local url="$1"
    if [[ "$url" =~ @([^/]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$url" =~ /c/([^/]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo "unknown_channel"
    fi
}

add_channel() {
    local url="$1"
    [ -z "$url" ] && { echo -e "${RED}URL requerida${NC}"; exit 1; }
    
    local channel_name=$(get_channel_name "$url")
    
    if grep -q "^$channel_name:" "$CHANNELS_FILE" 2>/dev/null; then
        echo -e "${YELLOW}Canal '$channel_name' ya existe${NC}"
        return
    fi
    
    echo -e "${BLUE}Verificando canal...${NC}"
    if ! yt-dlp --quiet --simulate --playlist-items 1 "$url" &>/dev/null; then
        echo -e "${RED}Error: URL inválida o canal inaccesible${NC}"
        exit 1
    fi
    
    echo "$channel_name:$url:" >> "$CHANNELS_FILE"
    mkdir -p "$DOWNLOADS_DIR/$channel_name"
    
    echo -e "${GREEN}Canal '$channel_name' agregado${NC}"
    log "Canal agregado: $channel_name ($url)"
}

remove_channel() {
    local channel_name="$1"
    [ -z "$channel_name" ] && { echo -e "${RED}Nombre requerido${NC}"; exit 1; }
    
    if ! grep -q "^$channel_name:" "$CHANNELS_FILE" 2>/dev/null; then
        echo -e "${RED}Canal '$channel_name' no encontrado${NC}"
        exit 1
    fi
    
    grep -v "^$channel_name:" "$CHANNELS_FILE" > "$CHANNELS_FILE.tmp" && mv "$CHANNELS_FILE.tmp" "$CHANNELS_FILE"
    echo -e "${GREEN}Canal '$channel_name' removido${NC}"
    log "Canal removido: $channel_name"
}

list_channels() {
    if [ ! -f "$CHANNELS_FILE" ] || [ ! -s "$CHANNELS_FILE" ]; then
        echo -e "${YELLOW}No hay canales configurados${NC}"
        return
    fi
    
    echo -e "${BLUE}Canales monitoreados:${NC}"
    echo "-------------------"
    
    while IFS=':' read -r channel_name url last_video_id; do
        echo -e "${GREEN}Canal:${NC} $channel_name"
        echo -e "${BLUE}URL:${NC} $url"
        echo -e "${YELLOW}Último video:${NC} ${last_video_id:-Ninguno}"
        echo "-------------------"
    done < "$CHANNELS_FILE"
}

get_latest_video() {
    local url="$1"
    yt-dlp --quiet --dump-json --playlist-items 1 "$url" 2>/dev/null | jq -r '{id: .id, title: .title, upload_date: .upload_date}'
}

check_updates() {
    local target_channel="$1"
    
    [ ! -f "$CHANNELS_FILE" ] && { echo -e "${YELLOW}No hay canales${NC}"; return; }
    
    while IFS=':' read -r channel_name url last_video_id; do
        [ -n "$target_channel" ] && [ "$channel_name" != "$target_channel" ] && continue
        
        echo -e "${BLUE}Verificando: $channel_name${NC}"
        
        local video_info=$(get_latest_video "$url")
        if [ $? -eq 0 ] && [ "$video_info" != "null" ]; then
            local current_video_id=$(echo "$video_info" | jq -r '.id')
            local video_title=$(echo "$video_info" | jq -r '.title')
            
            if [ "$current_video_id" != "$last_video_id" ]; then
                echo -e "${GREEN}¡Nuevo video!${NC} $video_title"
            else
                echo -e "${BLUE}Sin videos nuevos${NC}"
            fi
        else
            echo -e "${RED}Error verificando canal${NC}"
        fi
        echo "---"
    done < "$CHANNELS_FILE"
}

download_videos() {
    local target_channel="$1"
    local quality="${QUALITY:-best}"
    local format="${FORMAT:-mp4}"
    local audio_only="${AUDIO_ONLY:-false}"
    
    [ ! -f "$CHANNELS_FILE" ] && { echo -e "${YELLOW}No hay canales${NC}"; return; }
    
    local temp_file=$(mktemp)
    
    while IFS=':' read -r channel_name url last_video_id; do
        [ -n "$target_channel" ] && [ "$channel_name" != "$target_channel" ] && {
            echo "$channel_name:$url:$last_video_id" >> "$temp_file"
            continue
        }
        
        echo -e "${BLUE}Verificando: $channel_name${NC}"
        
        local video_info=$(get_latest_video "$url")
        if [ $? -eq 0 ] && [ "$video_info" != "null" ]; then
            local current_video_id=$(echo "$video_info" | jq -r '.id')
            local video_title=$(echo "$video_info" | jq -r '.title')
            
            if [ "$current_video_id" != "$last_video_id" ]; then
                echo -e "${GREEN}Descargando: $video_title${NC}"
                
                local download_dir="$DOWNLOADS_DIR/$channel_name"
                mkdir -p "$download_dir"
                
                local cmd="yt-dlp -P \"$download_dir\" -o \"%(title)s.%(ext)s\""
                
                if [ "$audio_only" = "true" ]; then
                    cmd="$cmd -x --audio-format mp3"
                else
                    case "$quality" in
                        "720p") cmd="$cmd -f \"bestvideo[height<=720]+bestaudio/best[height<=720]\"" ;;
                        "1080p") cmd="$cmd -f \"bestvideo[height<=1080]+bestaudio/best[height<=1080]\"" ;;
                        "worst") cmd="$cmd -f worst" ;;
                        *) cmd="$cmd -f \"bv*[ext=$format]+ba[ext=m4a]/b[ext=$format]\"" ;;
                    esac
                fi
                
                cmd="$cmd \"https://youtube.com/watch?v=$current_video_id\""
                
                if eval "$cmd"; then
                    echo -e "${GREEN}Descarga exitosa${NC}"
                    log "Descargado: $channel_name - $video_title ($current_video_id)"
                    echo "$channel_name:$url:$current_video_id" >> "$temp_file"
                else
                    echo -e "${RED}Error en descarga${NC}"
                    echo "$channel_name:$url:$last_video_id" >> "$temp_file"
                fi
            else
                echo -e "${BLUE}Sin videos nuevos${NC}"
                echo "$channel_name:$url:$last_video_id" >> "$temp_file"
            fi
        else
            echo -e "${RED}Error verificando canal${NC}"
            echo "$channel_name:$url:$last_video_id" >> "$temp_file"
        fi
        echo "---"
    done < "$CHANNELS_FILE"
    
    mv "$temp_file" "$CHANNELS_FILE"
}

show_history() {
    local target_channel="$1"
    
    [ ! -f "$LOG_FILE" ] && { echo -e "${YELLOW}Sin historial${NC}"; return; }
    
    echo -e "${BLUE}Historial de descargas:${NC}"
    if [ -n "$target_channel" ]; then
        grep "Descargado: $target_channel" "$LOG_FILE" | tail -20
    else
        grep "Descargado:" "$LOG_FILE" | tail -20
    fi
}

show_status() {
    echo -e "${BLUE}Estado del sistema:${NC}"
    echo "==================="
    
    local channel_count=0
    [ -f "$CHANNELS_FILE" ] && channel_count=$(wc -l < "$CHANNELS_FILE")
    echo -e "${GREEN}Canales:${NC} $channel_count"
    
    local download_count=0
    [ -f "$LOG_FILE" ] && download_count=$(grep -c "Descargado:" "$LOG_FILE")
    echo -e "${GREEN}Descargas:${NC} $download_count"
    
    for dir in "$DOWNLOADS_DIR"/*/; do
        [ -d "$dir" ] && {
            local size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo -e "${YELLOW}${dir##*/}:${NC} $size"
        }
    done
}

clean_temp() {
    echo -e "${BLUE}Limpiando temporales...${NC}"
    find /tmp -name "yt-dlp*" -delete 2>/dev/null
    
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt 10485760 ]; then
        tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
        log "Log rotado"
    fi
    echo -e "${GREEN}Limpieza completada${NC}"
}

update_ytdlp() {
    echo -e "${BLUE}Actualizando yt-dlp...${NC}"
    if yt-dlp -U; then
        echo -e "${GREEN}yt-dlp actualizado${NC}"
        log "yt-dlp actualizado"
    else
        echo -e "${RED}Error actualizando${NC}"
    fi
}

main() {
    check_dependencies
    
    local command="$1"
    shift
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -q|--quality) QUALITY="$2"; shift 2 ;;
            -f|--format) FORMAT="$2"; shift 2 ;;
            -a|--audio-only) AUDIO_ONLY="true"; shift ;;
            -h|--help) show_help; exit 0 ;;
            *) ARGS+=("$1"); shift ;;
        esac
    done
    
    case "$command" in
        "add") add_channel "${ARGS[0]}" ;;
        "remove") remove_channel "${ARGS[0]}" ;;
        "list") list_channels ;;
        "check") check_updates "${ARGS[0]}" ;;
        "download") download_videos "${ARGS[0]}" ;;
        "status") show_status ;;
        "history") show_history "${ARGS[0]}" ;;
        "clean") clean_temp ;;
        "update") update_ytdlp ;;
        "") show_help ;;
        *) echo -e "${RED}Comando desconocido: $command${NC}"; exit 1 ;;
    esac
}

main "$@"
EOF
fi

# Hacer ejecutable el script
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

echo -e "${BLUE}5. Verificando instalación...${NC}"
if [ -x "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo -e "${GREEN}✓ Script instalado correctamente en: $INSTALL_DIR/$SCRIPT_NAME${NC}"
else
    echo -e "${RED}✗ Error en la instalación del script${NC}"
    exit 1
fi

echo -e "${BLUE}6. Configuración inicial...${NC}"
mkdir -p "$HOME/.idyt"

echo -e "${GREEN}¡Instalación completada exitosamente!${NC}"
echo
echo -e "${YELLOW}Para empezar a usar:${NC}"
echo "1. Agregar un canal: ${BLUE}ytdl-manager add https://youtube.com/@midudev${NC}"
echo "2. Verificar videos: ${BLUE}ytdl-manager check${NC}"
echo "3. Descargar videos: ${BLUE}ytdl-manager download${NC}"
echo "4. Ver ayuda: ${BLUE}ytdl-manager --help${NC}"
echo
echo -e "${BLUE}Script instalado como:${NC} ytdl-manager"
echo -e "${BLUE}Archivos de configuración en:${NC} $HOME/.idyt/"
