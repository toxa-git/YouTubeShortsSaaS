# ai_engine.py
"""AI engine for speech recognition and face detection"""

import os
import whisper
import numpy as np
import cv2
import mediapipe as mp
import warnings
from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy.video.io.VideoFileClip import VideoFileClip

warnings.filterwarnings("ignore")


class WhisperEngine:
    """Handles speech recognition"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """Load Whisper model"""
        self.model = whisper.load_model(self.model_size)
    
    def transcribe(self, video_path: str, language: str = "ru") -> Dict:
        """Transcribe video to text with word timestamps"""
        if not self.model:
            self.load_model()
        
        result = self.model.transcribe(
            video_path,
            word_timestamps=True,
            language=language,
            task="transcribe",
            verbose=False
        )
        
        return result


class FaceDetector:
    """Detects faces for smart cropping"""
    
    def __init__(self):
        self.mp_face = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.detector = self.mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in a frame"""
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb_frame)
        
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                faces.append({
                    "x": int(bbox.xmin * w),
                    "y": int(bbox.ymin * h),
                    "width": int(bbox.width * w),
                    "height": int(bbox.height * h),
                })
        
        return faces
    
    def get_optimal_crop(
        self,
        frame_w: int,
        frame_h: int,
        target_ratio: float = 9/16,
        faces: Optional[List[Dict]] = None
    ) -> Tuple[int, int, int, int]:
        """
        Calculate optimal crop area for Shorts (9:16)
        If faces detected, center crop on face. Otherwise use video center.
        
        Returns: (x1, y1, x2, y2)
        """
        target_w = frame_h * target_ratio
        
        if target_w > frame_w:
            target_w = frame_w
        
        if faces:
            # Center on face
            face = faces[0]  # Use first detected face
            face_center_x = face["x"] + face["width"] // 2
            x1 = max(0, int(face_center_x - target_w / 2))
            x1 = min(x1, frame_w - int(target_w))
        else:
            # Center on video
            x1 = int((frame_w - target_w) / 2)
        
        x2 = int(x1 + target_w)
        y1 = 0
        y2 = frame_h
        
        return x1, y1, x2, y2


class AnalysisThread(QThread):
    """Threaded video analysis"""
    
    status_update = pyqtSignal(str)
    log_update = pyqtSignal(str, str)  # message, level
    finished = pyqtSignal(list, float, float)  # segments, width, height
    
    def __init__(self, video_path: str, model_size: str = "base"):
        super().__init__()
        self.video_path = video_path
        self.model_size = model_size
        self.whisper_engine = WhisperEngine(model_size)
    
    def run(self):
        """Execute analysis"""
        try:
            self.status_update.emit("🔊 Загрузка модели Whisper...")
            self.log_update.emit(
                f"Загрузка модели '{self.model_size}'...",
                "info"
            )
            
            self.whisper_engine.load_model()
            
            self.status_update.emit("🎤 Распознавание речи...")
            self.log_update.emit(
                "Анализ аудиодорожки (это может занять пару минут)...",
                "info"
            )
            
            result = self.whisper_engine.transcribe(self.video_path)
            segments = result['segments']
            
            self.log_update.emit(
                f"✅ Распознано {len(segments)} сегментов речи",
                "success"
            )
            
            # Get video dimensions
            clip = VideoFileClip(self.video_path)
            w, h = clip.size
            clip.close()
            
            self.finished.emit(segments, w, h)
            
        except Exception as e:
            self.log_update.emit(f"❌ Ошибка анализа: {str(e)}", "error")
            self.finished.emit([], 0, 0)