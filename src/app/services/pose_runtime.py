# src/app/services/pose_runtime.py
from __future__ import annotations
from typing import Optional, List
import cv2
import numpy as np
import mediapipe as mp

class PoseRuntime:
    def __init__(self):
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def infer_keypoints(self, bgr: np.ndarray) -> Optional[List[List[float]]]:
        """Retorna lista de keypoints [[x,y,vis], ...] normalizados (0..1) ou None."""
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        res = self._pose.process(rgb)
        if not res.pose_landmarks:
            return None
        kps = []
        for lm in res.pose_landmarks.landmark:
            x = float(lm.x)  # 0..1
            y = float(lm.y)  # 0..1
            v = float(lm.visibility)
            kps.append([x, y, v])
        return kps

    @staticmethod
    def decode_jpeg(jpeg_bytes: bytes) -> Optional[np.ndarray]:
        arr = np.frombuffer(jpeg_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
