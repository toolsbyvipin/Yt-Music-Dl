#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🎵 YT MUSIC DOWNLOADER - HACKER EDITION 🔥                              ║
║  Download songs, playlists, albums from YouTube Music                    ║
║  ⚡ Hacker-style UI with custom song symbols                            ║
║  🎯 Supports: Single songs, Playlists, Albums, Artists                  ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import re
import shutil
import signal
import subprocess
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# ===== DEPENDENCY CHECK =====
def check_dependencies():
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.prompt import Prompt, Confirm
        from rich import print as rprint
        from rich.text import Text
        from rich.box import ROUNDED, DOUBLE
        from rich.layout import Layout
        from rich.columns import Columns
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        from rich.live import Live
        from rich.align import Align
    except ImportError:
        missing.append("rich")
    
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        os.system(f"pip install {' '.join(missing)}")
        print("Restart the script after installation.")
        sys.exit(0)

check_dependencies()

import yt_dlp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.text import Text
from rich.box import ROUNDED, DOUBLE
from rich.layout import Layout
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.align import Align

console = Console()

# ===== COLOR THEME (FIXED) =====
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BLACK = '\033[40m'

# ===== HACKER ASCII ART & SYMBOLS =====
HACKER_ASCII = f"""
{Colors.RED}{Colors.BOLD}
    ██╗  ██╗██╗  ██╗ ██████╗██████╗ ███████╗██████╗ 
    ╚██╗██╔╝██║  ██║██╔════╝██╔══██╗██╔════╝██╔══██╗
     ╚███╔╝ ███████║██║     ██████╔╝█████╗  ██████╔╝
     ██╔██╗ ██╔══██║██║     ██╔══██╗██╔══╝  ██╔══██╗
    ██╔╝ ██╗██║  ██║╚██████╗██║  ██║███████╗██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
"""

# ===== SONG SYMBOLS =====
SONG_SYMBOLS = [
    "♩", "♪", "♫", "♬", "🎵", "🎶", "🎧", "🎤", 
    "🎼", "🎹", "🥁", "🎸", "🎺", "🎷", "🎻", "🪕"
]

HACKER_SYMBOLS = [
    "💀", "🔥", "⚡", "☠️", "👾", "🤖", "💻", "🖥️",
    "⌨️", "🖱️", "📡", "🔮", "🕯️", "🗡️", "🏴‍☠️", "🎯"
]

STATUS_SYMBOLS = {
    "downloading": "⬇️",
    "processing": "⚙️",
    "complete": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "music": "🎵",
    "hack": "💀",
    "power": "⚡",
    "target": "🎯"
}

# ===== QUALITY PRESETS =====
AUDIO_PRESETS = {
    "1": {
        "name": "🔊 HIGHEST QUALITY (320kbps MP3)",
        "format": "bestaudio/best",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        "extension": "mp3"
    },
    "2": {
        "name": "🎵 HIGH QUALITY (256kbps MP3)",
        "format": "bestaudio/best",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        "extension": "mp3"
    },
    "3": {
        "name": "🎶 MEDIUM QUALITY (192kbps MP3)",
        "format": "bestaudio/best",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        "extension": "mp3"
    },
    "4": {
        "name": "🎧 HIGH QUALITY M4A (AAC)",
        "format": "bestaudio[ext=m4a]/bestaudio",
        "postprocessors": [],
        "extension": "m4a"
    },
    "5": {
        "name": "🎤 FLAC LOSSLESS (Best Quality)",
        "format": "bestaudio[ext=flac]/bestaudio",
        "postprocessors": [],
        "extension": "flac"
    },
    "6": {
        "name": "💀 CUSTOM QUALITY",
        "format": None,
        "postprocessors": [],
        "extension": "mp3"
    }
}

# ===== YT MUSIC DOWNLOADER =====
class YTMusicDownloader:
    def __init__(self):
        # Save to Music folder on D: drive
        self.download_dir = Path("D:/YT_Music")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-folders
        self.songs_dir = self.download_dir / "Songs"
        self.playlists_dir = self.download_dir / "Playlists"
        self.albums_dir = self.download_dir / "Albums"
        
        for dir_path in [self.songs_dir, self.playlists_dir, self.albums_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.download_dir / "music_history.json"
        self.download_history = self.load_history()
        self.cancelled = False
        self.paused = False
        self.downloaded_count = 0
        self.failed_count = 0
        self.current_song = ""
        self.retry_count = 0
        self.max_retries = 3
    
    def load_history(self) -> Dict:
        """Load download history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_history(self):
        """Save download history"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]⚠️ Could not save history: {e}[/red]")
    
    def print_hacker_banner(self):
        """Display hacker-style banner"""
        console.print(Panel(HACKER_ASCII, border_style="red", box=DOUBLE))
        
        # Subtitle with random symbols
        symbols = random.sample(HACKER_SYMBOLS, 5)
        subtitle = f"{' '.join(symbols)}  YT MUSIC DOWNLOADER  {' '.join(symbols)}"
        console.print(Align.center(f"[bold red]{subtitle}[/bold red]"))
        console.print(Align.center("[dim]🎯 Hacker Edition • Download Songs Like a Pro[/dim]"))
        
        # Warning box - FIXED with proper color codes
        warning_text = f"""
{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}⚠️  HACKER MODE ACTIVE ⚠️{Colors.RESET}

{Colors.RED}🔴 DO NOT GO OFFLINE DURING DOWNLOAD!{Colors.RESET}
{Colors.RED}🔴 DO NOT CLOSE LAPTOP LID!{Colors.RESET}
{Colors.RED}🔴 STAY IN THE MATRIX!{Colors.RESET}

{Colors.YELLOW}⚡ Downloading at maximum speed...{Colors.RESET}
{Colors.GREEN}🎵 Music will be saved to D:\\YT_Music\\{Colors.RESET}
"""
        console.print(Panel(warning_text, border_style="red", box=ROUNDED))
        
        # Show download location
        console.print(f"\n[cyan]📁 Songs: {self.songs_dir}[/cyan]")
        console.print(f"[cyan]📀 Playlists: {self.playlists_dir}[/cyan]")
        console.print(f"[cyan]💿 Albums: {self.albums_dir}[/cyan]")
    
    def print_song_symbol(self, count: int) -> str:
        """Get random song symbol"""
        return random.choice(SONG_SYMBOLS)
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows/Unix compatibility"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip('. ')
        if len(filename) > 150:
            filename = filename[:150]
        return filename
    
    def get_song_info(self, url: str) -> Optional[Dict]:
        """Fetch song information without downloading"""
        console.print(f"\n[cyan]🔍 Scanning for music...[/cyan]")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            console.print(f"[red]❌ Error fetching info: {e}[/red]")
            return None
    
    def format_duration(self, seconds: Any) -> str:
        """Format duration in MM:SS"""
        if not seconds:
            return "Unknown"
        try:
            seconds = int(float(seconds))
        except:
            return "Unknown"
        
        if seconds < 0:
            return "Unknown"
        
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def display_song_info(self, info: Dict):
        """Display song information with hacker style"""
        is_playlist = 'entries' in info and info.get('entries')
        
        if is_playlist:
            # Playlist info
            table = Table(title="📀 PLAYLIST INFORMATION", style="magenta")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="white")
            
            title = info.get('title', 'Unknown')
            table.add_row("🎵 Playlist", title[:60] if title else "Unknown")
            table.add_row("👤 Artist", info.get('uploader', 'Unknown'))
            table.add_row("📊 Songs", str(info.get('playlist_count', 0)))
            table.add_row("⏱️ Duration", self.format_duration(info.get('duration', 0)))
            
            console.print(table)
            
            # Show first 10 songs with symbols
            entries = info.get('entries', [])
            if entries:
                song_table = Table(title="🎵 TRACKLIST", style="green")
                song_table.add_column("#", style="bold yellow")
                song_table.add_column("Title", style="white")
                song_table.add_column("Duration", style="cyan")
                
                for i, entry in enumerate(entries[:10], 1):
                    if entry is None:
                        continue
                    symbol = self.print_song_symbol(i)
                    title = entry.get('title', 'Unknown')[:50]
                    duration = self.format_duration(entry.get('duration', 0))
                    song_table.add_row(f"{symbol} {i}", title, duration)
                
                console.print(song_table)
                
                total = len([e for e in entries if e is not None])
                if total > 10:
                    console.print(f"[dim]... and {total - 10} more songs[/dim]")
        else:
            # Single song
            table = Table(title="🎵 SONG INFORMATION", style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="white")
            
            symbol = random.choice(SONG_SYMBOLS)
            title = info.get('title', 'Unknown')
            table.add_row(f"{symbol} Title", title[:60] if title else "Unknown")
            table.add_row("👤 Artist", info.get('uploader', 'Unknown'))
            table.add_row("⏱️ Duration", self.format_duration(info.get('duration', 0)))
            
            if info.get('description'):
                desc = info.get('description', '')[:100]
                if len(info.get('description', '')) > 100:
                    desc += '...'
                table.add_row("📝 Description", desc)
            
            console.print(table)
    
    def get_audio_preset(self) -> Tuple[str, Dict]:
        """Get audio quality preset"""
        console.print("\n[bold yellow]🎯 SELECT AUDIO QUALITY[/bold yellow]")
        console.print("[dim]⚡ Higher quality = larger file size[/dim]\n")
        
        for key, preset in AUDIO_PRESETS.items():
            console.print(f"  {key}. {preset['name']}")
        
        choice = Prompt.ask("\n[green]Enter choice[/green]", choices=list(AUDIO_PRESETS.keys()), default="1")
        
        preset = AUDIO_PRESETS[choice].copy()
        
        if choice == "6":  # Custom
            format_code = Prompt.ask("[cyan]Enter format code[/cyan]\n[dim](e.g., bestaudio, bestaudio[ext=flac])[/dim]")
            preset['format'] = format_code
            preset['extension'] = Prompt.ask("[cyan]Enter file extension[/cyan]", default="mp3")
        
        return choice, preset
    
    def progress_hook(self, d: Dict):
        """Progress hook for yt-dlp"""
        if self.paused:
            return
        
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = d.get('filename', '')
            
            if filename:
                filename = Path(filename).stem[:30]
            
            symbol = random.choice(SONG_SYMBOLS)
            console.print(f"\r   {symbol} {filename} | {percent}% | Speed: {speed} | ETA: {eta}", end='')
            
        elif d['status'] == 'finished':
            filename = Path(d.get('filename', 'Unknown')).stem
            console.print(f"\r   [green]✅ Downloaded: {filename}[/green]")
            self.downloaded_count += 1
            
        elif d['status'] == 'error':
            console.print(f"\r   [red]❌ Error downloading[/red]")
            self.failed_count += 1
    
    def download_song(self, url: str, output_dir: Path, preset: Dict, filename: Optional[str] = None):
        """Download a single song"""
        self.cancelled = False
        self.paused = False
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Get song title
        song_title = "song"
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    song_title = self.sanitize_filename(info.get('title', 'song'))
        except:
            pass
        
        # Prepare output
        if filename:
            song_title = self.sanitize_filename(filename)
        
        extension = preset.get('extension', 'mp3')
        output_file = output_dir / f"{song_title}.{extension}"
        
        # Skip if exists
        if output_file.exists():
            console.print(f"[yellow]⚠️ File already exists: {output_file.name}[/yellow]")
            if Confirm.ask("Overwrite?"):
                output_file.unlink()
            else:
                console.print("[yellow]⏭️ Skipping...[/yellow]")
                return
        
        # Prepare options
        ydl_opts = {
            'outtmpl': str(output_dir / f"{song_title}.%(ext)s"),
            'format': preset.get('format', 'bestaudio/best'),
            'postprocessors': preset.get('postprocessors', []),
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'overwrites': True,
            'restrictfilenames': True,
            'windowsfilenames': True,
            'writethumbnail': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        console.print(f"\n[green]⬇️ Downloading: {output_file.name}[/green]")
        console.print(f"[dim]📁 Location: {output_dir}[/dim]")
        
        start_time = time.time()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⏸️ Download paused[/yellow]")
            self.paused = not self.paused
            if self.paused:
                console.print("[yellow]Press Ctrl+C again to resume[/yellow]")
                try:
                    while self.paused:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.paused = False
                    console.print("[green]▶️ Resumed![/green]")
                    return
            else:
                console.print("[green]▶️ Resumed![/green]")
                return
                
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            self.failed_count += 1
        
        elapsed = time.time() - start_time
        
        if self.downloaded_count > 0:
            console.print(f"\n[bold green]✅ Download complete![/bold green]")
            console.print(f"   File: [cyan]{output_file.name}[/cyan]")
            console.print(f"   Time: [cyan]{self.format_duration(int(elapsed))}[/cyan]")
            
            # Save to history
            self.download_history[datetime.now().isoformat()] = {
                'title': song_title,
                'url': url,
                'quality': preset['name'],
                'location': str(output_file),
                'size': output_file.stat().st_size if output_file.exists() else 0
            }
            self.save_history()
    
    def download_playlist(self, url: str, output_dir: Path, preset: Dict, max_songs: Optional[int] = None):
        """Download an entire playlist"""
        self.cancelled = False
        self.paused = False
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Get playlist info
        playlist_title = "Playlist"
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    playlist_title = self.sanitize_filename(info.get('title', 'Playlist'))
        except:
            pass
        
        # Create playlist folder
        output_dir = output_dir / playlist_title
        output_dir.mkdir(parents=True, exist_ok=True)
        
        extension = preset.get('extension', 'mp3')
        
        ydl_opts = {
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'format': preset.get('format', 'bestaudio/best'),
            'postprocessors': preset.get('postprocessors', []),
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'overwrites': True,
            'restrictfilenames': True,
            'windowsfilenames': True,
            'writethumbnail': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        if max_songs:
            ydl_opts['playlistend'] = max_songs
        
        console.print(f"\n[green]⬇️ Downloading playlist: {playlist_title}[/green]")
        console.print(f"📁 Location: {output_dir}")
        console.print(f"🎵 Quality: {preset['name']}")
        if max_songs:
            console.print(f"📊 Max songs: {max_songs}")
        console.print("")
        
        start_time = time.time()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⏸️ Download paused[/yellow]")
            self.paused = not self.paused
            if self.paused:
                console.print("[yellow]Press Ctrl+C again to resume[/yellow]")
                try:
                    while self.paused:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.paused = False
                    console.print("[green]▶️ Resumed![/green]")
                    return
            else:
                console.print("[green]▶️ Resumed![/green]")
                return
                
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        
        elapsed = time.time() - start_time
        
        console.print("\n" + "=" * 60)
        console.print(f"[bold green]✅ PLAYLIST DOWNLOAD COMPLETE![/bold green]")
        console.print(f"   Songs downloaded: [green]{self.downloaded_count}[/green]")
        if self.failed_count > 0:
            console.print(f"   Failed: [red]{self.failed_count}[/red]")
        console.print(f"   Time: [cyan]{self.format_duration(int(elapsed))}[/cyan]")
        console.print(f"   Location: [cyan]{output_dir}[/cyan]")
        console.print("=" * 60)
        
        # Save to history
        self.download_history[datetime.now().isoformat()] = {
            'title': playlist_title,
            'url': url,
            'quality': preset['name'],
            'downloaded': self.downloaded_count,
            'failed': self.failed_count,
            'location': str(output_dir)
        }
        self.save_history()
    
    def search_song(self):
        """Search and download a song by name"""
        console.print("\n[bold yellow]🔍 SEARCH MUSIC[/bold yellow]")
        query = Prompt.ask("[cyan]Enter song name or artist[/cyan]")
        
        if not query:
            return
        
        # Search on YouTube Music
        search_url = f"ytsearch5:{query}"
        
        console.print(f"\n[cyan]🔍 Searching: {query}[/cyan]")
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(search_url, download=False)
                
                if not results or not results.get('entries'):
                    console.print("[red]❌ No results found![/red]")
                    return
                
                entries = results.get('entries', [])
                
                # Display results
                table = Table(title="🎵 SEARCH RESULTS", style="cyan")
                table.add_column("#", style="bold yellow")
                table.add_column("Title", style="white")
                table.add_column("Artist", style="green")
                table.add_column("Duration", style="cyan")
                
                for i, entry in enumerate(entries[:5], 1):
                    if entry is None:
                        continue
                    symbol = random.choice(SONG_SYMBOLS)
                    title = entry.get('title', 'Unknown')[:50]
                    uploader = entry.get('uploader', 'Unknown')[:30]
                    duration = self.format_duration(entry.get('duration', 0))
                    table.add_row(f"{symbol} {i}", title, uploader, duration)
                
                console.print(table)
                
                choice = Prompt.ask("[cyan]Select song number[/cyan]", default="1")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(entries):
                        selected = entries[idx]
                        video_id = selected.get('id')
                        if video_id:
                            url = f"https://youtube.com/watch?v={video_id}"
                            
                            # Get quality preset
                            preset_choice, preset = self.get_audio_preset()
                            
                            # Download
                            self.download_song(url, self.songs_dir, preset)
                    else:
                        console.print("[red]❌ Invalid selection![/red]")
                except ValueError:
                    console.print("[red]❌ Invalid selection![/red]")
                    
        except Exception as e:
            console.print(f"[red]❌ Search error: {e}[/red]")
    
    def show_history(self):
        """Show download history with hacker style"""
        if not self.download_history:
            console.print("[yellow]No download history found.[/yellow]")
            return
        
        table = Table(title="📜 DOWNLOAD HISTORY", style="magenta")
        table.add_column("Date", style="yellow")
        table.add_column("Title", style="white")
        table.add_column("Quality", style="green")
        table.add_column("Files", style="cyan")
        table.add_column("Location", style="dim")
        
        for timestamp, record in sorted(self.download_history.items(), reverse=True)[:20]:
            try:
                date = timestamp[:19].replace('T', ' ')
                files = record.get('downloaded', 1) or 1
                table.add_row(
                    date,
                    record.get('title', 'Unknown')[:25],
                    record.get('quality', 'Unknown')[:20],
                    str(files),
                    Path(record.get('location', '')).name[:15]
                )
            except:
                continue
        
        console.print(table)
    
    def open_music_folder(self):
        """Open the music folder"""
        try:
            if sys.platform == 'darwin':
                os.system(f'open "{self.download_dir}"')
            elif sys.platform == 'win32':
                os.system(f'start "" "{self.download_dir}"')
            else:
                os.system(f'xdg-open "{self.download_dir}"')
            console.print(f"[green]📁 Opening: {self.download_dir}[/green]")
        except Exception as e:
            console.print(f"[red]Could not open folder: {e}[/red]")
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed"""
        if shutil.which('ffmpeg'):
            return True
        
        console.print("[red]⚠️ FFmpeg not found![/red]")
        console.print("[yellow]FFmpeg is required for audio conversion.[/yellow]")
        
        if Confirm.ask("Continue without FFmpeg? (limited quality)"):
            return False
        
        console.print("""
[cyan]Install FFmpeg:[/cyan]
  Windows: https://www.gyan.dev/ffmpeg/builds/
  macOS: brew install ffmpeg
  Linux: sudo apt install ffmpeg
""")
        input("Press Enter after installing...")
        return shutil.which('ffmpeg') is not None
    
    def clear_screen(self):
        """Clear terminal"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def run(self):
        """Main loop"""
        self.clear_screen()
        self.print_hacker_banner()
        
        # Check FFmpeg
        has_ffmpeg = self.check_ffmpeg()
        
        while True:
            console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
            console.print("[bold yellow]💀 MAIN MENU[/bold yellow]")
            console.print("  [cyan]1.[/cyan] 🎵 Download Single Song")
            console.print("  [cyan]2.[/cyan] 📀 Download Playlist")
            console.print("  [cyan]3.[/cyan] 🔍 Search & Download Song")
            console.print("  [cyan]4.[/cyan] 📂 Download Album")
            console.print("  [cyan]5.[/cyan] 📜 View History")
            console.print("  [cyan]6.[/cyan] 📁 Open Music Folder")
            console.print("  [cyan]7.[/cyan] 🔧 Check FFmpeg")
            console.print("  [cyan]8.[/cyan] ❌ Exit")
            
            choice = Prompt.ask("\n[green]Select option[/green]", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                url = Prompt.ask("[cyan]Enter YouTube Music URL[/cyan]")
                
                if not url:
                    continue
                
                info = self.get_song_info(url)
                if info:
                    self.display_song_info(info)
                    
                    if Confirm.ask("\n[bold red]Download this song?[/bold red]"):
                        preset_choice, preset = self.get_audio_preset()
                        self.download_song(url, self.songs_dir, preset)
            
            elif choice == "2":
                url = Prompt.ask("[cyan]Enter YouTube Music Playlist URL[/cyan]")
                
                if not url:
                    continue
                
                info = self.get_song_info(url)
                if info:
                    self.display_song_info(info)
                    
                    if Confirm.ask("\n[bold red]Download this playlist?[/bold red]"):
                        preset_choice, preset = self.get_audio_preset()
                        
                        max_songs = None
                        total = info.get('playlist_count', 0)
                        if total > 20:
                            if not Confirm.ask(f"Playlist has {total} songs. Download all?"):
                                try:
                                    max_songs = int(Prompt.ask("[cyan]Enter max songs[/cyan]", default="10"))
                                except:
                                    max_songs = 10
                        
                        self.download_playlist(url, self.playlists_dir, preset, max_songs)
            
            elif choice == "3":
                self.search_song()
            
            elif choice == "4":
                url = Prompt.ask("[cyan]Enter YouTube Music Album URL[/cyan]")
                
                if not url:
                    continue
                
                info = self.get_song_info(url)
                if info:
                    self.display_song_info(info)
                    
                    if Confirm.ask("\n[bold red]Download this album?[/bold red]"):
                        preset_choice, preset = self.get_audio_preset()
                        self.download_playlist(url, self.albums_dir, preset)
            
            elif choice == "5":
                self.show_history()
            
            elif choice == "6":
                self.open_music_folder()
            
            elif choice == "7":
                has_ffmpeg = self.check_ffmpeg()
                if has_ffmpeg:
                    console.print("[green]✅ FFmpeg is installed![/green]")
                else:
                    console.print("[red]❌ FFmpeg not found[/red]")
            
            elif choice == "8":
                console.print("\n[bold red]💀 Exiting...[/bold red]")
                console.print("[dim]🎵 Keep the music playing![/dim]")
                break

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    console.print("\n[yellow]⚠️ Interrupted[/yellow]")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        downloader = YTMusicDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()