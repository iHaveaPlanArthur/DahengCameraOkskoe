import sys
import cv2
import gxipy as gx
import time

# open device
device_manager = gx.DeviceManager()
# device explore
dev_num, dev_info_list = device_manager.update_device_list()
if dev_num == 0:
    sys.exit(1)

strIndex = dev_info_list[0].get("index")
cam = device_manager.open_device_by_index(strIndex)

cam.stream_on()

video_size = cv2.VideoWriter_fourcc(*'XVID')

cam.ExposureTime.set(50000.0)

fps = cam.AcquisitionFrameRate.get()
expos = cam.ExposureTime.get()
print("framerate: ")
print(fps)
print("\n")
print("exposure time: ")
print(expos)
print("\n")

size = (cam.Width.get(), cam.Height.get())
print("the size of video is : %d X %d " % (cam.Width.get(), cam.Height.get()))

file_path = 'videvo'+time.strftime("%Y%m%d_%H%M%S", time.localtime())+'.avi'
video_save = cv2.VideoWriter(file_path, video_size, fps, size)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while video_save.isOpened():
    raw_image = cam.data_stream[0].get_image()  # Сделать снимок с помощью камеры
    if raw_image is None:
        print("Getting image failed.")
        continue
    rgb_image = raw_image.convert("RGB")  # Получить изображение RGB из цветного необработанного изображения
    if rgb_image is None:
        continue
    numpy_image = rgb_image.get_numpy_array()  # Создать массив numpy из данных изображения RGB
    if numpy_image is None:
        continue

    numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)  # Opencv использует изображения BGR и преобразует RGB в BGR.
    
    faces = face_cascade.detectMultiScale(numpy_image, scaleFactor=1.5, minNeighbors=5, minSize=(20,20))
    
    for(x,y,w,h) in faces:
        cv2.rectangle(numpy_image,(x,y), (x+w, y+h), (255,0,0), 2)

    cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # Размер окна регулируется
    cv2.imshow('video', numpy_image)
    video_save.write(numpy_image)  # Сохраните захваченное изображение в формате numpy_image.

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.stream_off()
cam.close_device()


