#decodes text file produced by webpage
import os, sys
from cv2 import cv2
import numpy as np

pathf = '48/info.txt' #text file
pathz = 'VID/15FPS/to_do/48' #pictures file
save_path = 'fromweb/' #save combined pictures
f = open(pathf, 'r')
content = f.read()
made = content.count(',') #number of matches should be one less than number of frames
tobe = len(os.listdir(pathz))
#if tobe - 1 != made:
    #print("Number of matches is bad!")
    #sys.exit(0)

content = content.split(',') #matches
del content[-1] #last one is blank

def Saver(nr1, nr2, img1, img2, licznik, folder):
    vis = np.zeros((224, 448, 3), np.uint8)
    begin1 = nr1 * 224
    begin2 = nr2 * 224
    vis[:224, :224, :3] = img1[:224, begin1:begin1+224, :3]
    vis[:224, 224:448, :3] = img2[:224, begin2:begin2+224, :3]
    cv2.imwrite(save_path + "/" + folder + "/" + str(licznik) + ".png", vis)

licznikZ = 1 #cointer for imgs
licznikY = 722 #counter of good matches
licznikN = 369 #counter of bad matches
for idx, dop in enumerate(content):
    print("{} -> {}".format(idx, dop))
    if dop != '0': #jesli jest dopasowanie
        img1 = cv2.imread(pathz + '/' + str(licznikZ) + '.png') #ladujemy zdj
        img2 = cv2.imread(pathz + '/' + str(licznikZ+1) + '.png')
        matching = dop.split('.') #rozdzielamy pojedyncze dop
        for m in matching:
            Saver(int(m[0])-1, int(m[2])-1, img1, img2, licznikY, 'YES' ) #moge robic m[0] bo liczba zdj nie przekracza 10
            licznikY += 1
    if licznikZ % 3 == 0: #co trzecie zdj tworzymy dopasowania NO
        n = int(img1.shape[1] / 224) # ilosc obiektow
        for i in range(n-1):
            for j in range(i+1, n):
                Saver(i, j, img1, img1, licznikN, 'NO')
                licznikN += 1
    licznikZ += 1