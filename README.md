# OBJECTTracking

### Table of Contents
1. [What I've learned?](#what-Ive-learned)
2. [Android application](#android-application)
3. [IOS Application](#ios-application)
4. [Machine learning](#ml)
5. [Hardware](#hardware)
6. [Electronic board](#electronic-board)

## What I've learned?
* How to use **machine learning** to detect, track objects. How to build and train your own machine learning model and evolutional model. (**Python, Tensorflow, UnityML**)
* Building my own **Android** application that uses machine learning and camera. (**Java, Android Studio**)
* How to build simple **IOS** application that uses built in and external machine learning models, bluetooth and camera. (**Swift, XCode, OpenCV**)
* How to develop from the ground up, special **electronic board** that uses bluetooth. (**Silicon Labs, C**)

#### [Android application](APPS/Android/)
In Java works with SDK wersion 28 - Android 9. Application uses tensorflow model to detect objects and allows user to record videos from the camera. You can also click on object and it shows all the pictures of the same category objects in frame. Good base for developing visual machine learning solutions. <br>
Some errors with older Huawei phones. Optimalization posibilities: https://developers.google.com/ml-kit/ I also share compressed (quantitized) Tensorflow lite model in application resources folder. (*ssd_mobilenet_v2_quantized_coco*)


![android](IMAGES/android.png)

#### [IOS application](APPS/IOS/)
IOS application. Compiled OpenCV 4.0.0 framework with trackers avaiable here (https://www.dropbox.com/s/0iqwqfjz95ehut5/opencv2.framework.zip?dl=0) add it to Frameworks in XCode project settings. You can compile framework yourself following tutorial in official page but remember to add tracking package! Framework should be in main project folder (CamTracking2), can be changed in build settings. You can also follow this tutorial https://medium.com/@yiweini/opencv-with-swift-step-by-step-c3cc1d1ee5f1 Aplication allows to test OpenCV trackers, connect to Bluetooth devices and record videos. No suport for Vision tracking so far.


#### [ML](ML/)
Machine learning. Folder with files for creating special object comparison net, running different nets and collecting data. Everything using Keras and Tensorflow. Useful as example to work with.
* **[my_net.py](ML/my_net.py)** <br>
Using keras you can quickly create, train and deploy ready to use model of special net. It is developed for comparing the similarity of two pictures. I also share trained model on car pictures. Aproximately 5k images, 85% accuracy, 350 epochs. 

![mynet](IMAGES/my_net.png)
* **[data.py](ML/data.py)** <br>
Script in python using OpenCV to create set of 2 images either similar or different from video file. All commands in terminal. It needs preprocessed video to display pictures - file *process.py* uses Tensorflow model *mask_rcnn_inception_v2_coco*. Shows pictures of desired category objects from one frame and next. User needs to point which are similar, sets are created automaticly. Screenshot below - second picture.
* **[webpage](ML/webpage/)** <br>
Simple webpage that enables data collection similar to data.py but with progress save. Some improvements can be done. It needs preprocessed video to display pictures - file *process.py*. Webpage creates text file that should look like that 1-2,2-1 it means the same objects are 1 from first picture and 2 from second, 2 from first and 1 from second. Bad matches are created automaticly. Then we can create set of images with *webdecoder.py*. Folder structure without pictures as in repository. Screenshot below - first picture.
* **[run.py](ML/run.py)** <br>
File containing code for running different kinds of neural nets. Mask rcnn object detection, mobilenet_v2 classifier, ssd mobilenet_v2 object detector and Tensorflow Lite model.


#### ![screen](IMAGES/sc.png)


#### Hardware

Simple device to use with mobile phones. All parts were designed in Inventor Proffesional and then 3D printed. Lower part has special thread used in almost all photography devices. We can easily mount it to, for example tripod. Inside the device, is place for all the electronics. I choosed Arduino Nano, Bluetooth for connection and stepper motor. The last one was a mistake. Much better would be the brushless motor used widely in camera gimbals. Upper part has a simple mount for smartphones, wich works with almost all models.

![hardware](IMAGES/hardware.jpg)

#### [Electronic board](ELECTRONIC-BOARD/)

Using Silicon Labs chip I developed special electronic board that uses Bluetooth. The goal was to implement [AoA in Bluetooth 5.1](https://www.silabs.com/products/wireless/learning-center/bluetooth/bluetooth-direction-finding), but unfortunatelly I wasn't able to achieve that. However I learned how to project board using Eagle from Autodesk and low level programing in Silicon Labs and C. Read [board.pdf](https://github.com/adkuba/OBJECTTracking/blob/master/board.pdf) to learn more about the idea.

![my-chip-board](IMAGES/chip-low.png)
![my-antenna-board](IMAGES/antenna-low.png)
![ready-board](IMAGES/ready-low.jpg)

Icons credits: 
[link1](https://www.flaticon.com/authors/freepik) 
[link2](https://www.flaticon.com/authors/pause08) 
[link3](https://www.flaticon.com/authors/smashicons)
