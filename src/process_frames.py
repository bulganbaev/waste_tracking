import os
import cv2
import sys
from ultralytics import YOLO

# Папка с изображениями камер
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '../images')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/best.pt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def list_cameras():
    print("Available cameras:")
    cameras = sorted([d for d in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, d))])
    for idx, cam in enumerate(cameras):
        print(f"[{idx}] {cam}")
    return cameras

def select_camera(cameras):
    try:
        idx = int(input("Select camera by number: "))
        return cameras[idx]
    except (IndexError, ValueError):
        print("Invalid selection.")
        sys.exit(1)

def process_frames(camera_serial):
    camera_dir = os.path.join(IMAGES_DIR, camera_serial)
    frame_paths = sorted([
        os.path.join(camera_dir, f) for f in os.listdir(camera_dir)
        if f.lower().endswith('.jpg')
    ])

    if not frame_paths:
        print("No images found in selected camera folder.")
        return

    # Загрузка модели
    model = YOLO(MODEL_PATH)
    print(f"Loaded model from {MODEL_PATH}")

    # Получаем разрешение первого кадра
    sample_img = cv2.imread(frame_paths[0])
    height, width = sample_img.shape[:2]

    # Инициализация видео
    output_path = os.path.join(OUTPUT_DIR, f"{camera_serial}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 10  # можно изменить
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Processing {len(frame_paths)} frames...")

    for i, frame_path in enumerate(frame_paths):
        frame = cv2.imread(frame_path)
        results = model.predict(frame, verbose=False)

        # Наносим предсказания на изображение
        annotated = results[0].plot()
        out.write(annotated)

        if i % 10 == 0 or i == len(frame_paths) - 1:
            print(f"Processed {i+1}/{len(frame_paths)} frames")

    out.release()
    print(f"✅ Saved result to: {output_path}")

if __name__ == "__main__":
    cameras = list_cameras()
    selected_camera = select_camera(cameras)
    process_frames(selected_camera)