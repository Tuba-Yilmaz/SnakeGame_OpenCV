#gerekli kütüphaneleri ekledik
import numpy as np
import cv2
import sys
import random
import time
import keyboard
import pygame
from pygame.locals import *


#KURAL= elma yersen skor artar
def elma_yemek(elma_konum, score):
    elma_konum = [random.randrange(1,50)*10,random.randrange(1,50)*10]
    score += 1
    return elma_konum, score
#KURAL:Sınıra çarpma
def sinirlara_carpma(yilan_kafasi):
    if yilan_kafasi[0]>=500 or yilan_kafasi[0]<=0 or yilan_kafasi[1]>=500 or yilan_kafasi[1]<=0 :
        return 1 #çarptıysa 1 dön
    else:
        return 0 #çarpmadıysa 0 dön
#KURAL:Kendine çarpma
def kendine_carpma(yilan_konum):
    yilan_kafasi = yilan_konum[0]
    #yilan_konum[1:] kafayı yani ilk satırı atla diğerlerine bak(slicing)
    if yilan_kafasi in yilan_konum[1:]:
        return 1 #kendine çarptıysa 1 dön
    else:
        return 0 #kendine çarpmadıysa 0 dön


def main():
 k=-1
 #oyun penceresini siyah zemin oluşturduk
 img = np.zeros((500, 500, 3), dtype='uint8')

 pygame.init()#kütüphaneyi başlat
 # Yılan ve Elmanın ilk konumu
 yilan_konum = [[250, 250], [240, 250], [230, 250]]
 elma_konum = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]

 score = 0#oyun puanını tutan değişken
 prev_button_direction = 1
 button_direction = 1
 yilan_kafasi = [250, 250]
 direction='right'
 while True:
    im = np.zeros((500, 500, 3), dtype='uint8')
    #cv2.imshow('a', im)oluşturduğumuz np arrayi
    cv2.waitKey(1)

    #WEBCAM ÜZERİNDEN OYNAYACAKSANIZ---------------------------------------------------
    for event in pygame.event.get() :#olayları yakala
        if event.type == pygame.QUIT:#olay q tuşuna basmaksa
            pygame.quit()#kütüphaneyi kapat
            sys.exit()#kapat
        elif event.type == pygame.KEYDOWN:#olay klavye olayıysa
            if (event.key == K_LEFT or event.key == K_a) and direction != 'right':#sol tuş ya da A'ya basılırsa
                direction = 'left'
                button_direction = 0
                k == 'U+2190'
            elif (event.key == K_RIGHT or event.key == K_d) and direction != 'left':#sağ tuş ya da D'ye basılırsa
                direction = 'right'
                button_direction = 1
                k == 'U+2192'
            elif (event.key == K_UP or event.key == K_w) and direction != 'down':#yukarı tuşu ya da w'ye basılırsa
                direction = 'up'
                button_direction = 3
                k == 'U+2191'
            elif (event.key == K_DOWN or event.key == K_s) and direction != 'up':#aşağı tuşu ya da s'ye basılırsa
                direction = 'down'
                button_direction = 2
                k == 'U+2193'
            elif event.key == K_ESCAPE or event.key == K_q:#esc tuşu ya da q'ya basılırsa
                pygame.quit()
                sys.exit()
    #-------------------------------------------------------------------


    # ELMA ÇİZ(kırmızı kare)
    cv2.rectangle(im, (elma_konum[0], elma_konum[1]), (elma_konum[0] + 12, elma_konum[1] + 12),(0, 0, 255), -1)
    #YILAN ÇİZ(yesil dikdörtgenleri oluşturduk)
    for position in yilan_konum:
        cv2.rectangle(im, (position[0], position[1]), (position[0] + 12, position[1] + 12), (0, 255, 0), 2)

    # Sabit bir süreden sonra yılan ilerler
    t_end = time.time() + 0.2
    #k:basılan tuşu tutar
    k = -1 #hiçbir tuşa basılmadığında waitKey() -1 döndürür

    while time.time() < t_end:
     if k == -1:
        k = cv2.waitKey(125)
     else:
        continue

    #KLAVYE ÜZERİNDEN OYNAYACAKSANIZ--------------------------------------------------------------
    '''
    # 0-Left, 1-Right, 3-Up, 2-Down, q-Break
    # a-Left, d-Right, w-Up, s-Down
    if keyboard.is_pressed('up') and prev_button_direction != 2 or k == ord('w') and prev_button_direction != 2:
        button_direction = 3
        direction = 'up'
        k == 'U+2191'
    elif keyboard.is_pressed('down') and prev_button_direction != 3 or k == ord('s') and prev_button_direction != 3:
        button_direction = 2
        direction='down'
        k == 'U+2193'
    elif keyboard.is_pressed('left') and prev_button_direction != 1 or k == ord('a') and prev_button_direction != 1:
        button_direction = 0
        direction = 'left'
        k == 'U+2190'
    elif  keyboard.is_pressed('right')and prev_button_direction != 0 or k == ord('d') and prev_button_direction != 0:
        button_direction = 1
        direction = 'right'
        k == 'U+2192'
    elif k == ord('q'):#q ye bastığında çık
        break
    elif k==32: #boşluk tuşuna basınca durdurulur
        cv2.waitKey()#herhangi bir tuşa basınca başlar
    else:
        button_direction = button_direction
        
    '''

    prev_button_direction = button_direction

    # basılan tuşa göre kafa konumunu ayarla
    if button_direction == 1 or direction =='right':#sağ
        yilan_kafasi[0] += 10#x'i arttırdık
    elif button_direction == 0 or direction == 'left':#sol
        yilan_kafasi[0] -= 10#x'i eksilttik
    elif button_direction == 2 or direction == 'down':#aşağı
        yilan_kafasi[1] -= 10#y'yi eksilttik
    elif button_direction == 3 or direction == 'up':#yukarı
        yilan_kafasi[1] += 10#y'yi arttırdık

    # Elma yiyince yilanın boyunu uzatalım
    if yilan_kafasi == elma_konum:
        elma_konum, score = elma_yemek(elma_konum, score)
        yilan_konum.insert(0, list(yilan_kafasi))#çizilen dikdörtgeni ekle
    else:#yılan ilerliyor görünümü sağlar
        yilan_konum.insert(0, list(yilan_kafasi))#yılanın başı listeye ekleniyor
        yilan_konum.pop()#kuyruk siliniyor

    # surfarray.make_surface komutu bir numpy dizisini bir pygame Surface nesnesine dönüştürür
    imc = pygame.surfarray.make_surface(im)  # diziyi pygame kütüphanesinin anlayabileceği bir formata dönüştürdük
    img = pygame.display.set_mode((500, 500))  # 500x500 boyutunda bir pencere oluştur
    imc = pygame.transform.rotate(imc, 90)
    img.blit(imc, (0, 0))  # surface'i screen'in sol üst köşesine çiz
    pygame.display.flip()  # pencereyi güncelle

    # Skor yazdıralım
    if sinirlara_carpma(yilan_kafasi) == 1 or kendine_carpma(yilan_konum) == 1:#hata yapılırsa
        font = cv2.FONT_ITALIC
        img = np.zeros((500, 500, 3), dtype='uint8')#siyah zemin üstüne
        cv2.putText(img, 'SKORUNUZ: {}'.format(score), (140, 250), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('a', img)
        cv2.waitKey(2000)#2saniye ekranda tut
        cv2.destroyAllWindows()#pencereleri kapat
        main()#oyunu tekrar başlat
        pygame.time.wait(1000)#1saniye bekle


if __name__ == '__main__':
	main()
