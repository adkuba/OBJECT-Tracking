#link do repo w README
#model oparty na mobilenet v2
from tensorflow import keras
import os
import numpy as np
import random
import pickle
import cv2

#UWAGA UBERTURBOHIPERWAZNE bez tego tensorflow gpu nie dziala
from tensorflow import config
physical_devices = config.experimental.list_physical_devices('GPU')
config.experimental.set_memory_growth(physical_devices[0], True)

def _make_divisible(v, divisor, min_value=None):
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v


def relu6(x):
    #Relu 6
    return keras.backend.relu(x, max_value=6.0)


def _conv_block(inputs, filters, kernel, strides):
    #convolution block
    channel_axis = 1 if keras.backend.image_data_format() == 'channels_first' else -1

    x = keras.layers.Conv2D(filters, kernel, padding='same', strides=strides)(inputs)
    x = keras.layers.BatchNormalization(axis=channel_axis)(x)
    return keras.layers.Activation(relu6)(x)


def _bottleneck(inputs, filters, kernel, t, alpha, s, r=False):
    #bottleneck
    channel_axis = 1 if keras.backend.image_data_format() == 'channels_first' else -1
    # Depth
    tchannel = keras.backend.int_shape(inputs)[channel_axis] * t
    # Width
    cchannel = int(filters * alpha)

    x = _conv_block(inputs, tchannel, (1, 1), (1, 1))

    x = keras.layers.DepthwiseConv2D(kernel, strides=(s, s), depth_multiplier=1, padding='same')(x)
    x = keras.layers.BatchNormalization(axis=channel_axis)(x)
    x = keras.layers.Activation(relu6)(x)

    x = keras.layers.Conv2D(cchannel, (1, 1), strides=(1, 1), padding='same')(x)
    x = keras.layers.BatchNormalization(axis=channel_axis)(x)

    if r:
        x = keras.layers.Add()([x, inputs])

    return x


def _inverted_residual_block(inputs, filters, kernel, t, alpha, strides, n):
    #inverted residual block
    x = _bottleneck(inputs, filters, kernel, t, alpha, strides)

    for i in range(1, n):
        x = _bottleneck(x, filters, kernel, t, alpha, 1, True)

    return x

def reduceNet(inputs, alpha=1.0):
    #first part of new model
    #conv + four first bottlenecks

    first_filters = _make_divisible(32 * alpha, 8)
    x = _conv_block(inputs, first_filters, (3, 3), strides=(2, 2))
    x = _inverted_residual_block(x, 16, (3, 3), t=1, alpha=alpha, strides=1, n=1)
    x = _inverted_residual_block(x, 24, (3, 3), t=6, alpha=alpha, strides=2, n=2)
    x = _inverted_residual_block(x, 32, (3, 3), t=6, alpha=alpha, strides=2, n=3)
    x = _inverted_residual_block(x, 64, (3, 3), t=6, alpha=alpha, strides=2, n=4)
    #wyjscie po tym to 14^2 x 64
    return x

def absolute(tensors):
        return [keras.backend.abs(tensors[0]-tensors[1])]

def fullNet(input_shape, alpha=1.0):
    #full net architecture
    inputs = [keras.layers.Input(shape=input_shape), keras.layers.Input(shape=input_shape)]
    #mamy 2 inputy teraz robimy small reduce
    x1 = reduceNet(inputs[0])
    x2 = reduceNet(inputs[1])
    #laczymy dwa wejscia w jedno
    #difference between outputs
    combined = keras.backend.abs(x1-x2)
    #pozostala czesc sieci
    combined = _inverted_residual_block(combined, 96, (3, 3), t=6, alpha=alpha, strides=1, n=3)
    combined = _inverted_residual_block(combined, 160, (3, 3), t=6, alpha=alpha, strides=2, n=3)
    combined = _inverted_residual_block(combined, 320, (3, 3), t=6, alpha=alpha, strides=1, n=1)
    
    if alpha > 1.0:
        last_filters = _make_divisible(1280 * alpha, 8)
    else:
        last_filters = 1280

    combined = _conv_block(combined, last_filters, (1, 1), strides=(1, 1))
    combined = keras.layers.GlobalAveragePooling2D()(combined)
    #tu mam troche inaczej niz gosciu na gicie
    #zamiast conv2d i innych zwykla warstwa dense z 1 outputem
    output = keras.layers.Dense(1, activation='sigmoid')(combined)

    model = keras.Model(inputs, output)

    return model


model = fullNet((224, 224, 3))
#print(model.summary())
model.compile(optimizer=keras.optimizers.RMSprop(lr=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

#more batch size more memory used
batch_size = 8

#following is image generator
def convert(img):
    img = np.expand_dims(img, axis=0)
    img = (2.0 / 255.0) * img - 1.0
    img = img.astype('float32')
    return img

def datacreate(path, cat, val, img): #"/YES/" -> type 1 -> val
    img = cv2.imread(path + cat + img)
    img1 = img[:224, :224]
    img2 = img[:224, 224:448]
    i1 = convert(img1)
    i2 = convert(img2)
    i1 = np.squeeze(i1, axis=0)
    i2 = np.squeeze(i2, axis=0)
    return [i1, i2, val] #zapakowane dane

#przerobiona wersja czytajaca dane w k czesciach - nie laduje wszystkiego naraz do ramu
def imagesGenerator(path, k):
    alldata = []
    yesimages = os.listdir(path + '/YES')
    noimages = os.listdir(path + '/NO')
    yeslen = len(yesimages)
    nolen = len(noimages)

    while True:
        x1 = []
        x2 = []
        y = []
        sy = 0
        ey = int(yeslen/k)
        sn = 0
        en = int(nolen/k)
        for i in range(k):
            bufor = []
            for img in yesimages[sy:ey]:
                bufor.append(datacreate(path, "/YES/", 1, img))
            for img in noimages[sn:en]:
                bufor.append(datacreate(path, "/NO/", 0, img))
            random.shuffle(bufor)
            #uwaga liczba zdjec warto zeby byla podzielna przez k bo inaczej obetnie
            ey=sy
            en=sn
            sy+=int(yeslen/k)
            sn+=int(nolen/k)

            for d in bufor:
                if len(x1) == batch_size:
                    yield [np.array(x1), np.array(x2)], np.asarray(y)
                    x1.clear()
                    x2.clear()
                    y.clear()
                x1.append(d[0])
                x2.append(d[1])
                y.append(d[2])

'''
#----------------
#pierwsze uczenie
train_dir = '/home/kuba/Pictures/training_todo/auta_training/train'
validation_dir = '/home/kuba/Pictures/training_todo/auta_training/validation'

train_gen = imagesGenerator(train_dir, 8)
validation_gen = imagesGenerator(validation_dir, 4)

epochs = 50
steps_per_epoch = 669 # floor(imgs number / batch size)
validation_steps = 223 # as above

#training
history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

#history and model save
nazwa = "newNet_50e_cars"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")
'''


#--------------
#drugie uczenie
train_dir = '/home/kuba/Pictures/training_todo/konie_training/train'
validation_dir = '/home/kuba/Pictures/training_todo/konie_training/validation'

train_gen = imagesGenerator(train_dir, 6)
validation_gen = imagesGenerator(validation_dir, 4)

epochs = 50
steps_per_epoch = 502 # floor(imgs number / batch size)
validation_steps = 140 # as above

#training
history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

#history and model save
nazwa = "newNet_50e_horses"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")



#--------------
#trzecie uczenie
train_dir = '/home/kuba/Pictures/training_todo/auta_konie_training/train'
validation_dir = '/home/kuba/Pictures/training_todo/auta_konie_training/validation'

train_gen = imagesGenerator(train_dir, 14)
validation_gen = imagesGenerator(validation_dir, 10)

epochs = 50
steps_per_epoch = 1172 # floor(imgs number / batch size)
validation_steps = 363 # as above

#training
history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

#history and model save
nazwa = "newNet_50e_cars_horses"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")