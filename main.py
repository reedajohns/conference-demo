#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roboflow Conference Demo App
============================
Runs an InferencePipeline in a background thread and exposes the most-recent
annotated frame at `/latest.jpg`. A simple FastAPI front-end displays that
image and lets visitors change the refresh rate on the fly.

Run with:
    $ python main.py       # or: uvicorn main:app --reload

Dependencies: see requirements.txt
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional
from fastapi.staticfiles import StaticFiles

import cv2
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Response
from inference import InferencePipeline

CONFIG = yaml.safe_load(Path(__file__).with_name("config.yaml").read_text())

# -----------------------------------------------------------------------------
# Shared state between inference callback and web handlers
# -----------------------------------------------------------------------------
_latest_frame: Optional[bytes] = None
_lock = threading.Lock()


def _on_prediction(result: dict, _: "InferencePipeline.VideoFrame") -> None:
    """Sink callback that encodes the workflow `output_image` as JPEG.

    Args:
        result: Prediction dictionary returned by the workflow.
        _:      Raw video frame (unused here).
    """
    global _latest_frame  # pylint: disable=global-statement
    if not result.get("output_image"):
        return

    # Convert to bytes once, keep in memory.
    img = result["output_image"].numpy_image  # BGR order
    success, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if success:
        with _lock:
            _latest_frame = buf.tobytes()


def _start_pipeline() -> None:
    """Starts the Roboflow InferencePipeline and blocks until it exits."""
    p = InferencePipeline.init_with_workflow(
        api_key=CONFIG["roboflow"]["api_key"],
        workspace_name=CONFIG["roboflow"]["workspace"],
        workflow_id=CONFIG["roboflow"]["workflow_id"],
        video_reference=CONFIG["roboflow"]["video_reference"],
        max_fps=CONFIG["roboflow"]["max_fps"],
        on_prediction=_on_prediction,
    )
    p.start()
    p.join()


# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(title="Roboflow Live Inference Demo")

# NEW → expose everything in the current folder under /static
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent),
    name="static",
)


@app.get("/latest.jpg", summary="Latest annotated frame", include_in_schema=False)
async def latest_jpg() -> Response:
    """Return the most-recent JPEG frame."""
    with _lock:
        if _latest_frame is None:
            raise HTTPException(status_code=404, detail="No frame yet")
        return Response(content=_latest_frame, media_type="image/jpeg")  # :contentReference[oaicite:0]{index=0}


@app.get("/", include_in_schema=False)
async def root() -> Response:
    """Serve the main HTML UI."""
    html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return Response(content=html, media_type="text/html")


if __name__ == "__main__":
    threading.Thread(target=_start_pipeline, daemon=True).start()

    import uvicorn
    uvicorn.run(            # ← give the object, not the import string
        app,
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        log_level="info",
    )


