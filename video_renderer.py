# video_renderer.py
"""Video rendering and processing"""

import os
import numpy as np
from math import sin
from typing import List, Tuple, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import cv2

from YouTubeShortsSaaS.config import VIDEO_CONFIG
from YouTubeShortsSaaS.ai_engine import FaceDetector
from YouTubeShortsSaaS.utils import EmojiMapper


class SubtitleRenderer:
    """Renders animated subtitles"""
    
    # Animation types
    ANIMATION_POP = "pop"
    ANIMATION_ZOOM = "zoom"
    ANIMATION_FADE = "fade"
    ANIMATION_SLIDE = "slide"
    
    def __init__(
        self,
        font_name: str,
        font_size: int,
        color: str,
        highlight_color: str,
        stroke_width: int,
        animation_type: str = "pop"
    ):
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.highlight_color = highlight_color
        self.stroke_width = stroke_width
        self.animation_type = animation_type
    
    def create_word_clip(
        self,
        text: str,
        start_t: float,
        end_t: float,
        y_position: int,
        is_highlight: bool = False
    ) -> Optional['TextClip']:
        """Create animated text clip for a word"""
        duration = end_t - start_t
        
        if duration <= 0.05:
            return None
        
        # Use highlight color if this is current word
        text_color = self.highlight_color if is_highlight else self.color
        
        txt_clip = TextClip(
            text.upper(),
            fontsize=self.font_size,
            color=text_color,
            font=self.font_name,
            stroke_color="black",
            stroke_width=self.stroke_width,
            method="caption"
        ).set_start(start_t).set_duration(duration).set_position(("center", y_position))
        
        # Apply animation
        txt_clip = self._apply_animation(txt_clip, start_t, duration)
        
        return txt_clip
    
    def _apply_animation(
        self,
        clip: 'TextClip',
        start_t: float,
        duration: float
    ) -> 'TextClip':
        """Apply animation effect to clip"""
        
        if self.animation_type == self.ANIMATION_POP:
            return self._animate_pop(clip, start_t, duration)
        elif self.animation_type == self.ANIMATION_ZOOM:
            return self._animate_zoom(clip, start_t, duration)
        elif self.animation_type == self.ANIMATION_FADE:
            return self._animate_fade(clip, start_t, duration)
        elif self.animation_type == self.ANIMATION_SLIDE:
            return self._animate_slide(clip, start_t, duration)
        
        return clip
    
    def _animate_pop(self, clip: 'TextClip', start_t: float, duration: float) -> 'TextClip':
        """Pop animation"""
        def scale_func(t):
            local_t = t - start_t
            if local_t < 0:
                return 1.0
            if local_t < 0.15:
                return 1.0 + 0.25 * sin(local_t * 20)
            return 1.0
        
        return clip.resize(scale_func)
    
    def _animate_zoom(self, clip: 'TextClip', start_t: float, duration: float) -> 'TextClip':
        """Zoom animation"""
        def scale_func(t):
            local_t = t - start_t
            if local_t < 0:
                return 0.8
            progress = min(local_t / 0.2, 1.0)
            return 0.8 + (0.2 * progress)
        
        return clip.resize(scale_func)
    
    def _animate_fade(self, clip: 'TextClip', start_t: float, duration: float) -> 'TextClip':
        """Fade animation"""
        def opacity_func(t):
            local_t = t - start_t
            if local_t < 0:
                return 0.0
            if local_t < 0.1:
                return local_t / 0.1
            return 1.0
        
        return clip.set_opacity(opacity_func)
    
    def _animate_slide(self, clip: 'TextClip', start_t: float, duration: float) -> 'TextClip':
        """Slide animation"""
        def pos_func(t):
            local_t = t - start_t
            if local_t < 0:
                return (-0.5, "center")
            if local_t < 0.2:
                x = -0.5 + (local_t / 0.2) * 0.5
                return (x, "center")
            return ("center", "center")
        
        return clip.set_position(pos_func)


class RenderThread(QThread):
    """Threaded video rendering"""
    
    status_update = pyqtSignal(str)
    log_update = pyqtSignal(str, str)  # message, level
    progress_update = pyqtSignal(bool)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        segments: List[dict],
        video_size: Tuple[int, int],
        font_name: str,
        text_color: str,
        highlight_color: str,
        font_size: int,
        stroke_width: int,
        animation_type: str,
        use_face_detection: bool = True,
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.start_time = start_time
        self.end_time = end_time
        self.segments = segments
        self.video_size = video_size
        self.font_name = font_name
        self.text_color = text_color
        self.highlight_color = highlight_color
        self.font_size = font_size
        self.stroke_width = stroke_width
        self.animation_type = animation_type
        self.use_face_detection = use_face_detection
        
        self.subtitle_renderer = SubtitleRenderer(
            font_name, font_size, text_color, highlight_color,
            stroke_width, animation_type
        )
        self.face_detector = FaceDetector() if use_face_detection else None
    
    def run(self):
        """Execute rendering"""
        try:
            self.progress_update.emit(True)
            self.log_update.emit(
                f"🎬 Рендеринг фрагмента {int(self.start_time)}с - {int(self.end_time)}с",
                "info"
            )
            
            # Load and cut video
            self.status_update.emit("✂️ Вырезание фрагмента...")
            clip = VideoFileClip(self.input_path).subclip(
                self.start_time, self.end_time
            )
            
            # Smart cropping with face detection
            self.status_update.emit("👁️ Умная обрезка видео...")
            w, h = clip.size
            clip = self._smart_crop(clip, w, h)
            
            # Create subtitles
            self.status_update.emit("🎨 Создание субтитров...")
            subtitle_clips = self._create_subtitles(clip.duration)
            
            # Composite
            self.status_update.emit("🎬 Финальный рендеринг...")
            final_video = CompositeVideoClip([clip] + subtitle_clips)
            
            # Render
            final_video.write_videofile(
                self.output_path,
                codec=VIDEO_CONFIG["codec"],
                audio_codec=VIDEO_CONFIG["audio_codec"],
                fps=VIDEO_CONFIG["fps"],
                preset=VIDEO_CONFIG["preset"],
                bitrate=VIDEO_CONFIG["bitrate"],
                threads=VIDEO_CONFIG["threads"],
                verbose=False,
                logger=None
            )
            
            clip.close()
            for c in subtitle_clips:
                c.close()
            
            self.progress_update.emit(False)
            self.log_update.emit("✅ Фрагмент успешно сохранен!", "success")
            self.finished.emit(True, f"Видео сохранено:\n{self.output_path}")
            
        except Exception as e:
            self.progress_update.emit(False)
            self.log_update.emit(f"❌ Ошибка рендеринга: {str(e)}", "error")
            self.finished.emit(False, str(e))
    
    def _smart_crop(self, clip: 'VideoFileClip', w: int, h: int) -> 'VideoFileClip':
        """Smart crop with face detection"""
        target_w = h * VIDEO_CONFIG["target_ratio"]
        
        if target_w <= w:
            if self.use_face_detection and self.face_detector:
                # Get first frame for face detection
                first_frame = clip.get_frame(0)
                faces = self.face_detector.detect_faces(first_frame)
                x1, y1, x2, y2 = self.face_detector.get_optimal_crop(
                    w, h, VIDEO_CONFIG["target_ratio"], faces if faces else None
                )
            else:
                # Center crop
                x1 = int((w - target_w) / 2)
                x2 = int(x1 + target_w)
                y1, y2 = 0, h
            
            clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
            self.log_update.emit(
                f"✅ Видео обрезано до {int(x2-x1)}x{h}",
                "success"
            )
        
        return clip
    
    def _create_subtitles(self, clip_duration: float) -> List:
        """Create subtitle clips"""
        clips = []
        y_position = int(clip_duration * 0.75)  # Approximate
        word_count = 0
        
        # Filter segments
        relevant_segments = [
            seg for seg in self.segments
            if seg['end'] > self.start_time and seg['start'] < self.end_time
        ]
        
        for segment in relevant_segments:
            if 'words' not in segment:
                continue
            
            for i, word_data in enumerate(segment['words']):
                word_text = word_data['word'].strip()
                if not word_text:
                    continue
                
                start_t = word_data['start'] - self.start_time
                end_t = word_data['end'] - self.start_time
                
                if start_t < 0 or end_t > clip_duration:
                    continue
                
                # Highlight current word
                is_highlight = (i % 3 == 0)  # Highlight every 3rd word
                
                # Add emoji
                emoji = EmojiMapper.find_emoji(word_text)
                display_text = f"{word_text} {emoji}" if emoji else word_text
                
                txt_clip = self.subtitle_renderer.create_word_clip(
                    display_text, start_t, end_t, y_position, is_highlight
                )
                
                if txt_clip:
                    clips.append(txt_clip)
                    word_count += 1
        
        self.log_update.emit(f"✅ Создано {word_count} анимированных слов", "success")
        return clips