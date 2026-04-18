# ui_manager.py
"""Main UI Manager for the application"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGroupBox, QGridLayout, QFileDialog, QColorDialog, QMessageBox,
    QComboBox, QSpinBox, QLineEdit, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from YouTubeShortsSaaS.config import COLORS, UI_CONFIG, SUBTITLE_PRESETS
from YouTubeShortsSaaS.ui_components import ModernButton, ShortCard, DropZone, SettingsPanel
from YouTubeShortsSaaS.ai_engine import AnalysisThread
from YouTubeShortsSaaS.video_renderer import RenderThread
from YouTubeShortsSaaS.utils import Logger, TimeFormatter


class UIManager(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.segments = []
        self.video_width = 0
        self.video_height = 0
        self.current_video_path = ""
        self.analysis_thread = None
        self.render_thread = None
        self.render_threads = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("🎬 YouTube Shorts Creator Pro")
        self.setMinimumSize(UI_CONFIG["window_width"], UI_CONFIG["window_height"])
        
        self.apply_global_stylesheet()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title = QLabel("🎥 YOUTUBE SHORTS CREATOR PRO")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {COLORS['accent_blue']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel(
            "Интеллектуальная нарезка видео на вирусные Shorts "
            "с умным распознаванием лиц и динамическими субтитрами"
        )
        subtitle.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.on_file_dropped)
        main_layout.addWidget(self.drop_zone)
        
        # Input path (hidden)
        self.input_path_label = QLabel("")
        self.input_path_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        main_layout.addWidget(self.input_path_label)
        
        # Settings
        self.settings_panel = SettingsPanel()
        main_layout.addWidget(self.settings_panel)
        
        # Analyze button
        self.analyze_btn = ModernButton("🔍 АНАЛИЗИРОВАТЬ ВИДЕО", is_primary=True)
        self.analyze_btn.setMinimumHeight(50)
        self.analyze_btn.setStyleSheet(self.analyze_btn.styleSheet() + f"\nfont-size: 14px;")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        main_layout.addWidget(self.analyze_btn)
        
        # Results group
        self.results_group = QGroupBox("🎬 НАЙДЕННЫЕ ФРАГМЕНТЫ")
        self.results_group.setVisible(False)
        results_layout = QVBoxLayout(self.results_group)
        
        self.video_info_label = QLabel("")
        self.video_info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        results_layout.addWidget(self.video_info_label)
        
        # Export all button
        export_all_btn = ModernButton("📦 ЭКСПОРТИРОВАТЬ ВСЕ", is_primary=True)
        export_all_btn.clicked.connect(self.export_all_fragments)
        results_layout.addWidget(export_all_btn)
        
        # Cards scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(500)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(8)
        scroll.setWidget(self.cards_widget)
        
        results_layout.addWidget(scroll)
        main_layout.addWidget(self.results_group)
        
        # Log area
        log_group = QGroupBox("📊 ЛОГ СОБЫТИЙ")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent_green']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                padding: 8px;
            }}
        """)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group)
        
        main_layout.addStretch()
    
    def apply_global_stylesheet(self):
        """Apply global stylesheet"""
        stylesheet = f"""
            QMainWindow {{
                background-color: {COLORS['bg_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit, QSpinBox, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                selection-background-color: {COLORS['accent_blue']};
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid {COLORS['accent_blue']};
            }}
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent_green']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }}
            QGroupBox {{
                color: {COLORS['accent_blue']};
                font-weight: bold;
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['accent_blue']};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    @pyqtSlot(str)
    def on_file_dropped(self, file_path: str):
        """Handle file dropped on drop zone"""
        if os.path.exists(file_path):
            self.current_video_path = file_path
            self.input_path_label.setText(f"📁 {os.path.basename(file_path)}")
            self.analyze_btn.setEnabled(True)
            self.add_log(f"Видео загружено: {os.path.basename(file_path)}", "success")
    
    def add_log(self, message: str, level: str = "info"):
        """Add message to log"""
        formatted, _ = Logger.log(message, level)
        self.log_text.append(formatted)
    
    def start_analysis(self):
        """Start video analysis"""
        if not self.current_video_path:
            QMessageBox.critical(self, "Ошибка", "Выберите видеофайл!")
            return
        
        if not os.path.exists(self.current_video_path):
            QMessageBox.critical(self, "Ошибка", "Файл не найден!")
            return
        
        self.clear_cards()
        self.results_group.setVisible(False)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("⏳ АНАЛИЗ...")
        
        # Start analysis thread
        self.analysis_thread = AnalysisThread(
            self.current_video_path,
            self.settings_panel.model_combo.currentText()
        )
        
        self.analysis_thread.status_update.connect(self.add_log)
        self.analysis_thread.log_update.connect(
            lambda msg, lvl: self.add_log(msg, lvl)
        )
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.start()
    
    @pyqtSlot(list, float, float)
    def on_analysis_finished(self, segments: list, width: float, height: float):
        """Handle analysis completion"""
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 АНАЛИЗИРОВАТЬ ВИДЕО")
        
        if not segments:
            QMessageBox.warning(self, "Внимание", "Речь в видео не распознана!")
            return
        
        self.segments = segments
        self.video_width = int(width)
        self.video_height = int(height)
        
        # Split into episodes
        episodes = self.split_into_episodes(segments)
        
        if not episodes:
            QMessageBox.warning(self, "Внимание", "Нет подходящих фрагментов!")
            return
        
        # Create cards
        for i, episode in enumerate(episodes):
            start_t = episode[0]['start']
            end_t = episode[-1]['end']
            
            text_preview = " ".join(
                [seg.get('text', '').strip() for seg in episode[:3]]
            )
            if len(text_preview) > 150:
                text_preview = text_preview[:150] + "..."
            
            word_count = sum(len(seg.get('words', [])) for seg in episode)
            
            card = ShortCard(i, start_t, end_t, text_preview, word_count)
            card.render_requested.connect(self.render_fragment)
            card.preview_requested.connect(self.preview_fragment)
            self.cards_layout.addWidget(card)
        
        # Show results
        duration = segments[-1]['end']
        self.video_info_label.setText(
            f"📹 {os.path.basename(self.current_video_path)} | "
            f"Длительность: {TimeFormatter.seconds_to_string(duration)} | "
            f"Фрагментов: {len(episodes)}"
        )
        self.results_group.setVisible(True)
        
        self.add_log(f"Найдено {len(episodes)} фрагментов для Shorts", "success")
    
    def split_into_episodes(self, segments: list, max_duration: float = 55) -> list:
        """Split segments into episodes"""
        episodes = []
        current = []
        current_dur = 0
        
        for seg in segments:
            dur = seg['end'] - seg['start']
            
            if dur > max_duration:
                continue
            
            if current_dur + dur > max_duration and current:
                episodes.append(current)
                current = []
                current_dur = 0
            
            current.append(seg)
            current_dur += dur
        
        if current:
            episodes.append(current)
        
        return episodes
    
    def render_fragment(self, index: int, start_t: float, end_t: float):
        """Render a single fragment"""
        base_name = os.path.splitext(os.path.basename(self.current_video_path))[0]
        default_name = f"{base_name}_shorts_{index+1}.mp4"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Сохранить фрагмент #{index+1}", default_name, "MP4 видео (*.mp4)"
        )
        
        if not file_path:
            return
        
        settings = self.settings_panel.get_settings()
        
        # Create render thread
        render_thread = RenderThread(
            self.current_video_path,
            file_path,
            start_t,
            end_t,
            self.segments,
            (self.video_width, self.video_height),
            settings["font"],
            settings["color"],
            settings["highlight_color"],
            settings["font_size"],
            settings["stroke_width"],
            settings["animation"],
            use_face_detection=True
        )
        
        render_thread.status_update.connect(self.add_log)
        render_thread.log_update.connect(
            lambda msg, lvl: self.add_log(msg, lvl)
        )
        render_thread.finished.connect(
            lambda success, msg: self.on_render_finished(success, msg)
        )
        
        self.render_threads.append(render_thread)
        render_thread.start()
    
    def preview_fragment(self, index: int):
        """Preview fragment information"""
        card = self.cards_layout.itemAt(index).widget()
        if card:
            dur = card.end_time - card.start_time
            QMessageBox.information(
                self,
                f"Фрагмент #{index+1}",
                f"Время: {TimeFormatter.seconds_to_string(card.start_time)} - "
                f"{TimeFormatter.seconds_to_string(card.end_time)}\n"
                f"Длительность: {int(dur)}с\n"
                f"Слов: {card.word_count}"
            )
    
    def export_all_fragments(self):
        """Export all fragments"""
        if self.cards_layout.count() == 0:
            return
        
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if not folder:
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Создать {self.cards_layout.count()} видео?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        base_name = os.path.splitext(os.path.basename(self.current_video_path))[0]
        
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card:
                output = os.path.join(folder, f"{base_name}_shorts_{i+1}.mp4")
                self.render_fragment(i, card.start_time, card.end_time)
        
        self.add_log(f"Все {self.cards_layout.count()} фрагментов добавлены в очередь", "success")
    
    def on_render_finished(self, success: bool, message: str):
        """Handle render completion"""
        if success:
            QMessageBox.information(self, "✅ Успех", message)
            self.add_log("Рендеринг завершен успешно", "success")
        else:
            QMessageBox.critical(self, "❌ Ошибка", message)
            self.add_log(f"Ошибка рендеринга: {message}", "error")
    
    def clear_cards(self):
        """Clear all cards"""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()