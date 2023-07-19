import sys
import cv2
import gxipy as gx
import numpy as np
from pyzbar import pyzbar

# open device
device_manager = gx.DeviceManager()
# device explore
dev_num, dev_info_list = device_manager.update_device_list()
if dev_num == 0:
    sys.exit(1)

strIndex = dev_info_list[0].get("index")
cam = device_manager.open_device_by_index(strIndex)

cam.ExposureAuto.set(0)
cam.BalanceWhiteAuto.set(0)
cam.BalanceRatioSelector.set(0)
cam.BalanceRatio.set(1.7)
cam.BalanceRatioSelector.set(1)
cam.BalanceRatio.set(1.1)
cam.BalanceRatioSelector.set(2)
cam.BalanceRatio.set(3)
cam.Gain.set(24)
cam.ExposureTime.set(10000)

cam.stream_on()

video_size = cv2.VideoWriter_fourcc(*'MP4V')

# size = (cam.Width.get(), cam.Height.get())

# file_path = 'videvo'+time.strftime("%Y%m%d_%H%M%S", time.localtime())+'.avi'
# video_save = cv2.VideoWriter(file_path, video_size, fps, size)


while 1: # video_save.isOpened():

    # ==================================СЧИТЫВАНИЕ ИЗОБРАЖЕНИЯ=====================================================

    image = cam.data_stream[0].get_image()  # Сделать снимок с помощью камеры
    image = image.convert("RGB")  # Получить изображение RGB из цветного необработанного изображения
    numpy_image = image.get_numpy_array()  # Создать массив numpy из данных изображения RGB
    if numpy_image is None:
        continue
    numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR) # Opencv использует изображения BGR и преобразует RGB в BGR.

    # ==================================СЧИТЫВАНИЕ ШТРИХ-КОДА=====================================================

    barcodes = pyzbar.decode(numpy_image)

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(numpy_image, (x, y), (x + w, y + h), (255, 255, 255), 2)
        bdata = barcode.data.decode("utf-8")
        btype = barcode.type
        text = f"{bdata},{btype}"
        cv2.putText(numpy_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # ==================================СЧИТЫВАНИЕ ЦВЕТА=====================================================

    lower_blue = np.array([100, 150, 20])
    lower_green = np.array([40, 50, 20])
    lower_pink = np.array([150, 50, 20])
    lower_orange = np.array([5, 150, 20])

    upper_blue = np.array([140, 255, 255])
    upper_green = np.array([70, 255, 255])
    upper_pink = np.array([180, 255, 255])
    upper_orange = np.array([20, 255, 255])

    color_image = cv2.cvtColor(numpy_image, cv2.COLOR_BGR2HSV)
    mask_blue = cv2.inRange(color_image, lower_blue, upper_blue)
    mask_green = cv2.inRange(color_image, lower_green, upper_green)
    mask_pink = cv2.inRange(color_image, lower_pink, upper_pink)
    mask_orange = cv2.inRange(color_image, lower_orange, upper_orange)

    conts_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts_pink, _ = cv2.findContours(mask_pink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts_orange, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    area = [0, 0, 0, 0]  # B G P O

    if len(conts_blue) != 0:
        for cont_blue in conts_blue:
            if cv2.contourArea(cont_blue) > 500:
                area[0] = area[0] + cv2.contourArea(cont_blue)
                x, y, w, h = cv2.boundingRect(cont_blue)
                cv2.rectangle(numpy_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    if len(conts_green) != 0:
        for cont_green in conts_green:
            if cv2.contourArea(cont_green) > 500:
                area[1] = area[1] + cv2.contourArea(cont_green)
                x, y, w, h = cv2.boundingRect(cont_green)
                cv2.rectangle(numpy_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if len(conts_pink) != 0:
        for cont_pink in conts_pink:
            if cv2.contourArea(cont_pink) > 500:
                area[2] = area[2] + cv2.contourArea(cont_pink)
                x, y, w, h = cv2.boundingRect(cont_pink)
                cv2.rectangle(numpy_image, (x, y), (x + w, y + h), (147, 20, 255), 2)
    if len(conts_orange) != 0:
        for cont_orange in conts_orange:
            if cv2.contourArea(cont_orange) > 500:
                area[3] = area[3] + cv2.contourArea(cont_orange)
                x, y, w, h = cv2.boundingRect(cont_orange)
                cv2.rectangle(numpy_image, (x, y), (x + w, y + h), (0, 165, 255), 2)

    max_value = max(area)
    if area.index(max_value) == 0:
        print('BLUE!')
    if area.index(max_value) == 1:
        print('GREEN!')
    if area.index(max_value) == 2:
        print('PINK!')
    if area.index(max_value) == 3:
        print('ORANGE!')

    #==================================ВЫВОД/СОХРАНЕНИЕ=====================================================

    cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # Размер окна регулируется
    cv2.imshow('video', numpy_image)
    # video_save.write(numpy_image)  # Сохраните захваченное изображение в формате numpy_image.

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.stream_off()
cam.close_device()

