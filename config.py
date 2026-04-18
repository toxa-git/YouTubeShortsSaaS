# config.py
"""Configuration and constants for the application"""

# === COLORS (Catppuccin Mocha Theme) ===
COLORS = {
    "bg_primary": "#11111b",
    "bg_secondary": "#1e1e2e",
    "bg_tertiary": "#313244",
    "border": "#45475a",
    "text_primary": "#cdd6f4",
    "text_secondary": "#6c7086",
    "accent_blue": "#89b4fa",
    "accent_purple": "#b4befe",
    "accent_green": "#a6e3a1",
    "accent_yellow": "#f9e2af",
    "accent_red": "#f38ba8",
}

# === SUBTITLE STYLES ===
SUBTITLE_PRESETS = {
    "alex_hormozi": {
        "font": "Arial",
        "font_size": 70,
        "color": "#FFD700",
        "highlight_color": "#00FF00",
        "stroke_width": 3,
        "animation": "pop",
    },
    "mrbeast": {
        "font": "Impact",
        "font_size": 80,
        "color": "#FFFFFF",
        "highlight_color": "#FF0000",
        "stroke_width": 4,
        "animation": "zoom",
    },
    "minimalist": {
        "font": "Helvetica",
        "font_size": 60,
        "color": "#FFFFFF",
        "highlight_color": "#89b4fa",
        "stroke_width": 1,
        "animation": "fade",
    },
}

# === VIDEO SETTINGS ===
VIDEO_CONFIG = {
    "target_ratio": 9 / 16,
    "fps": 30,
    "codec": "libx264",
    "audio_codec": "aac",
    "preset": "medium",
    "bitrate": "5000k",
    "threads": 4,
}

# === ANALYSIS SETTINGS ===
ANALYSIS_CONFIG = {
    "max_segment_duration": 55,
    "min_segment_duration": 3,
    "language": "ru",
}

# === UI SETTINGS ===
UI_CONFIG = {
    "window_width": 1200,
    "window_height": 900,
    "card_border_radius": 15,
    "shadow_blur": 20,
    "animation_duration": 300,
}