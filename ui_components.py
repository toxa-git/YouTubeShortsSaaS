# ui_components.py
"""Reusable UI components"""

from PyQt6.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QComboBox, QSpinBox, QLineEdit, QGridLayout, QGroupBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from YouTubeShortsSaaS.config import COLORS, SUBTITLE_PRESETS
from YouTubeShortsSaaS.utils import TimeFormatter, ViraityScoreCalculator


class ModernButton(QPushButton):
    """Custom button with modern styling"""
    
    def __init__(self, text: str, is_primary: bool = False):
        super().__init__(text)
        self.is_primary = is_primary
        self.setup_style()
    
    def setup_style(self):
        """Apply modern button style"""
        if self.is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_blue']};
                    color: {COLORS['bg_primary']};
                    border: none;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_purple']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['accent_blue']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['border']};
                }}
            """)


class ShortCard(QFrame):
    """Card displaying a short fragment"""
    
    render_requested = pyqtSignal(int, float, float)
    preview_requested = pyqtSignal(int)
    
    def __init__(
        self,
        index: int,
        start_time: float,
        end_time: float,
        text_preview: str,
        word_count: int
    ):
        super().__init__()
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.word_count = word_count
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup card UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 15px;
                border: 1px solid {COLORS['border']};
                margin: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['accent_blue']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel(f"🎬 Фрагмент #{self.index + 1}")
        title.setStyleSheet(f"font-weight: bold; color: {COLORS['accent_blue']}; font-size: 14px;")
        header.addWidget(title)
        
        # Virality Score Badge
        duration = self.end_time - self.start_time
        virality = ViraityScoreCalculator.calculate(self.index, self.word_count, duration)
        virality_badge = QLabel(f"🔥 Virality: {virality}%")
        virality_badge.setStyleSheet(
            f"background-color: {COLORS['bg_tertiary']}; color: {COLORS['accent_yellow']}; "
            f"padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;"
        )
        header.addWidget(virality_badge)
        
        header.addStretch()
        
        # Time label
        time_text = f"{TimeFormatter.seconds_to_string(self.start_time)} - {TimeFormatter.seconds_to_string(self.end_time)}"
        time_label = QLabel(time_text)
        time_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        header.addWidget(time_label)
        
        # Word count
        words_badge = QLabel(f"📝 {self.word_count} слов")
        words_badge.setStyleSheet(
            f"background-color: {COLORS['bg_primary']}; color: {COLORS['accent_green']}; "
            f"padding: 4px 8px; border-radius: 10px; font-size: 11px;"
        )
        header.addWidget(words_badge)
        
        layout.addLayout(header)
        
        # Text preview
        preview = QTextEdit()
        preview.setHtml(f"<span style='color: {COLORS['text_primary']}; font-size: 12px;'>{text_preview}</span>")
        preview.setReadOnly(True)
        preview.setMaximumHeight(70)
        preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout.addWidget(preview)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = ModernButton("👁 Предпросмотр")
        preview_btn.clicked.connect(lambda: self.preview_requested.emit(self.index))
        btn_layout.addWidget(preview_btn)
        
        render_btn = ModernButton("🚀 Рендерить", is_primary=True)
        render_btn.clicked.connect(lambda: self.render_requested.emit(self.index, self.start_time, self.end_time))
        btn_layout.addWidget(render_btn)
        
        layout.addLayout(btn_layout)


class DropZone(QFrame):
    """Drag and drop zone for video files"""
    
    file_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup drop zone UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border: 2px dashed {COLORS['accent_blue']};
                border-radius: 15px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel("☁️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)
        
        # Text
        text = QLabel("Перетащите видео сюда\nили нажмите для выбора")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        layout.addWidget(text)
        
        # Supported formats
        formats = QLabel("Поддерживаемые форматы: MP4, AVI, MOV, MKV, FLV, WMV")
        formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formats.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(formats)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_primary']};
                    border: 2px solid {COLORS['accent_green']};
                    border-radius: 15px;
                }}
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.setup_ui()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop"""
        self.setup_ui()
        
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.file_dropped.emit(file_path)


class SettingsPanel(QGroupBox):
    """Settings and configuration panel"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__("⚙️ НАСТРОЙКИ РЕНДЕРИНГА")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        layout = QGridLayout(self)
        layout.setSpacing(15)
        
        # Row 1: Model and Preset
        layout.addWidget(QLabel("Модель Whisper:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium"])
        self.model_combo.setCurrentText("base")
        layout.addWidget(self.model_combo, 0, 1)
        
        layout.addWidget(QLabel("Стиль Субтитров:"), 0, 2)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(SUBTITLE_PRESETS.keys())
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        layout.addWidget(self.preset_combo, 0, 3)
        
        # Row 2: Font and Animation
        layout.addWidget(QLabel("Шрифт:"), 1, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Helvetica", "Impact", "Verdana", "Courier"])
        layout.addWidget(self.font_combo, 1, 1)
        
        layout.addWidget(QLabel("Анимация:"), 1, 2)
        self.animation_combo = QComboBox()
        self.animation_combo.addItems(["pop", "zoom", "fade", "slide"])
        layout.addWidget(self.animation_combo, 1, 3)
        
        # Row 3: Font Size and Color
        layout.addWidget(QLabel("Размер Шрифта:"), 2, 0)
        self.font_size = QSpinBox()
        self.font_size.setRange(40, 120)
        self.font_size.setValue(70)
        layout.addWidget(self.font_size, 2, 1)
        
        layout.addWidget(QLabel("Основной Цвет:"), 2, 2)
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit("#FFD700")
        self.color_input.setMaximumWidth(80)
        color_layout.addWidget(self.color_input)
        color_btn = ModernButton("🎨")
        color_btn.setMaximumWidth(50)
        color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout, 2, 3)
        
        # Row 4: Highlight and Stroke
        layout.addWidget(QLabel("Цвет Выделения:"), 3, 0)
        highlight_layout = QHBoxLayout()
        self.highlight_input = QLineEdit("#00FF00")
        self.highlight_input.setMaximumWidth(80)
        highlight_layout.addWidget(self.highlight_input)
        highlight_btn = ModernButton("🎨")
        highlight_btn.setMaximumWidth(50)
        highlight_btn.clicked.connect(self.choose_highlight_color)
        highlight_layout.addWidget(highlight_btn)
        highlight_layout.addStretch()
        layout.addLayout(highlight_layout, 3, 1)
        
        layout.addWidget(QLabel("Толщина Обводки:"), 3, 2)
        self.stroke_spin = QSpinBox()
        self.stroke_spin.setRange(0, 10)
        self.stroke_spin.setValue(2)
        layout.addWidget(self.stroke_spin, 3, 3)
    
    def on_preset_changed(self, preset_name: str):
        """Update UI when preset changes"""
        if preset_name in SUBTITLE_PRESETS:
            preset = SUBTITLE_PRESETS[preset_name]
            self.font_combo.setCurrentText(preset["font"])
            self.font_size.setValue(preset["font_size"])
            self.color_input.setText(preset["color"])
            self.highlight_input.setText(preset["highlight_color"])
            self.stroke_spin.setValue(preset["stroke_width"])
            self.animation_combo.setCurrentText(preset["animation"])
    
    def choose_color(self):
        """Choose color dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_input.setText(color.name())
    
    def choose_highlight_color(self):
        """Choose highlight color dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.highlight_input.setText(color.name())
    
    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            "model": self.model_combo.currentText(),
            "font": self.font_combo.currentText(),
            "font_size": self.font_size.value(),
            "color": self.color_input.text(),
            "highlight_color": self.highlight_input.text(),
            "stroke_width": self.stroke_spin.value(),
            "animation": self.animation_combo.currentText(),
        }