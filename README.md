# Roboflow Conference Demo

A self-contained FastAPI mini-app that

* runs a **Roboflow Workflow** in the background
* shows the latest annotated frame in near-real-time on a local web page
* lets booth visitors throttle the refresh rate from a dropdown

---

## 📂 Project layout

```
conference_demo/
├── config.yaml          # all tweakable settings
├── main.py              # FastAPI server + inference thread
├── index.html           # one-page UI
├── roboflow_logo.png    # logo used by the UI
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

| Tool                          | Tested version                  |
| ----------------------------- | ------------------------------- |
| Python                        | 3.9 – 3.11                      |
| pip / venv                    | latest recommended              |
| Roboflow `inference` SDK      | ≥ 0.50                          |
| (optional) GPU drivers / CUDA | only if your workflow uses them |

> **Hardware:** Works on a laptop, Jetson, or any Linux/Windows/Mac box that can access a webcam or RTSP stream.

---

## 🚀 Quick start

```bash
git clone https://github.com/your-org/conference_demo.git
cd conference_demo
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# edit config.yaml (API key, workflow, video source) as needed
python main.py
```

Open **[http://localhost:8000](http://localhost:8000)** (or `http://<device-ip>:8000` on the booth Wi-Fi).
You’ll see the live stream plus a refresh-rate selector.

---

## 🔧 Configuration

All runtime knobs sit in **`config.yaml`**.

```yaml
roboflow:
  api_key:        "<your-key>"
  workspace:      "roboflowreed"
  workflow_id:    "coco"
  video_reference: 0          # 0 = webcam, "rtsp://..." = network camera
  max_fps:        30          # capture rate

server:
  host:           "0.0.0.0"   # expose on all interfaces so visitors can connect
  port:           8000
  refresh_intervals_ms: [33,100,250,500,1000]
  default_interval_ms: 100
```

*Environment variables* are respected if you prefer not to store the API key in plaintext—just set `ROBOFLOW_API_KEY`.

---

## 🖥️ Folder-served assets

The line in **`main.py`**

```python
app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")
```

exposes every file in the project folder at `/static/<filename>`.
`index.html` references the logo via `/static/roboflow_logo.png`; swap in any branding without touching code.

---

## 🆘 Troubleshooting

| Symptom                                                                   | Likely cause / fix                                                                                                                                                      |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| “Failed to open camera”                                                   | `video_reference` incorrect. Use `ls /dev/video*` for USB webcams or test your RTSP URL with VLC.                                                                       |
| Page unreachable from other laptops                                       | Open firewall or bind to `0.0.0.0` (already the default in `config.yaml`).                                                                                              |

---