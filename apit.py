#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
import subprocess
import datetime
import csv
import threading
import time
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path

# === CONFIGURACIÓN AVANZADA ===
CONFIG_PATH = Path.home() / ".github_actions" / "config.json"
EXPORT_DIR = Path.home() / ".github_actions" / "exports"
CACHE_DIR = Path.home() / ".github_actions" / "cache"
LOGS_DIR = Path.home() / ".github_actions" / "logs"
PER_PAGE = 100
MAX_WORKERS = 10
CACHE_DURATION = 300  # 5 minutos

# === COLORES Y ESTILOS AVANZADOS ===
class Colors:
    # Colores principales
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    
    # Colores básicos
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Colores brillantes
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Fondos
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Gradientes RGB (simulados)
    NEON_BLUE = "\033[38;5;39m"
    NEON_GREEN = "\033[38;5;46m"
    NEON_PINK = "\033[38;5;201m"
    NEON_CYAN = "\033[38;5;39m"
    NEON_YELLOW = "\033[38;5;226m"
    NEON_PURPLE = "\033[38;5;165m"
    NEON_ORANGE = "\033[38;5;208m"
    ELECTRIC_BLUE = "\033[38;5;27m"
    LIME_GREEN = "\033[38;5;118m"
    HOT_PINK = "\033[38;5;198m"
    NEON_RED = "\033[38;5;39m"

class Symbols:
    ARROW_RIGHT = "→"
    ARROW_LEFT = "←"
    ARROW_UP = "↑"
    ARROW_DOWN = "↓"
    CHECK = "✓"
    CROSS = "✗"
    STAR = "★"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"
    BULLET = "•"
    CIRCLE = "●"
    SQUARE = "■"
    TRIANGLE = "▲"
    MUSIC = "♪"
    LIGHTNING = "⚡"
    FIRE = "🔥"
    ROCKET = "🚀"
    GEM = "💎"
    CROWN = "👑"
    SKULL = "💀"
    ALIEN = "👽"
    ROBOT = "🤖"
    UNICORN = "🦄"

# === ANIMACIONES AVANZADAS ===
class LoadingAnimations:
    @staticmethod
    def bouncing_ball(duration: float = 2.0, message: str = "Procesando"):
        """Animación de pelota rebotando"""
        chars = [" •  ", "  • ", "   •", "  • "]
        start_time = time.time()
        i = 0
        while time.time() - start_time < duration:
            print(f"\r{Colors.NEON_BLUE}{message} {chars[i % len(chars)]}{Colors.RESET}", end="", flush=True)
            time.sleep(0.2)
            i += 1
        print(f"\r{Colors.GREEN}{message} {Symbols.CHECK}{Colors.RESET}     ")
    
    @staticmethod
    def spinning_loader(duration: float = 2.0, message: str = "Cargando"):
        """Animación giratoria"""
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start_time = time.time()
        i = 0
        while time.time() - start_time < duration:
            print(f"\r{Colors.NEON_PURPLE}{chars[i % len(chars)]} {message}...{Colors.RESET}", end="", flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r{Colors.GREEN}{Symbols.CHECK} {message} completado!{Colors.RESET}     ")
    
    @staticmethod
    def progress_bar(current: int, total: int, message: str = "Progreso", width: int = 40):
        """Barra de progreso avanzada"""
        if total == 0:
            return
        
        percentage = current / total
        filled = int(width * percentage)
        bar = "█" * filled + "░" * (width - filled)
        
        color = Colors.NEON_GREEN if percentage > 0.7 else Colors.NEON_ORANGE if percentage > 0.3 else Colors.NEON_PINK
        
        print(f"\r{color}{message}: [{bar}] {percentage:.1%} ({current}/{total}){Colors.RESET}", end="", flush=True)
        
        if current == total:
            print(f"\r{Colors.GREEN}{message}: [{bar}] {percentage:.1%} ({current}/{total}) {Symbols.CHECK}{Colors.RESET}")

class VisualEffects:
    @staticmethod
    def rainbow_text(text: str) -> str:
        """Texto con efecto arcoíris"""
        colors = [Colors.BRIGHT_RED, Colors.BRIGHT_YELLOW, Colors.BRIGHT_GREEN, 
                 Colors.BRIGHT_CYAN, Colors.BRIGHT_BLUE, Colors.BRIGHT_MAGENTA]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                result += colors[i % len(colors)] + char + Colors.RESET
            else:
                result += char
        return result
    
    @staticmethod
    def glitch_text(text: str) -> str:
        """Efecto glitch en texto"""
        import random
        glitch_chars = ['░', '▒', '▓', '█', '▄', '▀', '■', '□']
        result = ""
        for char in text:
            if char != ' ' and random.random() < 0.1:
                result += Colors.BRIGHT_RED + random.choice(glitch_chars) + Colors.RESET
            else:
                result += char
        return result
    
    @staticmethod
    def neon_border(text: str, width: int = 60) -> str:
        """Borde neón alrededor del texto"""
        lines = text.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        border_width = max(width, max_len + 4)
        
        top_border = f"{Colors.NEON_BLUE}╔{'═' * (border_width - 2)}╗{Colors.RESET}"
        bottom_border = f"{Colors.NEON_BLUE}╚{'═' * (border_width - 2)}╝{Colors.RESET}"
        
        result = [top_border]
        for line in lines:
            padding = border_width - len(line) - 4
            result.append(f"{Colors.NEON_BLUE}║{Colors.RESET} {line}{' ' * padding} {Colors.NEON_BLUE}║{Colors.RESET}")
        result.append(bottom_border)
        
        return '\n'.join(result)

# === MODELO DE DATOS AVANZADO ===
@dataclass
class Repository:
    name: str
    full_name: str
    private: bool
    fork: bool
    html_url: str
    clone_url: str
    description: Optional[str]
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    size: int
    created_at: str
    updated_at: str
    pushed_at: str
    default_branch: str
    topics: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Repository':
        return cls(
            name=data.get('name', ''),
            full_name=data.get('full_name', ''),
            private=data.get('private', False),
            fork=data.get('fork', False),
            html_url=data.get('html_url', ''),
            clone_url=data.get('clone_url', ''),
            description=data.get('description'),
            language=data.get('language'),
            stargazers_count=data.get('stargazers_count', 0),
            forks_count=data.get('forks_count', 0),
            size=data.get('size', 0),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            pushed_at=data.get('pushed_at', ''),
            default_branch=data.get('default_branch', 'main'),
            topics=data.get('topics', [])
        )
    
    def get_type_icon(self) -> str:
        if self.fork:
            return f"{Colors.NEON_ORANGE}{Symbols.DIAMOND}{Colors.RESET}"
        elif self.private:
            return f"{Colors.NEON_PINK}{Symbols.HEART}{Colors.RESET}"
        else:
            return f"{Colors.NEON_GREEN}{Symbols.STAR}{Colors.RESET}"
    
    def get_language_color(self) -> str:
        language_colors = {
            'Python': Colors.NEON_BLUE,
            'JavaScript': Colors.NEON_YELLOW,
            'TypeScript': Colors.NEON_BLUE,
            'Java': Colors.NEON_ORANGE,
            'C++': Colors.NEON_PURPLE,
            'C': Colors.NEON_PURPLE,
            'Go': Colors.NEON_CYAN,
            'Rust': Colors.NEON_ORANGE,
            'Ruby': Colors.NEON_RED,
            'PHP': Colors.NEON_PURPLE,
            'HTML': Colors.NEON_ORANGE,
            'CSS': Colors.NEON_BLUE,
            'Shell': Colors.NEON_GREEN,
        }
        return language_colors.get(self.language or '', Colors.WHITE)

# === GESTOR DE CONFIGURACIÓN AVANZADO ===
class ConfigManager:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> tuple[str, str]:
        if not self.config_path.exists():
            self.print_error("Error: Configuración no encontrada")
            self.print_info("Ejecuta primero el script de configuración para registrar tu usuario y token")
            sys.exit(1)
        
        try:
            with open(self.config_path) as f:
                data = json.load(f)
            return data["username"], data["token"]
        except (json.JSONDecodeError, KeyError) as e:
            self.print_error(f"Error en configuración: {e}")
            sys.exit(1)
    
    def save_config(self, username: str, token: str):
        config = {"username": username, "token": token}
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        self.print_success("Configuración guardada exitosamente")
    
    @staticmethod
    def print_error(message: str):
        print(f"{Colors.BRIGHT_RED}{Symbols.CROSS} {message}{Colors.RESET}")
    
    @staticmethod
    def print_success(message: str):
        print(f"{Colors.BRIGHT_GREEN}{Symbols.CHECK} {message}{Colors.RESET}")
    
    @staticmethod
    def print_info(message: str):
        print(f"{Colors.BRIGHT_BLUE}{Symbols.BULLET} {message}{Colors.RESET}")

# === GESTOR DE CACHÉ AVANZADO ===
class CacheManager:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_file(self, username: str, repo_type: str) -> Path:
        return self.cache_dir / f"{username}_{repo_type}_repos.json"
    
    def is_cache_valid(self, cache_file: Path) -> bool:
        if not cache_file.exists():
            return False
        
        cache_age = time.time() - cache_file.stat().st_mtime
        return cache_age < CACHE_DURATION
    
    def save_to_cache(self, username: str, repo_type: str, repos: List[Dict]):
        cache_file = self.get_cache_file(username, repo_type)
        cache_data = {
            'timestamp': time.time(),
            'repos': repos
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_cache(self, username: str, repo_type: str) -> Optional[List[Dict]]:
        cache_file = self.get_cache_file(username, repo_type)
        if not self.is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file) as f:
                data = json.load(f)
            return data['repos']
        except (json.JSONDecodeError, KeyError):
            return None

# === CLIENTE API GITHUB MEJORADO ===
class GitHubAPIClient:
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.cache_manager = CacheManager()
    
    def fetch_repos(self, repo_type: str = "all", use_cache: bool = True) -> List[Repository]:
        # Intentar cargar desde caché primero
        if use_cache:
            cached_repos = self.cache_manager.load_from_cache(self.username, repo_type)
            if cached_repos:
                print(f"{Colors.NEON_CYAN}{Symbols.LIGHTNING} Usando datos del caché{Colors.RESET}")
                return [Repository.from_dict(repo) for repo in cached_repos]
        
        repos_data = []
        page = 1
        
        print(f"{Colors.NEON_BLUE}Obteniendo repositorios...{Colors.RESET}")
        
        while True:
            LoadingAnimations.spinning_loader(0.5, f"Página {page}")
            
            url = f"https://api.github.com/user/repos"
            params = {
                "type": repo_type,
                "per_page": PER_PAGE,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                page_data = response.json()
                if not page_data:
                    break
                
                repos_data.extend(page_data)
                page += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"{Colors.BRIGHT_RED}Error en API: {e}{Colors.RESET}")
                sys.exit(1)
        
        # Guardar en caché
        self.cache_manager.save_to_cache(self.username, repo_type, repos_data)
        
        repositories = [Repository.from_dict(repo) for repo in repos_data]
        print(f"{Colors.BRIGHT_GREEN}Se encontraron {len(repositories)} repositorios{Colors.RESET}")
        
        return repositories
    
    def delete_repository(self, full_name: str) -> bool:
        url = f"https://api.github.com/repos/{full_name}"
        try:
            response = self.session.delete(url, timeout=10)
            return response.status_code == 204
        except requests.exceptions.RequestException:
            return False
    
    def get_rate_limit(self) -> Dict:
        try:
            response = self.session.get("https://api.github.com/rate_limit", timeout=5)
            return response.json()
        except:
            return {}

# === INTERFAZ VISUAL AVANZADA ===
class VisualInterface:
    def __init__(self):
        self.terminal_width = shutil.get_terminal_size().columns
    
    def print_header(self):
        header = f"""
{Colors.NEON_BLUE}╔{'═' * (self.terminal_width - 2)}╗{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{VisualEffects.rainbow_text('🚀 GITHUB REPOSITORY MANAGER PRO 🚀').center(self.terminal_width - 2)}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}║{Colors.RESET}{Colors.NEON_PURPLE}✨ Terminal Edition con Superpoderes ✨{Colors.RESET.center(self.terminal_width - 2)}{Colors.NEON_BLUE}║{Colors.RESET}
{Colors.NEON_BLUE}╚{'═' * (self.terminal_width - 2)}╝{Colors.RESET}
        """
        print(header)
    
    def print_repository_list(self, repositories: List[Repository], show_details: bool = False):
        print(f"\n{Colors.NEON_GREEN}📁 REPOSITORIOS ENCONTRADOS:{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * self.terminal_width}{Colors.RESET}")
        
        for i, repo in enumerate(repositories, 1):
            # Icono según tipo
            icon = repo.get_type_icon()
            
            # Color según lenguaje
            lang_color = repo.get_language_color()
            language = f"{lang_color}{repo.language or 'N/A'}{Colors.RESET}"
            
            # Información básica
            stars = f"{Colors.NEON_YELLOW}{Symbols.STAR}{repo.stargazers_count}{Colors.RESET}"
            forks = f"{Colors.NEON_CYAN}{Symbols.DIAMOND}{repo.forks_count}{Colors.RESET}"
            
            # Línea principal
            main_line = f"{Colors.BRIGHT_WHITE}{i:3d}.{Colors.RESET} {icon} {Colors.BOLD}{repo.full_name}{Colors.RESET}"
            
            if show_details:
                print(f"{main_line}")
                print(f"     {Colors.DIM}├─ Lenguaje: {language}")
                print(f"     ├─ Estrellas: {stars} | Forks: {forks}")
                print(f"     ├─ Tamaño: {Colors.NEON_ORANGE}{repo.size} KB{Colors.RESET}")
                if repo.description:
                    desc = repo.description[:60] + "..." if len(repo.description) > 60 else repo.description
                    print(f"     └─ Descripción: {Colors.DIM}{desc}{Colors.RESET}")
                print()
            else:
                info = f"[{language}] {stars} {forks}"
                padding = self.terminal_width - len(main_line) - len(info) - 10
                print(f"{main_line}{' ' * max(1, padding)}{info}")
        
        print(f"{Colors.DIM}{'─' * self.terminal_width}{Colors.RESET}")
    
    def print_menu(self):
        menu = f"""
{Colors.NEON_PURPLE}🎮 OPCIONES DISPONIBLES:{Colors.RESET}

{Colors.NEON_GREEN}🔍 Exploración:{Colors.RESET}
   --all      📋 Todos los repositorios
   --public   🌍 Solo repositorios públicos  
   --private  🔒 Solo repositorios privados
   --forks    🔄 Solo forks

{Colors.NEON_BLUE}⚡ Acciones:{Colors.RESET}
   --clone    📥 Clonar repositorios
   --delete   🗑️  Eliminar repositorios
   --stats    📊 Estadísticas detalladas
   --export   💾 Exportar a CSV/JSON

{Colors.NEON_ORANGE}🔧 Configuración:{Colors.RESET}
   --setup    ⚙️  Configurar credenciales
   --cache    🗄️  Gestionar caché
   --help     ❓ Mostrar ayuda
        """
        print(VisualEffects.neon_border(menu.strip()))

# === EXPORTADOR AVANZADO ===
class DataExporter:
    def __init__(self):
        self.export_dir = EXPORT_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_csv(self, repositories: List[Repository], label: str) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Headers expandidos
            writer.writerow([
                'name', 'full_name', 'private', 'fork', 'language', 
                'stars', 'forks', 'size_kb', 'created_at', 'updated_at',
                'description', 'html_url', 'clone_url', 'topics'
            ])
            
            for repo in repositories:
                writer.writerow([
                    repo.name, repo.full_name, repo.private, repo.fork,
                    repo.language or '', repo.stargazers_count, repo.forks_count,
                    repo.size, repo.created_at, repo.updated_at,
                    repo.description or '', repo.html_url, repo.clone_url,
                    ';'.join(repo.topics)
                ])
        
        return filepath
    
    def export_json(self, repositories: List[Repository], label: str) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}.json"
        filepath = self.export_dir / filename
        
        data = {
            'export_date': datetime.datetime.now().isoformat(),
            'total_repositories': len(repositories),
            'repositories': [
                {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private,
                    'fork': repo.fork,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'size_kb': repo.size,
                    'created_at': repo.created_at,
                    'updated_at': repo.updated_at,
                    'pushed_at': repo.pushed_at,
                    'description': repo.description,
                    'html_url': repo.html_url,
                    'clone_url': repo.clone_url,
                    'default_branch': repo.default_branch,
                    'topics': repo.topics
                }
                for repo in repositories
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath

# === ANALIZADOR DE ESTADÍSTICAS ===
class StatsAnalyzer:
    @staticmethod
    def analyze_repositories(repositories: List[Repository]) -> Dict:
        if not repositories:
            return {}
        
        # Análisis básico
        total = len(repositories)
        private_count = sum(1 for r in repositories if r.private)
        public_count = total - private_count
        fork_count = sum(1 for r in repositories if r.fork)
        original_count = total - fork_count
        
        # Análisis de lenguajes
        languages = {}
        for repo in repositories:
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1
        
        # Estadísticas de estrellas y forks
        total_stars = sum(r.stargazers_count for r in repositories)
        total_forks = sum(r.forks_count for r in repositories)
        total_size = sum(r.size for r in repositories)
        
        # Repositorio más popular
        most_starred = max(repositories, key=lambda r: r.stargazers_count, default=None)
        most_forked = max(repositories, key=lambda r: r.forks_count, default=None)
        largest = max(repositories, key=lambda r: r.size, default=None)
        
        return {
            'total': total,
            'private': private_count,
            'public': public_count,
            'forks': fork_count,
            'original': original_count,
            'languages': languages,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_size_kb': total_size,
            'total_size_mb': round(total_size / 1024, 2),
            'most_starred': most_starred,
            'most_forked': most_forked,
            'largest': largest,
            'avg_stars': round(total_stars / total, 2) if total > 0 else 0,
            'avg_forks': round(total_forks / total, 2) if total > 0 else 0,
        }
    
    @staticmethod
    def print_stats(stats: Dict, ui: VisualInterface):
        if not stats:
            print(f"{Colors.BRIGHT_RED}No hay datos para mostrar estadísticas{Colors.RESET}")
            return
        
        # Crear visualización de estadísticas
        stats_text = f"""
📊 ESTADÍSTICAS GENERALES

🔢 Resumen:
   Total de repositorios: {Colors.NEON_BLUE}{stats['total']}{Colors.RESET}
   Públicos: {Colors.NEON_GREEN}{stats['public']}{Colors.RESET} | Privados: {Colors.NEON_PINK}{stats['private']}{Colors.RESET}
   Originales: {Colors.NEON_YELLOW}{stats['original']}{Colors.RESET} | Forks: {Colors.NEON_ORANGE}{stats['forks']}{Colors.RESET}

⭐ Popularidad:
   Total de estrellas: {Colors.NEON_YELLOW}{stats['total_stars']}{Colors.RESET}
   Total de forks: {Colors.NEON_CYAN}{stats['total_forks']}{Colors.RESET}
   Promedio de estrellas: {Colors.NEON_YELLOW}{stats['avg_stars']}{Colors.RESET}
   Promedio de forks: {Colors.NEON_CYAN}{stats['avg_forks']}{Colors.RESET}

💾 Almacenamiento:
   Tamaño total: {Colors.NEON_PURPLE}{stats['total_size_mb']} MB{Colors.RESET} ({stats['total_size_kb']} KB)

🏆 Destacados:"""
        
        if stats['most_starred']:
            repo = stats['most_starred']
            stats_text += f"\n   Más estrellado: {Colors.BOLD}{repo.full_name}{Colors.RESET} ({Colors.NEON_YELLOW}{repo.stargazers_count} ⭐{Colors.RESET})"
        
        if stats['most_forked']:
            repo = stats['most_forked']
            stats_text += f"\n   Más forkeado: {Colors.BOLD}{repo.full_name}{Colors.RESET} ({Colors.NEON_CYAN}{repo.forks_count} 🔄{Colors.RESET})"
        
        if stats['largest']:
            repo = stats['largest']
            stats_text += f"\n   Más grande: {Colors.BOLD}{repo.full_name}{Colors.RESET} ({Colors.NEON_PURPLE}{repo.size} KB{Colors.RESET})"
        
        # Top 5 lenguajes
        if stats['languages']:
            stats_text += f"\n\n💻 Top 5 Lenguajes:"
            sorted_langs = sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True)[:5]
            sorted_langs = sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True)[:5]
            colors = [Colors.NEON_BLUE, Colors.NEON_GREEN, Colors.NEON_YELLOW, Colors.NEON_ORANGE, Colors.NEON_PINK]
            for i, (lang, count) in enumerate(sorted_langs, 1):
                color = colors[i-1]
                stats_text += f"\n   {i}. {color}{lang}{Colors.RESET}: {count} repos"
        
        print(VisualEffects.neon_border(stats_text.strip()))

# === GESTOR DE OPERACIONES AVANZADO ===
class RepositoryManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.ui = VisualInterface()
        self.exporter = DataExporter()
        self.username = None
        self.token = None
        self.github_client = None
    
    def initialize(self):
        """Inicializar el gestor con credenciales"""
        try:
            self.username, self.token = self.config_manager.load_config()
            self.github_client = GitHubAPIClient(self.username, self.token)
            return True
        except SystemExit:
            return False
    
    def setup_credentials(self):
        """Configurar credenciales de GitHub"""
        self.ui.print_header()
        print(f"{Colors.NEON_PURPLE}🔧 CONFIGURACIÓN DE CREDENCIALES{Colors.RESET}\n")
        
        print(f"{Colors.NEON_BLUE}Para usar este gestor necesitas:{Colors.RESET}")
        print(f"  1. Tu nombre de usuario de GitHub")
        print(f"  2. Un Personal Access Token con permisos de repo")
        print(f"  3. Crear token en: {Colors.NEON_CYAN}https://github.com/settings/tokens{Colors.RESET}\n")
        
        username = input(f"{Colors.NEON_GREEN}Usuario de GitHub: {Colors.RESET}").strip()
        if not username:
            self.config_manager.print_error("Usuario requerido")
            return False
        
        token = input(f"{Colors.NEON_GREEN}Personal Access Token: {Colors.RESET}").strip()
        if not token:
            self.config_manager.print_error("Token requerido")
            return False
        
        # Verificar credenciales
        LoadingAnimations.spinning_loader(1.5, "Verificando credenciales")
        
        test_client = GitHubAPIClient(username, token)
        try:
            rate_limit = test_client.get_rate_limit()
            if rate_limit:
                self.config_manager.save_config(username, token)
                self.config_manager.print_success("Credenciales configuradas correctamente")
                return True
            else:
                self.config_manager.print_error("Error: Credenciales inválidas")
                return False
        except:
            self.config_manager.print_error("Error: No se pudo verificar las credenciales")
            return False
    
    def clone_repositories(self, repositories: List[Repository]):
        """Clonar repositorios con progreso visual"""
        if not repositories:
            self.config_manager.print_error("No hay repositorios para clonar")
            return
        
        print(f"\n{Colors.NEON_BLUE}📥 CLONANDO REPOSITORIOS{Colors.RESET}\n")
        
        # Crear directorio de destino
        clone_dir = Path.cwd() / "github_repos"
        clone_dir.mkdir(exist_ok=True)
        
        successful_clones = 0
        failed_clones = 0
        
        for i, repo in enumerate(repositories, 1):
            LoadingAnimations.progress_bar(i-1, len(repositories), "Clonando")
            
            repo_path = clone_dir / repo.name
            if repo_path.exists():
                print(f"\n{Colors.NEON_YELLOW}⚠️  {repo.full_name} ya existe, saltando...{Colors.RESET}")
                continue
            
            try:
                # Cambiar al directorio de destino
                os.chdir(clone_dir)
                
                # Ejecutar git clone
                result = subprocess.run(
                    ["git", "clone", repo.clone_url, repo.name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    successful_clones += 1
                    print(f"\n{Colors.BRIGHT_GREEN}✓ {repo.full_name} clonado exitosamente{Colors.RESET}")
                else:
                    failed_clones += 1
                    print(f"\n{Colors.BRIGHT_RED}✗ Error clonando {repo.full_name}: {result.stderr.strip()}{Colors.RESET}")
                
            except subprocess.TimeoutExpired:
                failed_clones += 1
                print(f"\n{Colors.BRIGHT_RED}✗ Timeout clonando {repo.full_name}{Colors.RESET}")
            except Exception as e:
                failed_clones += 1
                print(f"\n{Colors.BRIGHT_RED}✗ Error clonando {repo.full_name}: {e}{Colors.RESET}")
            
            # Pequeña pausa entre clones
            time.sleep(0.5)
        
        LoadingAnimations.progress_bar(len(repositories), len(repositories), "Clonando")
        
        # Resumen final
        print(f"\n{Colors.NEON_GREEN}📊 RESUMEN DE CLONADO:{Colors.RESET}")
        print(f"  ✅ Exitosos: {Colors.BRIGHT_GREEN}{successful_clones}{Colors.RESET}")
        print(f"  ❌ Fallidos: {Colors.BRIGHT_RED}{failed_clones}{Colors.RESET}")
        print(f"  📁 Directorio: {Colors.NEON_CYAN}{clone_dir}{Colors.RESET}")
    
    def delete_repositories(self, repositories: List[Repository]):
        """Eliminar repositorios con confirmación y progreso"""
        if not repositories:
            self.config_manager.print_error("No hay repositorios para eliminar")
            return
        
        print(f"\n{Colors.BRIGHT_RED}🗑️  ELIMINACIÓN DE REPOSITORIOS{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}⚠️  Esta acción es IRREVERSIBLE{Colors.RESET}\n")
        
        # Mostrar lista de repositorios a eliminar
        for i, repo in enumerate(repositories, 1):
            icon = repo.get_type_icon()
            print(f"  {i}. {icon} {repo.full_name}")
        
        print(f"\n{Colors.BRIGHT_RED}¿Estás seguro de que quieres eliminar estos {len(repositories)} repositorios?{Colors.RESET}")
        confirmation = input(f"{Colors.NEON_YELLOW}Escribe 'ELIMINAR' para confirmar: {Colors.RESET}").strip()
        
        if confirmation != 'ELIMINAR':
            self.config_manager.print_info("Operación cancelada")
            return
        
        # Segunda confirmación
        print(f"\n{Colors.BRIGHT_RED}ÚLTIMA CONFIRMACIÓN{Colors.RESET}")
        final_confirmation = input(f"{Colors.NEON_YELLOW}Escribe 'SI' para proceder: {Colors.RESET}").strip().upper()
        
        if final_confirmation != 'SI':
            self.config_manager.print_info("Operación cancelada")
            return
        
        # Proceder con eliminación
        print(f"\n{Colors.NEON_RED}🔥 ELIMINANDO REPOSITORIOS...{Colors.RESET}\n")
        
        successful_deletions = 0
        failed_deletions = 0
        
        for i, repo in enumerate(repositories, 1):
            LoadingAnimations.progress_bar(i-1, len(repositories), "Eliminando")
            
            try:
                if self.github_client.delete_repository(repo.full_name):
                    successful_deletions += 1
                    print(f"\n{Colors.BRIGHT_GREEN}✓ {repo.full_name} eliminado{Colors.RESET}")
                else:
                    failed_deletions += 1
                    print(f"\n{Colors.BRIGHT_RED}✗ Error eliminando {repo.full_name}{Colors.RESET}")
                
            except Exception as e:
                failed_deletions += 1
                print(f"\n{Colors.BRIGHT_RED}✗ Error eliminando {repo.full_name}: {e}{Colors.RESET}")
            
            # Pausa para evitar rate limiting
            time.sleep(1)
        
        LoadingAnimations.progress_bar(len(repositories), len(repositories), "Eliminando")
        
        # Resumen final
        print(f"\n{Colors.NEON_RED}📊 RESUMEN DE ELIMINACIÓN:{Colors.RESET}")
        print(f"  ✅ Exitosos: {Colors.BRIGHT_GREEN}{successful_deletions}{Colors.RESET}")
        print(f"  ❌ Fallidos: {Colors.BRIGHT_RED}{failed_deletions}{Colors.RESET}")
    
    def prompt_repository_selection(self, repositories: List[Repository], action: str = "procesar") -> List[Repository]:
        """Prompt interactivo para seleccionar repositorios"""
        if not repositories:
            return []
        
        print(f"\n{Colors.NEON_PURPLE}🎯 SELECCIÓN DE REPOSITORIOS{Colors.RESET}")
        print(f"Selecciona qué repositorios deseas {action}:\n")
        
        # Opciones de selección
        print(f"{Colors.NEON_GREEN}Opciones de selección:{Colors.RESET}")
        print(f"  • Números específicos: 1,3,5,7")
        print(f"  • Rangos: 1-5,10-15")
        print(f"  • 'all' para todos")
        print(f"  • 'none' para cancelar")
        print(f"  • 'public' para solo públicos")
        print(f"  • 'private' para solo privados")
        print(f"  • 'forks' para solo forks\n")
        
        self.ui.print_repository_list(repositories)
        
        selection = input(f"\n{Colors.NEON_CYAN}Tu selección: {Colors.RESET}").strip().lower()
        
        if selection == 'none':
            return []
        elif selection == 'all':
            return repositories
        elif selection == 'public':
            return [r for r in repositories if not r.private and not r.fork]
        elif selection == 'private':
            return [r for r in repositories if r.private]
        elif selection == 'forks':
            return [r for r in repositories if r.fork]
        else:
            # Parsear selección numérica
            selected = []
            parts = selection.split(',')
            
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Rango
                    try:
                        start, end = map(int, part.split('-'))
                        for i in range(start-1, min(end, len(repositories))):
                            if 0 <= i < len(repositories):
                                selected.append(repositories[i])
                    except ValueError:
                        continue
                else:
                    # Número individual
                    try:
                        index = int(part) - 1
                        if 0 <= index < len(repositories):
                            selected.append(repositories[index])
                    except ValueError:
                        continue
            
            return selected
    
    def manage_cache(self):
        """Gestionar caché de datos"""
        cache_manager = CacheManager()
        
        print(f"\n{Colors.NEON_PURPLE}🗄️  GESTIÓN DE CACHÉ{Colors.RESET}\n")
        
        cache_files = list(cache_manager.cache_dir.glob("*.json"))
        
        if not cache_files:
            print(f"{Colors.NEON_YELLOW}No hay archivos de caché{Colors.RESET}")
            return
        
        print(f"{Colors.NEON_GREEN}Archivos de caché encontrados:{Colors.RESET}")
        total_size = 0
        
        for i, cache_file in enumerate(cache_files, 1):
            size = cache_file.stat().st_size
            total_size += size
            age = time.time() - cache_file.stat().st_mtime
            age_str = f"{int(age/60)} min" if age < 3600 else f"{int(age/3600)} h"
            
            print(f"  {i}. {cache_file.name} ({size} bytes, {age_str})")
        
        print(f"\n{Colors.NEON_BLUE}Tamaño total del caché: {total_size} bytes{Colors.RESET}")
        
        action = input(f"\n{Colors.NEON_YELLOW}¿Limpiar caché? (s/N): {Colors.RESET}").strip().lower()
        
        if action in ['s', 'si', 'y', 'yes']:
            for cache_file in cache_files:
                cache_file.unlink()
            
            print(f"{Colors.BRIGHT_GREEN}✓ Caché limpiado exitosamente{Colors.RESET}")
        else:
            print(f"{Colors.NEON_BLUE}Caché conservado{Colors.RESET}")

# === INTERFAZ PRINCIPAL ===
class GitHubManagerPro:
    def __init__(self):
        self.manager = RepositoryManager()
        self.ui = VisualInterface()
        self.stats_analyzer = StatsAnalyzer()
    
    def run(self, args):
        """Ejecutar el gestor según argumentos"""
        
        # Mostrar header siempre
        self.ui.print_header()
        
        # Configuración inicial
        if args.setup:
            return self.manager.setup_credentials()
        
        # Gestión de caché
        if args.cache:
            if not self.manager.initialize():
                return False
            self.manager.manage_cache()
            return True
        
        # Inicializar cliente
        if not self.manager.initialize():
            print(f"\n{Colors.NEON_YELLOW}⚠️  Configuración requerida{Colors.RESET}")
            setup_ok = self.manager.setup_credentials()
            if not setup_ok:
                return False
            self.manager.initialize()
        
        # Determinar tipo de repositorios
        repo_type = "all"
        if args.public:
            repo_type = "public"
        elif args.private:
            repo_type = "private"
        elif args.forks:
            repo_type = "forks"
        
        # Obtener repositorios
        LoadingAnimations.bouncing_ball(1.0, "Conectando con GitHub")
        
        try:
            if args.forks:
                # Para forks, obtenemos todos y filtramos
                all_repos = self.manager.github_client.fetch_repos("all", not args.no_cache)
                repositories = [r for r in all_repos if r.fork]
            else:
                repositories = self.manager.github_client.fetch_repos(repo_type, not args.no_cache)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error obteniendo repositorios: {e}{Colors.RESET}")
            return False
        
        if not repositories:
            print(f"{Colors.NEON_YELLOW}No se encontraron repositorios{Colors.RESET}")
            return True
        
        # Mostrar estadísticas si se solicita
        if args.stats:
            stats = self.stats_analyzer.analyze_repositories(repositories)
            self.stats_analyzer.print_stats(stats, self.ui)
            return True
        
        # Exportar datos si se solicita
        if args.export:
            csv_path = self.manager.exporter.export_csv(repositories, repo_type)
            json_path = self.manager.exporter.export_json(repositories, repo_type)
            
            print(f"\n{Colors.BRIGHT_GREEN}📁 EXPORTACIÓN COMPLETADA:{Colors.RESET}")
            print(f"  CSV: {Colors.NEON_CYAN}{csv_path}{Colors.RESET}")
            print(f"  JSON: {Colors.NEON_PURPLE}{json_path}{Colors.RESET}")
            return True
        
        # Mostrar repositorios
        self.ui.print_repository_list(repositories, args.details)
        
        # Acciones específicas
        if args.clone:
            selected = self.manager.prompt_repository_selection(repositories, "clonar")
            if selected:
                self.manager.clone_repositories(selected)
        
        elif args.delete:
            selected = self.manager.prompt_repository_selection(repositories, "eliminar")
            if selected:
                self.manager.delete_repositories(selected)
        
        return True

# === PUNTO DE ENTRADA PRINCIPAL ===
def main():
    parser = argparse.ArgumentParser(
        description=f"{VisualEffects.rainbow_text('🚀 GitHub Repository Manager Pro')}\nGestor avanzado de repositorios con superpoderes visuales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.NEON_BLUE}Ejemplos de uso:{Colors.RESET}
  {Colors.NEON_GREEN}%(prog)s --setup{Colors.RESET}                  Configurar credenciales
  {Colors.NEON_GREEN}%(prog)s --all --stats{Colors.RESET}            Estadísticas de todos los repos
  {Colors.NEON_GREEN}%(prog)s --public --clone{Colors.RESET}         Clonar repos públicos seleccionados
  {Colors.NEON_GREEN}%(prog)s --private --export{Colors.RESET}       Exportar repos privados
  {Colors.NEON_GREEN}%(prog)s --forks --delete{Colors.RESET}         Eliminar forks seleccionados
  {Colors.NEON_GREEN}%(prog)s --all --details{Colors.RESET}          Ver detalles de todos los repos
        """
    )
    
    # Grupos de argumentos
    exploration = parser.add_argument_group('🔍 Exploración')
    exploration.add_argument('--all', action='store_true', help='Todos los repositorios')
    exploration.add_argument('--public', action='store_true', help='Solo repositorios públicos')
    exploration.add_argument('--private', action='store_true', help='Solo repositorios privados')
    exploration.add_argument('--forks', action='store_true', help='Solo forks')
    
    actions = parser.add_argument_group('⚡ Acciones')
    actions.add_argument('--clone', action='store_true', help='Clonar repositorios seleccionados')
    actions.add_argument('--delete', action='store_true', help='Eliminar repositorios seleccionados')
    actions.add_argument('--stats', action='store_true', help='Mostrar estadísticas detalladas')
    actions.add_argument('--export', action='store_true', help='Exportar a CSV y JSON')
    
    display = parser.add_argument_group('🎨 Visualización')
    display.add_argument('--details', action='store_true', help='Mostrar detalles completos')
    display.add_argument('--no-cache', action='store_true', help='Desactivar caché')
    
    config = parser.add_argument_group('🔧 Configuración')
    config.add_argument('--setup', action='store_true', help='Configurar credenciales')
    config.add_argument('--cache', action='store_true', help='Gestionar caché')
    
    args = parser.parse_args()
    
    # Si no se proporcionan argumentos, mostrar menú
    if not any(vars(args).values()):
        ui = VisualInterface()
        ui.print_header()
        ui.print_menu()
        return
    
    # Ejecutar gestor
    try:
        manager_pro = GitHubManagerPro()
        success = manager_pro.run(args)
        
        if success:
            print(f"\n{Colors.BRIGHT_GREEN}🎉 Operación completada exitosamente!{Colors.RESET}")
        else:
            print(f"\n{Colors.BRIGHT_RED}❌ Operación fallida{Colors.RESET}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}⚠️  Operación cancelada por el usuario{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}💥 Error inesperado: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
