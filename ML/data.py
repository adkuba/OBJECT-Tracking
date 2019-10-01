#reads folder with pictures as processed frames
#user creates set of images
import argparse
import os
from cv2 import cv2
import numpy as np

#parser to point wich video we want to process in floder
parser = argparse.ArgumentParser(description='VID number.')
parser.add_argument('number', metavar='N', type=int, nargs=1, help='number of video to process')
parser.add_argument('frameN', metavar='F', type=int, nargs=1, help='video start frame number starting from 1')
args = parser.parse_args()
path='VID/15FPS/to_do' #main folder with videos
save_path = '/Pictures/cd'
path_to_folder=path + '/' + str(args.number[0])
cv2.namedWindow("old", cv2.WINDOW_NORMAL)
cv2.namedWindow("new", cv2.WINDOW_NORMAL)
class Found(Exception): pass
licznikY = 1684
licznikN = 2855
licznikSN = 1
con = 0

def numbers(img):
    image = img.copy()
    _, width = image.shape[:2]
    n = int(width/224) #number of images
    pixels = 50 #where to draw number
    for i in range(n):
        cv2.putText(image, str(i), (pixels, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        pixels += 224
    return image

def Saver(nr1, nr2, img1, img2, licznik, folder):
    vis = np.zeros((224, 448, 3), np.uint8)
    begin1 = nr1 * 224
    begin2 = nr2 * 224
    vis[:224, :224, :3] = img1[:224, begin1:begin1+224, :3]
    vis[:224, 224:448, :3] = img2[:224, begin2:begin2+224, :3]
    cv2.imwrite(save_path + "/" + folder + "/" + str(licznik) + ".png", vis)

video_in_img = sorted(os.listdir(path_to_folder), key=lambda name: int(name[:len(name)-4])) #sorting by numbers
length = len(video_in_img) #number of images to analize
last = cv2.imread(path_to_folder + '/' + video_in_img[args.frameN[0]-1]) #starting frame
try:
    for idx, img_name in enumerate(video_in_img[args.frameN[0]:]): #reading from desired frame number
        if con !=0: #special case for skipping frames
            con -= 1
            continue
        new = cv2.imread(path_to_folder + '/' + img_name) #reading img
        cv2.imshow("old", numbers(last))
        cv2.imshow("new", numbers(new))
        cv2.waitKey(200)
        dop = False
        print("{}/{}; e for exit; d for next; f +10".format(idx+1+args.frameN[0], length)) #status
        while True: #saving YES images
            user1 = input("Old image: ")
            if user1 == 'd': #next frame
                break
            if user1 == 'e':
                raise Found
            if user1 == 'f': #skipping frames
                con = 10
                break
            user2 = input("Matches new: ")
            Saver(int(user1), int(user2), last, new, licznikY, 'YES') #saving
            licznikY += 1
            dop = True
        if dop and new.shape[1] > 224 and licznikSN == 3: #if there was match and min 2 imgs we create NO pictures every third
            n = int(new.shape[1] / 224) #number of imgs
            for i in range(n-1):
                for j in range(i+1, n):
                    Saver(i, j, new, new, licznikN, 'NO') #creating bad matches
                    licznikN += 1
        last = new.copy() #change
        if licznikSN == 3:
            licznikSN = 1
        else:
            licznikSN += 1
except Found:
    pass

print('END!')
print("NO: {}, YES: {}".format(licznikN, licznikY))