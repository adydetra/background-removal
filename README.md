# Background Removal 🖼️

Background Removal using Python and OpenCV. Replacing the background with a video

---

## Requirements

**Python** [3.12.7](https://www.python.org/downloads/release/python-3127/)

---

## Getting Started

### Recommended (Batch scripts)

1. **Setup environment** (creates `.venv` and installs dependencies)

```bat
setup.bat
```

2. **Run the app**

```bat
run.bat
```

### Manual steps (alternative)

1. **Create virtual environment**

```bash
uv venv
```

2. **Activate virtual environment**

Powershell

```powershell
.venv\Scripts\Activate.ps1
```

Command Prompt

```sh
\.venv\Scripts\activate.bat
```

Bash or WSL:

```bash
source .venv/Scripts/activate
```

3. **Install dependencies**

```bash
uv pip install -r requirements.txt
```

4. **Run the sample script**

```bash
python index.py
```

---

## Controls

- **`r`** Recapture the background after you change position or lighting (waits 2 seconds before taking the new frame).
- **`q` / `ESC`** Close the application window and stop the script.

---

## Configuration Flow

After launching `python index.py`, follow the interactive prompts:

- **Resolution**: choose from VGA (640x480), HD (1280x720), Full HD (1920x1080), or enter a custom size.
- **Frame Rate**: pick 30fps, 60fps, or specify a custom value.
- **Camera Scan**: the script probes available camera indices (0-4 by default) and shows detected resolutions/FPS.
- **Camera Selection**: choose the index that matches the device you want to use.

Once configured, the script initializes the chosen camera with your requested settings.

---

## Usage Tips

- **Use a static background** during auto capture to improve foreground detection accuracy.
- **Keep lighting consistent** to reduce noise when comparing against the reference frame.
- **Make sure `video.mp4`** stays in the same folder as `index.py`, or update the path in code if you want a different background.
- **Scanner shows detected resolutions/FPS.** Some virtual cameras (e.g., NVIDIA Broadcast) may report 0fps or a fixed resolution; pick the index that corresponds to your physical webcam if you need live input.
- **Requested settings may differ from actual.** After selection, the script prints the active resolution/FPS as reported by the camera driver. Adjust choices or try another camera if needed.
