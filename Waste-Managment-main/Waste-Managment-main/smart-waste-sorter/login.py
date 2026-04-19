import atexit
import datetime as dt
import json
import os
import threading
import time
import urllib.request

import cv2
from flask import Flask, Response, jsonify, redirect, render_template, request

from detection import SmartWasteDetector


def _create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    detector = SmartWasteDetector()
    stats_lock = threading.Lock()
    counts = {cat: 0 for cat in SmartWasteDetector.CATEGORIES}
    latest = {"category": None, "confidence": 0.0, "ts": 0.0}
    latest_meta = {"source": "simulated"}
    capacities = {cat: 60 for cat in SmartWasteDetector.CATEGORIES}
    events: list[tuple[float, str]] = []
    started_at = time.time()
    stop_event = threading.Event()
    latest_jpg: dict[str, bytes | None] = {"data": None}

    # Gemini API key (same as detection.py mein set ki hai)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

    # Demo login credentials
    USERS = {"admin": "admin123", "guest": "guest123"}

    def _cleanup() -> None:
        try:
            stop_event.set()
            detector.release()
        except Exception:
            pass

    atexit.register(_cleanup)

    def _detection_loop() -> None:
        last_counted = None
        while not stop_event.is_set():
            try:
                result = detector.read()
            except Exception:
                time.sleep(0.05)
                continue

            ok, buf = cv2.imencode(".jpg", result.annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            jpg_bytes = buf.tobytes() if ok else None

            with stats_lock:
                latest["category"] = result.category
                latest["confidence"] = float(result.confidence)
                latest["ts"] = time.time()
                latest_meta["source"] = getattr(result, "source", "simulated")
                latest_jpg["data"] = jpg_bytes

                if result.category != last_counted:
                    counts[result.category] = int(counts.get(result.category, 0)) + 1
                    last_counted = result.category
                    events.append((latest["ts"], result.category))
                    if len(events) > 400:
                        del events[:200]

            time.sleep(0.01)

    threading.Thread(target=_detection_loop, name="waste-detection", daemon=True).start()

    # ── Routes ────────────────────────────────────────────────────────────────

    @app.get("/")
    def index():
        return redirect("/login")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.post("/api/login")
    def api_login():
        data = request.get_json(silent=True) or {}
        u = str(data.get("username", "")).strip()
        p = str(data.get("password", ""))
        if USERS.get(u) == p:
            return jsonify({"ok": True, "role": "admin" if u == "admin" else "guest"})
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    @app.get("/dashboard")
    def dashboard():
        return render_template(
            "dashboard.html",
            categories=SmartWasteDetector.CATEGORIES,
        )

    @app.get("/category/<name>")
    def category_page(name):
        if name not in SmartWasteDetector.CATEGORIES:
            return redirect("/dashboard")
        return render_template(
            "category.html",
            category=name,
            categories=SmartWasteDetector.CATEGORIES,
        )

    @app.get("/api/categories")
    def categories():
        return jsonify({"categories": SmartWasteDetector.CATEGORIES})

    def _mjpeg_frames():
        while True:
            with stats_lock:
                jpg = latest_jpg["data"]
            if not jpg:
                time.sleep(0.05)
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            )
            time.sleep(0.06)

    @app.get("/video_feed")
    def video_feed():
        return Response(_mjpeg_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.get("/api/prediction")
    def prediction():
        with stats_lock:
            cat = latest["category"]
            conf = float(latest["confidence"])
            ts = float(latest["ts"])
        if cat is None:
            return jsonify({"ok": False, "error": "No detection available yet"}), 503
        return jsonify({"ok": True, "category": cat, "confidence": round(conf, 3), "ts": ts})

    # ── AI Disposal Tips ──────────────────────────────────────────────────────
    FALLBACK_TIPS = {
        "Plastic": [
            "Rinse before recycling — food residue contaminates batches",
            "Remove caps and labels if possible before disposal",
            "Flatten bottles to save bin space",
            "Check recycling number (1-7) on the bottom of item",
        ],
        "Paper": [
            "Keep paper dry — wet paper cannot be recycled",
            "Remove staples and plastic windows from envelopes",
            "Shredded paper goes in compost, not recycling bin",
            "Flatten cardboard boxes before placing in bin",
        ],
        "Metal": [
            "Rinse cans to remove food residue before recycling",
            "Aluminium cans are infinitely recyclable — always recycle",
            "Do not crush cans — sorting machines need to identify them",
            "Scrap metal can be taken to dedicated metal recycling centers",
        ],
        "Organic": [
            "Compost fruit and vegetable scraps at home easily",
            "Avoid composting meat or dairy — it attracts pests",
            "Organic waste in landfills produces harmful methane gas",
            "Coffee grounds and eggshells are excellent garden compost",
        ],
    }

    @app.get("/api/tips")
    def tips():
        category = request.args.get("category", "Plastic").strip()
        if category not in SmartWasteDetector.CATEGORIES:
            category = "Plastic"

        if not GEMINI_API_KEY:
            return jsonify({"tips": FALLBACK_TIPS.get(category, []), "source": "fallback"})

        prompt = (
            f"Give exactly 4 practical disposal tips for {category} waste. "
            "Each tip must be actionable and under 15 words. "
            "Reply ONLY with a JSON array of 4 strings, no markdown, no extra text: "
            '["tip1", "tip2", "tip3", "tip4"]'
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 200},
        }).encode("utf-8")

        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            tips_list = json.loads(text.strip())
            return jsonify({"tips": tips_list[:4], "source": "gemini"})
        except Exception:
            return jsonify({"tips": FALLBACK_TIPS.get(category, []), "source": "fallback"})

    # ── Stats ─────────────────────────────────────────────────────────────────
    @app.get("/api/stats")
    def stats():
        with stats_lock:
            snapshot_counts = dict(counts)
            snapshot_caps = dict(capacities)
            snapshot_events = list(events)
            cat = latest["category"]
            conf = float(latest["confidence"])
            ts = float(latest["ts"])
            source = str(latest_meta.get("source", "simulated"))

        total = int(sum(int(v) for v in snapshot_counts.values()))
        distribution_pct = {
            k: (0.0 if total <= 0 else round((int(snapshot_counts.get(k, 0)) / total) * 100.0, 1))
            for k in SmartWasteDetector.CATEGORIES
        }
        fill_pct = {
            k: (
                0.0
                if int(snapshot_caps.get(k, 0)) <= 0
                else round(min(int(snapshot_counts.get(k, 0)) / int(snapshot_caps[k]), 1.0) * 100.0, 1)
            )
            for k in SmartWasteDetector.CATEGORIES
        }

        now = time.time()
        events_last_min = [e for e in snapshot_events if (now - float(e[0])) <= 60.0]
        items_per_min = int(len(events_last_min))
        fullest_bin = max(SmartWasteDetector.CATEGORIES, key=lambda k: fill_pct.get(k, 0.0))

        alerts = []
        for k in SmartWasteDetector.CATEGORIES:
            if float(fill_pct.get(k, 0.0)) >= 90.0:
                alerts.append({
                    "type": "capacity", "severity": "high", "category": k,
                    "fill_pct": float(fill_pct[k]),
                    "message": "Bin Full - Collection Required",
                    "detail": f"{k} bin has reached {fill_pct[k]}% capacity.",
                })

        co2_factor_kg = {"Plastic": 1.7, "Paper": 1.0, "Metal": 2.4, "Organic": 0.4}
        co2_saved = float(sum(
            float(snapshot_counts.get(k, 0)) * float(co2_factor_kg.get(k, 0.0))
            for k in SmartWasteDetector.CATEGORIES
        ))
        recyclable = (int(snapshot_counts.get("Plastic", 0))
                      + int(snapshot_counts.get("Paper", 0))
                      + int(snapshot_counts.get("Metal", 0)))
        recycling_eff = 0.0 if total <= 0 else round((recyclable / total) * 100.0, 1)

        now_dt = dt.datetime.now()
        midnight_ts = dt.datetime(now_dt.year, now_dt.month, now_dt.day).timestamp()
        processed_today = int(sum(1 for t, _c in snapshot_events if float(t) >= midnight_ts))

        impact = {
            "co2_saved_kg": round(co2_saved, 2),
            "recycling_efficiency_pct": recycling_eff,
            "waste_processed_today": processed_today,
        }

        avg_fill = float(sum(fill_pct.values()) / max(1, len(fill_pct)))
        base = avg_fill / 100.0
        city_bins = [
            {"id": "SC-101", "name": "Central Plaza",   "x": 18, "y": 34},
            {"id": "SC-102", "name": "Metro Station",   "x": 42, "y": 28},
            {"id": "SC-103", "name": "University Gate", "x": 66, "y": 36},
            {"id": "SC-104", "name": "Tech Park",       "x": 76, "y": 62},
            {"id": "SC-105", "name": "Old Town",        "x": 34, "y": 66},
            {"id": "SC-106", "name": "Riverside",       "x": 56, "y": 56},
        ]

        def _marker_color(p: float) -> str:
            return "red" if p >= 90.0 else "yellow" if p >= 70.0 else "green"

        for b in city_bins:
            seed = sum(ord(ch) for ch in b["id"])
            jitter = ((seed % 21) - 10) / 100.0
            p = float(max(0.0, min(1.0, base + jitter)) * 100.0)
            b["fill_pct"] = round(p, 1)
            b["status"] = _marker_color(b["fill_pct"])

        history = []
        for t, c in snapshot_events[-60:][::-1]:
            history.append({
                "ts": float(t),
                "time": dt.datetime.fromtimestamp(float(t)).strftime("%H:%M:%S"),
                "category": c,
            })

        return jsonify({
            "ok": True,
            "counts": snapshot_counts,
            "capacities": snapshot_caps,
            "fill_pct": fill_pct,
            "total": total,
            "distribution_pct": distribution_pct,
            "kpis": {
                "items_per_min": items_per_min,
                "fullest_bin": fullest_bin,
                "fullest_bin_fill_pct": fill_pct.get(fullest_bin, 0.0),
            },
            "alerts": alerts,
            "impact": impact,
            "city": {
                "name": "Smart City District",
                "bins": city_bins,
                "uptime_s": int(time.time() - started_at),
            },
            "latest": {"category": cat, "confidence": round(conf, 3), "ts": ts, "source": source},
            "history": history,
        })

    return app


app = _create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)