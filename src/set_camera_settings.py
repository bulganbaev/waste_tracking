import gxipy as gx

def set_camera_settings(serial, settings):
    """
    Функция для настройки камеры по серийному номеру.

    :param serial: Серийный номер камеры.
    :param settings: Словарь с параметрами настройки.
        Должен включать ключи: 'exposure_time', 'gain'.
    """
    # Создаем менеджер устройств
    device_manager = gx.DeviceManager()

    # Обновляем список устройств
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        raise Exception("Камеры не найдены.")
    print(f"Найдено {dev_num} камера(ы).")

    # Открываем камеру по серийному номеру
    cam = device_manager.open_device_by_sn(serial)

    # Отключаем триггерный режим
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

    # Устанавливаем разрешение
    width_range = cam.Width.get_range()
    height_range = cam.Height.get_range()
    cam.Width.set(width_range['max'])
    cam.Height.set(height_range['max'])
    cam.OffsetX.set(0)
    cam.OffsetY.set(0)
    print(f"Установлено разрешение: {cam.Width.get()}x{cam.Height.get()}.")

    # Настройка гаммы
    if cam.GammaMode.is_writable():
        cam.GammaMode.set(1)
    else:
        print("GammaMode недоступен для записи.")

    if cam.Gamma.is_writable():
        cam.Gamma.set(0.5)
    else:
        print("Gamma недоступна для записи.")

    # Настройка баланса белого
    if hasattr(cam, 'BalanceWhiteAuto') and cam.BalanceWhiteAuto.is_writable():
        cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
        print("Баланс белого установлен в автоматический режим.")
    else:
        print("Баланс белого недоступен или не поддерживается.")

    # Настройка экспозиции и усиления
    exposure_time = max(10.0, min(float(settings['exposure_time']), 50000.0))
    gain = max(0.0, min(float(settings['gain']), 24.0))
    cam.ExposureTime.set(exposure_time)
    cam.Gain.set(gain)
    print(f"Экспозиция: {exposure_time}, Усиление: {gain}.")

    # Устанавливаем формат пикселей
    try:
        cam.PixelFormat.set(gx.GxPixelFormatEntry.BAYER_RG8)
        print("Формат пикселей установлен на BayerRG8.")
    except Exception as e:
        print(f"Ошибка при установке формата пикселей: {e}")

    # Настройка частоты кадров
    if cam.AcquisitionFrameRate.is_writable():
        cam.AcquisitionFrameRate.set(5.0)  # Устанавливаем частоту кадров
        print("Частота кадров установлена на 15 FPS.")
    else:
        print("AcquisitionFrameRate недоступен для записи.")

    print("Настройки камеры успешно применены.")

    # Закрываем камеру
    cam.close_device()
    print("Камера закрыта.")


if __name__ == "__main__":
    # Настройки камеры
    settings = {
        'serial': 'CCA23050008',  # Серийный номер вашей камеры
        'exposure_time': 10000.0,  # Экспозиция в микросекундах
        'gain': 5.0,  # Усиление
    }

    try:
        set_camera_settings(settings['serial'], settings)
    except Exception as e:
        print(f"Ошибка: {e}")

