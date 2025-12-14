# Video-to-Notes Automation Pipeline

## Key Features

### 1. Multi-Threaded Video Processing

Processes multiple videos simultaneously using `ThreadPoolExecutor`, cutting down total runtime significantly.

### 2. Automatic Frame Extraction

- Powered by `ffmpeg`
- Supports MP4, WEBM, MKV
- Extracts frames at a configurable rate (`fps=0.02`)
- Optional GPU acceleration (CUDA)
- If frames already exist, extraction is skipped → perfect for resumable runs

### 3. Image-to-PDF Conversion

Converts extracted frames into clean PDFs:

- Preserves correct order
- Ensures RGB-safe images via Pillow (PIL)
- Skips already-created PDFs to avoid redundant work

### 4. Intelligent Cleanup

After each PDF is generated, all temporary image frames are deleted to keep storage usage minimal.

### 5. Correct Numerical Ordering

Files are sorted by the numeric prefix in their filenames:

001 Intro.mp4 → 001.pdf
002 TopicA.mp4 → 002.pdf


Ensures perfectly sequenced final output.

### 6. Final PDF Merger

All generated PDFs are merged into:

final_merged.pdf


using `pypdf` for stable handling of large documents.

### 7. Error Logging and Safe Unicode Output

- Logs all errors and events to `run.log`
- Uses safe printing to avoid Unicode issues on Windows terminals

---

## Project Structure
```
.
├── video/ - Input videos
├── pdf/ - Generated PDFs + final merged PDF
├── run.log - Execution logs
└── main.py - Main automation script
```

---

## Technologies Used

- Python 3
- ffmpeg
- Pillow (PIL)
- pypdf
- tqdm
- ThreadPoolExecutor
- logging

---

## How the Pipeline Works

1. Scan the `video/` folder for supported video files
2. Sort videos by leading numeric prefix
3. For each video (processed in parallel):
   - Extract frames
   - Create PDF
   - Delete temporary frames
4. Merge all PDFs into a final consolidated document
5. Output execution summary and logs

---

## Setup & Usage

### 1. Install Python Dependencies

```
pip install pillow pypdf tqdm
2. Install ffmpeg
Ensure ffmpeg is installed and available in your system PATH.

3. Add Videos
Place .mp4, .webm, or .mkv files inside the video/ directory.

4. Run the Script
python main.py
Example Use Cases
Creating printable notes from lecture videos

Archiving tutorial series into document form

Preprocessing data for OCR or ML pipelines

Preparing structured study material

Compressing training content into shareable PDFs

Potential Enhancements
OCR-based text extraction from frames

Automatic FPS adaptation based on motion detection

Web or desktop GUI

Cloud import/export (Google Drive, S3)

Async ffmpeg execution

Duplicate-frame detection to reduce PDF size
```
## Highlights
- Fully automated end-to-end workflow
- Resumable and safe for reruns
- Memory-efficient with automatic cleanup
- Parallelized for speed
- Predictable, numerically sorted output
