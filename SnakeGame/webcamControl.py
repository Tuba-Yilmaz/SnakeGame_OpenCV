'''PyAutoGUI, Python ile diğer uygulamaların
 pencerelerinde fare ve klavyeyi kontrol etmenize
 ve etkileşimde bulunmanıza olanak sağlayan bir modüldür'''
import cv2
import imutils
import numpy as np
from collections import deque
import time
import pyautogui
from threading import Thread
import pynput

#Framelerin okunması için ayrı iş parçacığı uygulayan sınıf.
from pynput.keyboard import Key


class WebcamVideoStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(0)
        self.ret, self.frame = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target = self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            self.ret, self.frame = self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True

#yeşil renk için hsv aralığı
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

#tampon noktaları
buffer = 20

#pyautogui'nin her karede ekranın ortasını tıklamaması için kullanılır
flag = 0

#Nesne koordinatlarının 'tampon' numarasını depolayan puanlar deque yapısı
pts = deque(maxlen = buffer)
#Minimum sayıyı sayar. Yön değişikliğinin meydana geldiği tespit edilecek kare sayısı
counter = 0
#Yön değişikliği dX, dY'de saklanır
(dX, dY) = (0, 0)
#Yönü tuttuğumuz değişken
direction = ''
#Pyautogui tarafından hangi tuşa basıldığını algılamak için son basılan değişken
last_pressed = ''

#Kameranın düzgün bir şekilde başlamasına izin vermek için 3 saniye uyuyun.
time.sleep(3)

#Ekranın genişliğini ve yüksekliğini algılamak için pyautogui işlevini kullanın
width,height = pyautogui.size()

#Ana iş parçacığından ayrı bir iş parçacığında video yakalamaya başlayın
vs = WebcamVideoStream().start()
#video_shower = VideoShow(vs.read()).start()

#Ekranın ortasına tıklayın, oyun penceresi buraya yerleştirilmelidir.
pyautogui.click(int(width/2), int(height/2))

while True:

    #Okunan frame'i frame'de sakla
    frame = vs.read()
    #yansitmayı kapadık
    frame = cv2.flip(frame,1)
    #verilen pencereyi 600x600yap
    frame = imutils.resize(frame, width = 600)
    #Aşırı paraziti gidermek için çekirdek boyutu 11 olan Gauss Filtresini kullanarak çerçeveyi bulanıklaştırın
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    #HSV daha iyi segmentasyona izin verdiği için çerçeveyi HSV'ye dönüştürün.
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    #Çerçeve için yeşil değerleri gösteren bir maske oluşturun
    mask = cv2.inRange(hsv_converted_frame, greenLower, greenUpper)
    #Maskelenmiş görüntüde bulunan küçük beyaz noktaları silmek için maskelenmiş çıktıyı aşındırın
    mask = cv2.erode(mask, None, iterations = 2)
    #Hedefimizi geri yüklemek için ortaya çıkan görüntüyü genişletin
    mask = cv2.dilate(mask, None, iterations = 2)#2kez genişletti

    #Maskelenmiş görüntüdeki tüm konturları bulun
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    #Define center of the ball to be detected as None
    center = None

    #Herhangi bir nesne algılanırsa, yalnızca devam edin
    if(len(cnts) > 0):
        #Maksimum alana sahip konturu bulun
        c = max(cnts, key = cv2.contourArea)
        #Çemberin merkezini ve algılanan en büyük konturun yarıçapını bulun.
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #Etrafına bir daire çizmemiz gerektiğinden topun ağırlık merkezini hesaplayın.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Yalnızca hatırı sayılır boyutta bir top algılanırsa devam edin
        if radius > 10:
            #Nesnenin etrafına ve merkezine daireler çizin
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            #Çerçevedeki algılanan nesneyi pts deque yapısına ekleyin
            pts.appendleft(center)

    #Daha iyi performans için numpy arange işlevini kullanma. Tespit edilen tüm noktalara kadar döngü
    for i in np.arange(1, len(pts)):
        #Hiçbir nokta algılanmazsa, devam edin.
        if(pts[i-1] == None or pts[i] == None):
            continue

        #En az 10 karede yön değişikliği varsa devam edin
        if counter >= 10 and i == 1 and len(pts) > 10 and pts[-10] is not None:
            #Geçerli kare ile önceki 10. kare arasındaki mesafeyi hesaplayın.
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ('', '')

            #Mesafe 50 pikselden büyükse, önemli bir yön değişikliği meydana gelmiştir.
            if np.abs(dX) > 50:
                dirX = 'West' if np.sign(dX) == 1 else 'East'

            if np.abs(dY) > 50:
                dirY = 'North' if np.sign(dY) == 1 else 'South'

            #Yön değişkenini algılanan yöne ayarla
            direction = dirX if dirX != '' else dirY
            #Algılanan yönü çerçeveye yqazın.
            #cv2.putText(frame, direction, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        #Nesnenin hareketini göstermek için sondaki kırmızı bir çizgi çizin.
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    #Algılanan yön Doğu ise sağ tuşa basın
    if direction == 'East':
        if last_pressed != 'right':
            pyautogui.press('right')#sağ tuşa basar
            last_pressed = 'right'
            print("Right Pressed")
    #Algılanan yön Batı ise, Sol tuşa basın
    elif direction == 'West':
        if last_pressed != 'left':
            pyautogui.press('left')#sol tuşa basar
            last_pressed = 'left'
            print("Left Pressed")
    #algılanan yön Kuzey ise, Yukarı tuşuna basın
    elif direction == 'North':
        if last_pressed != 'up':
            pyautogui.press('up')  # yukarı tuşuna basar
            last_pressed = 'up'
            print("Up Pressed")
    #Algılanan yön Güney ise, aşağı tuşuna basın
    elif direction == 'South':
        if last_pressed != 'down':
            pyautogui.press('down')#aşağı tuşuna basar
            last_pressed = 'down'
            print("Down Pressed")


    cv2.imshow('Oyun Kontrol Penceresi', frame)
    key = cv2.waitKey(1) & 0xFF
    #Yön değişikliği algılandığında sayacı güncelleyin.
    counter += 1

    #Pyautogui merkeze tıklamadıysa, oyun penceresine odaklanmak için bir kez tıklayın.
    if (flag == 0):
        pyautogui.click(int(width/2), int(height/2))
        flag = 1

    #q tuşuna bawsınca pencereyi kapat
    if(key == ord('q')):
        break
#Tüm işlemlerden sonra web kamerasını serbest bırakın ve tüm pencereleri yok edin
vs.stop()
cv2.destroyAllWindows()
