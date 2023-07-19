import sys
import keyboard
import cv2
import gxipy as gx
import numpy as np
# from pyzbar import pyzbar


def exit_program():
    print("\nExiting the programm...\n")
    cv2.destroyAllWindows()
    cam.close_device()
    sys.exit(0)


def error_exit():
    print("\nEncouter some error! Exiting...\n")
    sys.exit(1)


device_manager = gx.DeviceManager()
dev_num, dev_info_list = device_manager.update_device_list()
if dev_num == 0:
    error_exit()

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

while True:

    # ==================================СЧИТЫВАНИЕ ИЗОБРАЖЕНИЙ=====================================================
    print("Press CTRL to launch recording;")
    print("Press ESC to exit the programm\n")
    while True:
        if keyboard.is_pressed('ctrl'):
            print("\nRecording...\n")
            break
        elif keyboard.is_pressed('escape'):
            exit_program()
    cam.stream_on()
    images = []
    for i in range(56):
        raw_image = cam.data_stream[0].get_image()  # Снимок с помощью камеры
        raw_image = raw_image.convert("RGB")  # Изображение RGB из цветного необработанного изображения
        raw_image = raw_image.get_numpy_array()  # Массив numpy из данных изображения RGB
        if raw_image is None:
            continue
        images.append(cv2.cvtColor(raw_image, cv2.COLOR_RGB2BGR))  # Opencv использует BGR
    cam.stream_off()
    # print(images)
    # print(len(images))

    # ========================================ОБРАБОТКА===========================================================
    for image in images:

        lower_blue = np.array([100, 150, 20])
        lower_green = np.array([40, 100, 20])
        lower_pink = np.array([150, 50, 20])
        lower_orange = np.array([5, 150, 20])

        upper_blue = np.array([140, 255, 255])
        upper_green = np.array([80, 255, 255])
        upper_pink = np.array([180, 255, 255])
        upper_orange = np.array([20, 255, 255])

        color_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
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
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        if len(conts_green) != 0:
            for cont_green in conts_green:
                if cv2.contourArea(cont_green) > 500:
                    area[1] = area[1] + cv2.contourArea(cont_green)
                    x, y, w, h = cv2.boundingRect(cont_green)
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if len(conts_pink) != 0:
            for cont_pink in conts_pink:
                if cv2.contourArea(cont_pink) > 500:
                    area[2] = area[2] + cv2.contourArea(cont_pink)
                    x, y, w, h = cv2.boundingRect(cont_pink)
                    cv2.rectangle(image, (x, y), (x + w, y + h), (147, 20, 255), 2)
        if len(conts_orange) != 0:
            for cont_orange in conts_orange:
                if cv2.contourArea(cont_orange) > 500:
                    area[3] = area[3] + cv2.contourArea(cont_orange)
                    x, y, w, h = cv2.boundingRect(cont_orange)
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 165, 255), 2)
        max_value = max(area)
        max_index = area.index(max_value)
        print(area)
        if max_index == 0 and area != [0, 0, 0, 0]:
            print('BLUE!')
        elif max_index == 1 and area != [0, 0, 0, 0]:
            print('GREEN!')
        elif max_index == 2 and area != [0, 0, 0, 0]:
            print('PINK!')
        elif max_index == 3 and area != [0, 0, 0, 0]:
            print('ORANGE!')
        else:
            print('NONE!')
    # ==================================ВЫВОД/СОХРАНЕНИЕ=====================================================

    for image in images:
        cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # Размер окна регулируется
        cv2.imshow('video', image)
        cv2.waitKey(18)