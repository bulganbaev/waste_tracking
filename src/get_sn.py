import gxipy as gx

def list_cameras():
    # Создаем менеджер устройств
    device_manager = gx.DeviceManager()

    # Обновляем список устройств
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        print("No cameras found. Please connect a camera.")
        return

    # Выводим информацию о камерах
    print(f"Number of cameras detected: {dev_num}")
    for i, dev_info in enumerate(dev_info_list):
        print(f"Camera {i + 1}:")
        print(f"  Model Name: {dev_info.get('model_name', 'Unknown')}")
        print(f"  Serial Number: {dev_info.get('sn', 'Unknown')}")
        print(f"  Vendor Name: {dev_info.get('vendor_name', 'Unknown')}")
        print(f"  Device Version: {dev_info.get('device_version', 'Unknown')}")
        print("")

if __name__ == "__main__":
    list_cameras()


