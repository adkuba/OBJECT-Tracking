import keras
import pickle
import os, random
import numpy as np
from cv2 import cv2

#input for first image
base_model1 = keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet', pooling='avg') #image classifier base
for layer in base_model1.layers:
    layer.trainable = False

#input for second image
base_model2 = keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet', pooling='avg') #image classifier base
for layer in base_model2.layers:
    layer.name = layer.name + str("_2")
    layer.trainable = False

#difference between outputs
def absolute(tensors):
    return [keras.backend.abs(tensors[0]-tensors[1])]

layerLambda = keras.layers.Lambda(absolute)
combined = layerLambda([base_model1.output, base_model2.output])

#final layer for score
z1 = keras.layers.Dense(1, activation='sigmoid')(combined)
model = keras.models.Model(inputs=[base_model1.input, base_model2.input], outputs=z1)

#after compiling you can train
model.compile(optimizer=keras.optimizers.RMSprop(lr=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

#folder structure for training
#__DATA
#   |__train
#   |   |__YES
#   |   |__NO
#   |__validation
#       |__YES
#       |__NO

train_dir = 'DATA/train'
validation_dir = 'DATA/validation'
train_yes_dir = train_dir + '/YES'
print ('Total training YES images:', len(os.listdir(train_yes_dir)))
train_no_dir = train_dir + '/NO'
print ('Total training NO images:', len(os.listdir(train_no_dir)))
validation_yes_dir = validation_dir + '/YES'
print ('Total validation YES images:', len(os.listdir(validation_yes_dir)))
validation_no_dir = validation_dir + '/NO'
print ('Total validation NO images:', len(os.listdir(validation_no_dir)))

#more batch size more memory used
batch_size = 8

#following is image generator

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

epochs = 100
steps_per_epoch = 669 # floor(imgs number / batch size)
validation_steps = 223 # as above

#training
history = model.fit_generator(train_gen, steps_per_epoch = steps_per_epoch, epochs=epochs, workers=1, validation_data=validation_gen, validation_steps=validation_steps)

#history and model save
nazwa = "YOUR MODEL NAME"
with open("./" + nazwa, 'wb') as filepi:
    pickle.dump(history.history, filepi)

model.save("./" + nazwa + ".h5")
