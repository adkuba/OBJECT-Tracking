#3 dodatkowe warstwy 640, 320, 4 neurony z dropout
import keras
import pickle
import os, random
import sys
import numpy as np
import matplotlib.pyplot as plt
from cv2 import cv2


base_model1 = keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet', pooling='avg')
for layer in base_model1.layers:
    layer.trainable = False

base_model2 = keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet', pooling='avg')
for layer in base_model2.layers:
    layer.name = layer.name + str("_2")
    layer.trainable = False

def absolute(tensors):
    return [keras.backend.abs(tensors[0]-tensors[1])]

layerLambda = keras.layers.Lambda(absolute)
combined = layerLambda([base_model1.output, base_model2.output])

drop = keras.layers.Dropout(0.5)(combined)
z1 = keras.layers.Dense(640, activation='relu')(drop)
z2 = keras.layers.Dense(320, activation='relu')(z1)
z3 = keras.layers.Dense(4, activation='relu')(z2)
z4 = keras.layers.Dense(1, activation='sigmoid')(z3)
model = keras.models.Model(inputs=[base_model1.input, base_model2.input], outputs=z4)

model.compile(optimizer=keras.optimizers.RMSprop(lr=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

train_dir = '/home/kuba/Pictures/SIMNET_TRAIN/train'
validation_dir = '/home/kuba/Pictures/SIMNET_TRAIN/validation'
train_yes_dir = '/home/kuba/Pictures/SIMNET_TRAIN/train/YES'
print ('Total training YES images:', len(os.listdir(train_yes_dir)))
train_no_dir = '/home/kuba/Pictures/SIMNET_TRAIN/train/NO'
print ('Total training NO images:', len(os.listdir(train_no_dir)))
validation_yes_dir = '/home/kuba/Pictures/SIMNET_TRAIN/validation/YES'
print ('Total validation YES images:', len(os.listdir(validation_yes_dir)))
validation_no_dir = '/home/kuba/Pictures/SIMNET_TRAIN/validation/NO'
print ('Total validation NO images:', len(os.listdir(validation_no_dir)))
image_size = 224 
batch_size = 32

def convert(img):
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = (2.0 / 255.0) * img - 1.0
    img = img.astype('float32')
    return img

def data(path, item, cat, label):
    img = cv2.imread(path + cat + item)
    img1 = img[:224, :112]
    img2 = img[:224, 112:224]
    img1 = cv2.resize(img1, (224, 224))
    img2 = cv2.resize(img2, (224, 224))
    i1 = convert(img1)
    i2 = convert(img2)
    i1 = np.squeeze(i1, axis=0)
    i2 = np.squeeze(i2, axis=0)
    return [i1, i2, label]

def imagesGenerator(path):
    x1 = []
    x2 = []
    y = []
    yeslen = len(os.listdir(path + "/YES"))
    nolen = len(os.listdir(path + "/NO"))
    yes = []
    no = []
    while True:
        yes.clear()
        no.clear()
        while len(yes) != yeslen or len(no) != nolen:
            yespick = ""
            nopick = ""
            if len(yes) < yeslen:
                while True: 
                    yespick = random.choice(os.listdir(path + "/YES"))
                    if yespick not in yes:
                        yes.append(yespick)
                        break
            if len(no) < nolen:
                while True:
                    nopick = random.choice(os.listdir(path + "/NO"))
                    if nopick not in no:
                        no.append(nopick)
                        break
            if yespick is not "":
                wyn = data(path, yespick, "/YES/", 1)
                x1.append(wyn[0])
                x2.append(wyn[1])
                y.append(wyn[2])
            if len(x1) == 32:
                yield [np.array(x1), np.array(x2)], np.asarray(y)
                x1.clear()
                x2.clear()
                y.clear()
            if nopick is not "":
                wyn = data(path, nopick, "/NO/", 0)
                x1.append(wyn[0])
                x2.append(wyn[1])
                y.append(wyn[2])
            if len(x1) == 32:
                yield [np.array(x1), np.array(x2)], np.asarray(y)
                x1.clear()
                x2.clear()
                y.clear()

train_gen = imagesGenerator(train_dir)
validation_gen = imagesGenerator(validation_dir)

epochs = 15
steps_per_epoch = 119
validation_steps = 51

history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

nazwa = "3_640_320_4"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")