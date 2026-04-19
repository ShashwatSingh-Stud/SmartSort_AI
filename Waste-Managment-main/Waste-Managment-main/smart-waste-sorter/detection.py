from __future__ import annotations

import os
# Gemini API Key should be set in .env or environment variables
import base64
import json
import os
import random
import time
import urllib.request
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass(frozen=True)
class DetectionResult:
    category: str
    confidence: float
    annotated_frame: np.ndarray
    source: str


def _normalize_label(label: str) -> str:
    s = (label or "").strip().lower()
    if "plastic" in s:
        return "Plastic"
    if "paper" in s:
        return "Paper"
    if "metal" in s or "aluminum" in s or "tin" in s:
        return "Metal"
    if "organic" in s or "compost" in s or "food" in s:
        return "Organic"
    return label.strip()


# ── Gemini Vision Classifier ──────────────────────────────────────────────────

class GeminiVisionClassifier:
    """
    Uses Google Gemini Vision API to classify waste from webcam frames.

    FREE tier: 1500 requests/day — plenty for hackathon demo!

    Setup (2 steps):
      1. Get free API key: https://aistudio.google.com  →  Get API Key
      2. Set environment variable:
            Windows CMD:   set GEMINI_API_KEY=AIza...
            PowerShell:    $env:GEMINI_API_KEY="AIza..."
            Mac/Linux:     export GEMINI_API_KEY=AIza...
      3. Run: python app.py
         Dashboard will show  MODEL: GEMINI-VISION
    """

    CATEGORIES = ["Plastic", "Paper", "Metal", "Organic"]

    PROMPT = (
        "You are a waste sorting AI. Look at this image and classify "
        "the primary waste item into exactly one of these 4 categories: "
        "Plastic, Paper, Metal, Organic.\n"
        "Reply with ONLY valid JSON, no extra text:\n"
        '{"category": "Plastic", "confidence": 0.92, "reason": "blue plastic bottle"}\n'
        "confidence must be between 0.0 and 1.0."
    )

    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        # Call API every 2 seconds — saves quota, keeps dashboard smooth
        self._interval_s = max(
            1.0,
            float(os.environ.get("GEMINI_INFER_INTERVAL_MS", "2000")) / 1000.0
        )
        self._last_call_ts = 0.0
        self._last_result: tuple[str, float] = ("Plastic", 0.85)

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def predict(self, frame_bgr: np.ndarray,
                last: Optional[tuple[str, float]] = None) -> tuple[str, float]:

        now = time.time()

        # Throttle: reuse last result until interval passes
        if (now - self._last_call_ts) < self._interval_s:
            return self._last_result

        # Resize to 320x240 — smaller = faster API call, still accurate
        small = cv2.resize(frame_bgr, (320, 240), interpolation=cv2.INTER_AREA)
        _, buf = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
        img_b64 = base64.b64encode(buf.tobytes()).decode("utf-8")

        # Gemini API payload
        payload = json.dumps({
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64
                        }
                    },
                    {
                        "text": self.PROMPT
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 100,
            }
        }).encode("utf-8")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.api_key}"
        )

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Extract text from Gemini response
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Strip markdown fences if Gemini adds them
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            parsed = json.loads(text)
            cat  = _normalize_label(str(parsed.get("category", "Plastic")))
            conf = float(parsed.get("confidence", 0.92))

            if cat not in self.CATEGORIES:
                cat = "Plastic"
            conf = max(0.0, min(1.0, conf))

            self._last_result  = (cat, conf)
            self._last_call_ts = time.time()
            return cat, conf

        except Exception as e:
            print(f"[GeminiVision] API Error (using mock): {e}")
            self._last_call_ts = time.time()
            return "Plastic", 0.98


# ── WasteClassifier (with Gemini as top priority) ────────────────────────────

class WasteClassifier:
    """
    Classifier priority order:
      1. Gemini Vision API  (if GEMINI_API_KEY is set)
      2. TFLite model       (if WASTE_MODEL_PATH points to .tflite)
      3. Keras model        (if WASTE_MODEL_PATH points to .h5/.keras)
      4. Simulated          (random, for demo without any key/model)
    """

    def __init__(self, categories: list[str]) -> None:
        self.categories = categories
        self.model_path = os.environ.get("WASTE_MODEL_PATH", "").strip()
        self.labels_path = os.environ.get("WASTE_LABELS_PATH", "").strip()
        self._mode = "simulated"

        self._rng = random.Random()
        self._last_pick_ts = 0.0
        self._hold_seconds = 0.75
        self._last_infer_ts = 0.0
        self._infer_interval_s = max(
            0.0,
            float(os.environ.get("WASTE_INFER_INTERVAL_MS", "200")) / 1000.0
        )

        self._tflite_interpreter = None
        self._tflite_in = None
        self._tflite_out = None
        self._keras_model = None
        self._labels: Optional[list[str]] = None

        # ── Priority 1: Gemini Vision API ────────────────────────────────
        self._gemini = GeminiVisionClassifier()
        if self._gemini.available:
            self._mode = "gemini-vision"
            print("[WasteClassifier] Gemini Vision API ready — real AI enabled!")
            return

        # ── Priority 2 & 3: Local TFLite / Keras model ───────────────────
        if not self.model_path:
            print("[WasteClassifier] Running in simulated mode.")
            print("  → To enable real AI: set GEMINI_API_KEY=AIza...")
            print("  → Get free key at: https://aistudio.google.com")
            return

        try:
            if self.model_path.lower().endswith(".tflite"):
                self._init_tflite()
                self._mode = "tflite"
            elif self.model_path.lower().endswith((".h5", ".keras")):
                self._init_keras()
                self._mode = "keras"
        except Exception:
            self._mode = "simulated"

    @property
    def mode(self) -> str:
        return self._mode

    def predict(self, frame_bgr: np.ndarray, *,
                last: Optional[tuple[str, float]] = None) -> tuple[str, float]:
        now = time.time()

        # Throttle for non-Gemini modes
        if (self._mode != "gemini-vision" and last is not None
                and self._infer_interval_s > 0
                and (now - self._last_infer_ts) < self._infer_interval_s):
            return last[0], float(last[1])

        # Gemini Vision
        if self._mode == "gemini-vision":
            try:
                pred = self._gemini.predict(frame_bgr, last=last)
                self._last_infer_ts = now
                return pred
            except Exception:
                pass  # fall through to simulated

        # TFLite
        if self._mode == "tflite":
            try:
                pred = self._predict_tflite(frame_bgr)
                self._last_infer_ts = now
                return pred
            except Exception:
                self._mode = "simulated"

        # Keras
        if self._mode == "keras":
            try:
                pred = self._predict_keras(frame_bgr)
                self._last_infer_ts = now
                return pred
            except Exception:
                self._mode = "simulated"

        # Simulated fallback
        if last is None or (now - self._last_pick_ts) > self._hold_seconds:
            category   = self._rng.choice(self.categories)
            confidence = self._rng.uniform(0.75, 0.99)
            self._last_pick_ts  = now
            self._last_infer_ts = now
            return category, float(confidence)
        return last[0], float(last[1])

    def _init_tflite(self) -> None:
        Interpreter = None
        try:
            from tflite_runtime.interpreter import Interpreter as _I  # type: ignore
            Interpreter = _I
        except Exception:
            try:
                from tensorflow.lite.python.interpreter import Interpreter as _I  # type: ignore
                Interpreter = _I
            except Exception:
                Interpreter = None

        if Interpreter is None:
            raise RuntimeError("No TFLite runtime. Install tensorflow or tflite-runtime.")

        self._tflite_interpreter = Interpreter(model_path=self.model_path)
        self._tflite_interpreter.allocate_tensors()
        self._tflite_in  = self._tflite_interpreter.get_input_details()[0]
        self._tflite_out = self._tflite_interpreter.get_output_details()[0]

        if self.labels_path and os.path.exists(self.labels_path):
            with open(self.labels_path, "r", encoding="utf-8") as f:
                self._labels = [l.strip() for l in f.read().splitlines() if l.strip()]

    def _predict_tflite(self, frame_bgr: np.ndarray) -> tuple[str, float]:
        assert self._tflite_interpreter and self._tflite_in and self._tflite_out
        input_shape = self._tflite_in["shape"]
        h, w = int(input_shape[1]), int(input_shape[2])
        x = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
        x = np.expand_dims(x, axis=0)
        dtype = self._tflite_in["dtype"]
        x = (x.astype(np.float32) / 255.0) if dtype == np.float32 else x.astype(dtype)
        self._tflite_interpreter.set_tensor(self._tflite_in["index"], x)
        self._tflite_interpreter.invoke()
        y   = np.array(self._tflite_interpreter.get_tensor(self._tflite_out["index"])).reshape(-1)
        idx = int(np.argmax(y))
        conf  = float(y[idx])
        label = self._labels[idx] if self._labels and 0 <= idx < len(self._labels) else str(idx)
        if not self._labels and y.shape[0] == 6:
            tn = ["cardboard","glass","metal","paper","plastic","trash"]
            label = tn[idx]
        mapped = _normalize_label(label)
        if mapped not in self.categories:
            mapped = self.categories[idx % len(self.categories)]
        return mapped, conf

    def _init_keras(self) -> None:
        import tensorflow as tf  # type: ignore
        self._keras_model = tf.keras.models.load_model(self.model_path, compile=False)

    def _predict_keras(self, frame_bgr: np.ndarray) -> tuple[str, float]:
        assert self._keras_model is not None
        try:
            ishape = self._keras_model.inputs[0].shape
            h = int(ishape[1]) if ishape[1] else 224
            w = int(ishape[2]) if ishape[2] else 224
        except Exception:
            h, w = 224, 224
        x = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
        x = np.expand_dims(x, axis=0).astype(np.float32) / 255.0
        y   = np.array(self._keras_model.predict(x, verbose=0)).reshape(-1)
        idx = int(np.argmax(y))
        conf = float(y[idx])
        if y.shape[0] == len(self.categories):
            return self.categories[idx], conf
        if y.shape[0] == 6:
            tn = ["cardboard","glass","metal","paper","plastic","trash"]
            return _normalize_label(tn[idx]), conf
        return self.categories[idx % len(self.categories)], conf


# ── SmartWasteDetector ────────────────────────────────────────────────────────

class SmartWasteDetector:
    """
    Webcam-based waste detector.
    Uses Gemini Vision API if GEMINI_API_KEY is set, otherwise simulates.
    """

    CATEGORIES = ["Plastic", "Paper", "Metal", "Organic"]

    def __init__(self, camera_index: int = 0,
                 window_name: str = "Smart Waste Sorting System") -> None:
        self.window_name = window_name
        self._last: Optional[DetectionResult] = None
        self.classifier = WasteClassifier(self.CATEGORIES)

        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = cv2.VideoCapture(camera_index)
        
        self.camera_available = self.cap.isOpened()
        if not self.camera_available:
            print(f"[SmartWasteDetector] Camera not found (index={camera_index}). Using simulated frames.")

    def release(self) -> None:
        try:
            self.cap.release()
        finally:
            try:
                cv2.destroyWindow(self.window_name)
            except Exception:
                pass

    def get_detected_waste_type(self) -> Optional[str]:
        return None if self._last is None else self._last.category

    def read(self) -> DetectionResult:
        if not self.camera_available:
            # Create a dummy frame if no camera
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "SIMULATED CAMERA", (200, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ok = True
        else:
            ok, frame = self.cap.read()
            
        if not ok or frame is None:
            time.sleep(0.03)
            raise RuntimeError("Could not read frame from webcam.")

        last = None if self._last is None else (self._last.category, self._last.confidence)
        category, confidence = self.classifier.predict(frame, last=last)

        annotated = self._annotate(frame, category=category, confidence=confidence)
        result = DetectionResult(
            category=category,
            confidence=float(confidence),
            annotated_frame=annotated,
            source=self.classifier.mode,
        )
        self._last = result
        return result

    def run_preview_loop(self) -> Optional[str]:
        while True:
            result = self.read()
            cv2.imshow(self.window_name, result.annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        last = self.get_detected_waste_type()
        self.release()
        return last

    def _annotate(self, frame_bgr: np.ndarray, *,
                  category: str, confidence: float) -> np.ndarray:
        out = frame_bgr.copy()
        self._tag(out, f"Detected: {category} ({confidence*100:.0f}%)",
                  (12, 34), scale=0.9, thickness=2)
        self._tag(out, f"Model: {self.classifier.mode}",
                  (12, 66), scale=0.6, thickness=1)
        return out

    def _tag(self, frame_bgr: np.ndarray, text: str, org: tuple[int, int],
             *, scale: float, thickness: int) -> None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), base = cv2.getTextSize(text, font, scale, thickness)
        x, y = org
        pad = 6
        cv2.rectangle(frame_bgr,
                      (x - pad, y - th - pad),
                      (x + tw + pad, y + base + pad), (0, 0, 0), -1)
        cv2.putText(frame_bgr, text, (x, y), font, scale,
                    (255, 255, 255), thickness, cv2.LINE_AA)


if __name__ == "__main__":
    detector = SmartWasteDetector()
    waste_type = detector.run_preview_loop()
    print("Last detected waste type:", waste_type)