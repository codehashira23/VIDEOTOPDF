import os
import re
import shutil
import pathlib
import subprocess
import sys
from PIL import Image
from pypdf import PdfWriter, PdfReader
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging

# ----------------------------
# UTF-8 PRINT FIX
# ----------------------------
sys.stdout.reconfigure(encoding="utf-8")


def safe_print(*args):
    text = " ".join(str(a) for a in args)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode())


# ----------------------------
# FOLDER SETUP
# ----------------------------
BASE_DIR = pathlib.Path(".")
VIDEO_DIR = BASE_DIR / "video"
OUTPUT_DIR = BASE_DIR / "pdf"

# enable GPU acceleration for ffmpeg (set to True/False)
USE_GPU = False


# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(filename="run.log", level=logging.INFO)


# ----------------------------
# SUPPORTIVE FUNCTIONS
# ----------------------------
def extract_number(name):
    """Extract leading number from filename. Example: '012 Lecture.mp4' → 12"""
    m = re.match(r"(\d+)", name)
    if m:
        return int(m.group(1))
    return 999999999  # send to bottom if no number


def ffmpeg_exists():
    return shutil.which("ffmpeg") is not None


# ----------------------------
# FRAME EXTRACTION
# ----------------------------
def extract_frames(video_path, output_subfolder):
    output_subfolder.mkdir(parents=True, exist_ok=True)

    if any(output_subfolder.glob("frame_*.jpg")):
        safe_print("Frames already exist for:", video_path.name)
        return True

    safe_print("Extracting frames for:", video_path.name)

    output_pattern = str(output_subfolder / "frame_%04d.jpg")

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", "fps=0.02",
    ]

    if USE_GPU:
        cmd.insert(1, "-hwaccel")
        cmd.insert(2, "cuda")

    cmd.append(output_pattern)

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    safe_print("Frame extraction complete for:", video_path.name)
    return True


# ----------------------------
# IMAGES → PDF
# ----------------------------
def images_to_pdf(image_folder, pdf_path):
    if pdf_path.exists():
        safe_print("PDF exists → skipping:", pdf_path.name)
        return True

    images = sorted(image_folder.glob("*.jpg"))
    if not images:
        safe_print("NO frames found for:", image_folder)
        return False

    safe_print("Creating PDF:", pdf_path.name)

    first = Image.open(images[0]).convert("RGB")
    others = [Image.open(p).convert("RGB") for p in images[1:]]

    first.save(pdf_path, save_all=True, append_images=others)

    first.close()
    for img in others:
        img.close()

    safe_print("PDF created:", pdf_path.name)
    return True


# ----------------------------
# DELETE FRAMES (SAVE SPACE)
# ----------------------------
def delete_frames(folder):
    for f in folder.glob("*.jpg"):
        f.unlink()
    try:
        folder.rmdir()
    except:
        pass


# ----------------------------
# PROCESS ONE VIDEO
# ----------------------------
def process_video(video_path):
    try:
        safe_print("\nProcessing:", video_path.name)

        number = str(extract_number(video_path.name)).zfill(3)
        img_dir = OUTPUT_DIR / number
        pdf_path = OUTPUT_DIR / f"{number}.pdf"

        extract_frames(video_path, img_dir)
        images_to_pdf(img_dir, pdf_path)

        # save space
        delete_frames(img_dir)

        return True

    except Exception as e:
        safe_print("ERROR processing", video_path.name, "→", e)
        logging.error(str(e))
        return False


# ----------------------------
# MERGE ALL PDFs
# ----------------------------
def merge_all_pdfs():
    merged = OUTPUT_DIR / "final_merged.pdf"
    if merged.exists():
        safe_print("Merged PDF already exists — skipping merge.")
        return

    pdfs = sorted(
        OUTPUT_DIR.glob("*.pdf"),
        key=lambda f: extract_number(f.stem)
    )

    writer = PdfWriter()

    safe_print("\nMerging PDFs...")

    for p in pdfs:
        safe_print("Adding:", p.name)
        reader = PdfReader(str(p))
        writer.append(reader)

    with open(merged, "wb") as f:
        writer.write(f)

    safe_print("Final merged PDF created:", merged)


# ----------------------------
# MAIN
# ----------------------------
def main():

    if not ffmpeg_exists():
        safe_print("ERROR: ffmpeg not installed.")
        return

    if not VIDEO_DIR.exists():
        safe_print("ERROR: 'video' folder missing.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    videos = sorted(
        list(VIDEO_DIR.glob("*.mp4")) +
        list(VIDEO_DIR.glob("*.webm")) +
        list(VIDEO_DIR.glob("*.mkv")),
        key=lambda f: extract_number(f.name)
    )

    if not videos:
        safe_print("No video files found in /video/")
        return

    safe_print("\nStarting multi-threaded processing...\n")

    # -------------- MULTITHREADING ----------
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(tqdm(ex.map(process_video, videos), total=len(videos)))

    merge_all_pdfs()

    safe_print("\nALL DONE.")


if __name__ == "__main__":
    main()
