import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, TextIO
import json
from enum import Enum
import threading
from functools import wraps
import traceback
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class LogLevel(Enum):
    DEBUG = ("💭", Fore.CYAN)
    INFO = ("💌", Fore.WHITE)
    WARNING = ("⚠️", Fore.YELLOW)
    ERROR = ("❌", Fore.RED)
    CRITICAL = ("🚨", Fore.RED + Style.BRIGHT)
    SUCCESS = ("✨", Fore.GREEN)

class Seraphina:
    """
    Seraphina: A magical and colorful logging system with cute emojis and terminal colors.
    """
    def __init__(
        self,
        name: str = "Seraphina",
        log_file: Optional[Union[str, Path]] = None,
        console_output: bool = True,
        log_level: LogLevel = LogLevel.INFO,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 3,
        use_colors: bool = True
    ):
        self.name = name
        self.console_output = console_output
        self.log_level = log_level
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.use_colors = use_colors
        self._lock = threading.Lock()
        
        # Setup file logging
        self.log_file = Path(log_file) if log_file else None
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
        # Initialize handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers"""
        self.handlers = []
        
        if self.console_output:
            self.handlers.append(sys.stdout)
            
        if self.log_file:
            self._rotate_logs_if_needed()
            self.handlers.append(open(self.log_file, 'a', encoding='utf-8'))

    def _rotate_logs_if_needed(self):
        """Rotate log files if size exceeds max_file_size"""
        if not self.log_file or not self.log_file.exists():
            return
            
        if self.log_file.stat().st_size > self.max_file_size:
            for i in range(self.backup_count - 1, 0, -1):
                old_file = self.log_file.parent / f"{self.log_file.stem}.{i}{self.log_file.suffix}"
                new_file = self.log_file.parent / f"{self.log_file.stem}.{i+1}{self.log_file.suffix}"
                if old_file.exists():
                    old_file.rename(new_file)
                    
            self.log_file.rename(self.log_file.parent / f"{self.log_file.stem}.1{self.log_file.suffix}")

    def _format_message(self, level: LogLevel, message: str, handler: TextIO) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        emoji, color = level.value
        base_msg = f"[{timestamp}] {emoji} [{self.name}] {message}"

        if self.use_colors and handler == sys.stdout:
            timestamp_color = Fore.BLUE + Style.DIM
            name_color = Fore.MAGENTA + Style.BRIGHT
            return f"{timestamp_color}[{timestamp}]{Style.RESET_ALL} {emoji} {name_color}[{self.name}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}"

        return base_msg  # No colors for file logs


    def _write_log(self, level: LogLevel, message: str):
        """Write the log message to all handlers"""
        with self._lock:
            for handler in self.handlers:
                formatted_message = self._format_message(level, message, handler)
                if hasattr(handler, "write"):
                    print(formatted_message, file=handler, flush=True)
                    
    def _log(self, level: LogLevel, message: str):
        """Internal logging method"""
        self._write_log(level, message)

    # Public logging methods with enhanced colors and emojis
    def debug(self, message: str):
        self._log(LogLevel.DEBUG, f"{message} 🐱")

    def info(self, message: str):
        self._log(LogLevel.INFO, f"{message} 🌸")

    def warning(self, message: str):
        self._log(LogLevel.WARNING, f"{message} 🌟")

    def error(self, message: str):
        self._log(LogLevel.ERROR, f"{message} 😿")

    def critical(self, message: str):
        self._log(LogLevel.CRITICAL, f"{message} 💔")

    def success(self, message: str):
        self._log(LogLevel.SUCCESS, f"{message} 🎉")

    # Specialized magical logging methods
    def spell_cast_start(self, spell_name: str):
        self.info(f"Casting spell: {spell_name} 🌟")

    def spell_cast_success(self, spell_name: str):
        self.success(f"Spell '{spell_name}' was cast successfully! ✨")

    def spell_cast_failure(self, spell_name: str):
        self.error(f"Failed to cast spell: {spell_name} 🌩️")

    def potion_brew_start(self, potion_name: str):
        self.info(f"Starting to brew {potion_name} 🧪")

    def potion_brew_complete(self, potion_name: str):
        self.success(f"Successfully brewed {potion_name} 🎊")

    def system_status(self, status: str):
        self.info(f"System Status: {status} 🌈")

    def close(self):
        """Close all file handlers"""
        for handler in self.handlers:
            if isinstance(handler, TextIO) and handler != sys.stdout:
                handler.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Decorator for logging function calls with magical flair
def enchanted_logging(logger: Seraphina):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"✨ Enchanting {func_name} ✨")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"🌟 {func_name} enchantment completed successfully 🌟")
                return result
            except Exception as e:
                logger.error(f"💫 Enchantment failed in {func_name}: {str(e)} 💫")
                logger.debug(f"📜 Spell scroll (traceback): {traceback.format_exc()} 📜")
                raise
        return wrapper
    return decorator

# # Example usage
# if __name__ == "__main__":
#     # Initialize Seraphina with both console and file output
#     logger = Seraphina(
#         name="MagicalRealm",
#         log_file="magical_logs/spellbook.log",
#         console_output=True,
#         use_colors=True
#     )

#     # Example function with enchanted logging decorator
#     @enchanted_logging(logger)
#     def cast_healing_spell(target: str):
#         logger.spell_cast_start("Healing Light")
#         # Simulate spell casting
#         logger.success(f"✨ {target} has been healed! ✨")
#         return f"{target} is now fully healed!"

#     try:
#         # Test the magical logger
#         logger.info("🌟 Awakening the magical realm... 🌟")
#         logger.spell_cast_start("Morning Brightness")
#         logger.success("🌅 The sun has risen on our magical world! 🌅")
        
#         # Cast a healing spell
#         result = cast_healing_spell("Mystical Forest")
#         logger.success(f"Magical operations completed! ✨")
        
#         # Test potion brewing
#         logger.potion_brew_start("Elixir of Wisdom")
#         logger.potion_brew_complete("Elixir of Wisdom")
        
#         # Test error logging
#         logger.warning("⚠️ Detected unusual magical fluctuations!")
#         raise ValueError("🌋 Magical overflow detected!")
#     except Exception as e:
#         logger.critical(f"Magical emergency: {str(e)}")
#     finally:
#         logger.info("✨ Sealing the magical realm... ✨")
#         logger.close()