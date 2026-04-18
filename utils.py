# utils.py
"""Utility functions for the application"""

import os
import time
from datetime import timedelta
from typing import List, Tuple, Optional


class TimeFormatter:
    """Formats time values"""
    
    @staticmethod
    def seconds_to_string(seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        return f"{int(seconds//60):02d}:{int(seconds%60):02d}"
    
    @staticmethod
    def seconds_to_timedelta(seconds: float) -> timedelta:
        """Convert seconds to timedelta"""
        return timedelta(seconds=seconds)


class FileManager:
    """Manages file operations"""
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"|?*\\'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def generate_output_path(base_path: str, index: int, suffix: str = "") -> str:
        """Generate output file path"""
        base, ext = os.path.splitext(base_path)
        filename = os.path.basename(base)
        dirname = os.path.dirname(base_path)
        
        safe_name = FileManager.get_safe_filename(filename)
        output_name = f"{safe_name}_shorts_{index+1}{suffix}.mp4"
        
        return os.path.join(dirname, output_name)


class ViraityScoreCalculator:
    """Calculates pseudo-random virality scores"""
    
    @staticmethod
    def calculate(index: int, word_count: int, duration: float) -> int:
        """
        Calculate virality score based on metrics
        Returns value between 80-99
        """
        base_score = 80
        
        # Bonus for word count (more engaged content)
        word_bonus = min((word_count / 100) * 10, 10)
        
        # Bonus for duration (optimal length)
        if 20 < duration < 50:
            duration_bonus = 5
        else:
            duration_bonus = 0
        
        # Pseudo-random variation
        seed_score = (index * 7 + int(word_count * 3.14)) % 19
        
        total = base_score + word_bonus + duration_bonus + seed_score
        return min(int(total), 99)


class EmojiMapper:
    """Maps keywords to relevant emojis"""
    
    EMOJI_MAP = {
        "money": "💰",
        "fire": "🔥",
        "rocket": "🚀",
        "love": "❤️",
        "star": "⭐",
        "crown": "👑",
        "win": "🏆",
        "success": "✅",
        "growth": "📈",
        "mind": "🧠",
        "bomb": "💣",
        "magic": "✨",
        "fast": "⚡",
        "code": "💻",
        "book": "📚",
    }
    
    @staticmethod
    def find_emoji(text: str) -> Optional[str]:
        """Find relevant emoji for text"""
        text_lower = text.lower()
        for keyword, emoji in EmojiMapper.EMOJI_MAP.items():
            if keyword in text_lower:
                return emoji
        return None


class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def log(message: str, level: str = "info") -> Tuple[str, str]:
        """
        Format log message with timestamp
        Returns (formatted_message, html_colored_message)
        """
        timestamp = time.strftime("%H:%M:%S")
        
        colors = {
            "error": ("#f38ba8", "❌"),
            "success": ("#a6e3a1", "✅"),
            "warning": ("#f9e2af", "⚠️"),
            "info": ("#89b4fa", "ℹ️"),
        }
        
        color, prefix = colors.get(level, ("#89b4fa", "ℹ️"))
        formatted = f'<span style="color: {color};">[{timestamp}] {prefix} {message}</span>'
        
        return formatted, level