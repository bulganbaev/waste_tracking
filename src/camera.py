import time
import gxipy as gx
import cv2
import numpy as np
from datetime import datetime


class Camera:
    def __init__(self, settings: dict):
        self.device_manager = gx.DeviceManager()
        self.cam_sn = settings['serial']
        self.settings_dict = settings
        self.cam = None

    def check_camera_numbers(self):
        dev_num, _ = self.device_manager.update_device_list()
        if dev_num == 0:
            raise Exception("Камеры не найдены.")
        print(f"[INFO] Найдено камер: {dev_num}")

    def camera_settings(self):
        self.cam = self.device_manager.open_device_by_sn(self.cam_sn)

        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.cam.Width.set(self.cam.Width.get_range()['max'])
        self.cam.Height.set(self.cam.Height.get_range()['max'])
        self.cam.OffsetX.set(0)
        self.cam.OffsetY.set(0)

        if self.cam.GammaMode.is_writable():
            self.cam.GammaMode.set(gx.GxGammaModeEntry.USER)
        if self.cam.Gamma.is_writable():
            self.cam.Gamma.set(0.5)

        exposure_time = max(10.0, min(float(self.settings_dict.get('exposure_time', 10000.0)), 50000.0))
        gain = max(0.0, min(float(self.settings_dict.get('gain', 0.0)), 24.0))
        self.cam.ExposureTime.set(exposure_time)
        self.cam.Gain.set(gain)

        try:
            self.cam.PixelFormat.set(gx.GxPixelFormatEntry.BAYER_RG8)
            print("[INFO] BayerRG8 установлен.")
        except Exception:
            self.cam.PixelFormat.set(gx.GxPixelFormatEntry.BAYER_RG10)
            print("[INFO] BayerRG10 установлен (резерв).")

        if self.cam.AcquisitionFrameRate.is_writable():
            self.cam.AcquisitionFrameRate.set(30)

        print("[INFO] Настройки камеры применены.")

    def start_camera(self):
        if not self.cam:
            raise Exception("Камера не инициализирована.")
        self.cam.stream_on()
        time.sleep(0.5)

    def stop_camera(self):
        if self.cam:
            try:
                self.cam.stream_off()
            except Exception as e:
                print(f"[WARN] stream_off: {e}")
            try:
                self.cam.close_device()
            except Exception as e:
                print(f"[WARN] close_device: {e}")
            self.cam = None

    def get_frame(self):
        try:
            raw_image = self.cam.data_stream[0].get_image(timeout=3000)
            if raw_image is None or raw_image.get_status() != 0:
                return None

            numpy_image = raw_image.get_numpy_array()
            if numpy_image is None:
                return None

            if numpy_image.dtype != np.uint8:
                numpy_image = (numpy_image / 256).astype(np.uint8)

            rgb_image = cv2.cvtColor(numpy_image, cv2.COLOR_BAYER_RG2RGB)
            return rgb_image

        except Exception as e:
            print(f"[ERROR] Ошибка получения кадра: {e}")
            return None

    def __del__(self):
        self.stop_camera()


def stream_camera(camera: Camera, save=False):
    try:
        camera.check_camera_numbers()
        camera.camera_settings()
        camera.start_camera()

        print("[INFO] Трансляция запущена. Нажмите 'q' для выхода.")
        last_time = time.time()
        frame_count = 0

        video_writer = None

        while True:
            frame = camera.get_frame()
            if frame is None:
                print("[WARN] Повреждённый кадр, пропускаем...")
                continue

            if save and video_writer is None:
                h, w = frame.shape[:2]
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output_{now_str}.avi"
                video_writer = cv2.VideoWriter(
                    filename,
                    cv2.VideoWriter_fourcc(*'XVID'),
                    15.0,
                    (w, h)
                )
                print(f"[INFO] Запись видео: {filename}")

            frame_count += 1
            now = time.time()
            if now - last_time >= 1.0:
                print(f"[INFO] FPS: {frame_count}")
                frame_count = 0
                last_time = now

            scale_percent = 20
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            cv2.imshow("Camera Stream", resized_frame)

            if save and video_writer:
                video_writer.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"[ERROR] Ошибка запуска: {e}")

    finally:
        if save and video_writer:
            video_writer.release()
            print("[INFO] Видеофайл сохранён.")
        camera.stop_camera()
        cv2.destroyAllWindows()
        print("[INFO] Трансляция остановлена.")


if __name__ == "__main__":
    settings = {
        'serial': 'CCA24130001',
        'exposure_time': 20000.0,
        'gain': 5.0
    }

    camera = Camera(settings)
    stream_camera(camera, save=True)  # True — сохранить .avi с цветом
