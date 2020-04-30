import keras
from cv2 import cv2
import numpy as np
import os, random, sys
import pickle
import matplotlib.pyplot as plt

import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = True  # to log device placement (on which device the operation ran)
                                    # (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
set_session(sess)  # set this TensorFlow session as the default session for Keras

model = keras.models.load_model('../../mask_net/0_newdata_imagenet_350.h5', custom_objects = { "keras": keras }) #ladujemy model ten keras jest potrzebny

#print("Number of layers: {}".format(len(model.layers)))
#sys.exit(0)
#jest 314 warstw bedziemy robic finetune od x warstwy
fine_tune_from = 306
for layer in model.layers[fine_tune_from:]:
  layer.trainable =  True

model.compile(optimizer = keras.optimizers.RMSprop(lr=0.00001), loss='binary_crossentropy', metrics=['accuracy'])

#model.summary()
#sys.exit(0)

train_dir = '/home/kuba/Pictures/SIMNet_mask/train'
validation_dir = '/home/kuba/Pictures/SIMNet_mask/validation'
train_yes_dir = train_dir + '/YES'
print ('Total training YES images:', len(os.listdir(train_yes_dir)))
train_no_dir = train_dir + '/NO'
print ('Total training NO images:', len(os.listdir(train_no_dir)))
validation_yes_dir = validation_dir + '/YES'
print ('Total validation YES images:', len(os.listdir(validation_yes_dir)))
validation_no_dir = validation_dir + '/NO'
print ('Total validation NO images:', len(os.listdir(validation_no_dir)))

#generator napisac jest ok ale czy nie spadnie z rowerka? bardzo duzo ramu bedzie potrzebne
batch_size = 8

def convert(img):
    img = np.expand_dims(img, axis=0)
    img = (2.0 / 255.0) * img - 1.0
    img = img.astype('float32')
    return img

def imagesGenerator(path):
    alldata = []
    for img in os.listdir(path + '/YES'):
        img = cv2.imread(path + "/YES/" + img)
        img1 = img[:224, :224]
        img2 = img[:224, 224:448]
        i1 = convert(img1)
        i2 = convert(img2)
        i1 = np.squeeze(i1, axis=0)
        i2 = np.squeeze(i2, axis=0)
        alldata.append([i1, i2, 1]) #zapakowane dane dla yes
    for img in os.listdir(path + '/NO'):
        img = cv2.imread(path + "/NO/" + img)
        img1 = img[:224, :224]
        img2 = img[:224, 224:448]
        i1 = convert(img1)
        i2 = convert(img2)
        i1 = np.squeeze(i1, axis=0)
        i2 = np.squeeze(i2, axis=0)
        alldata.append([i1, i2, 0]) #zapakowane dane dla no
    random.shuffle(alldata) #random danych

    while True:
        x1 = []
        x2 = []
        y = []
        for d in alldata:
            if len(x1) == batch_size:
                yield [np.array(x1), np.array(x2)], np.asarray(y)
                x1.clear()
                x2.clear()
                y.clear()
            x1.append(d[0])
            x2.append(d[1])
            y.append(d[2])

train_gen = imagesGenerator(train_dir)
validation_gen = imagesGenerator(validation_dir)

epochs = 50
steps_per_epoch = 669 #5357/8 (liczba zdj / batch size) podloga
validation_steps = 223 #1784

history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

nazwa = "0_newdata_imagenet_400f"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")