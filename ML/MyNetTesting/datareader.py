import pickle
import matplotlib.pyplot as plt

path = "/home/kuba/Documents/gitfolders/Tracking_python_data/mask_net/"
names =[ '0_newdata_imagenet', '0_newdata_imagenet_100', '0_newdata_imagenet_150', '0_newdata_imagenet_200', '0_newdata_imagenet_250', '0_newdata_imagenet_350' ]
val_accs = []
val_acc = []
#continues = [ '0_newdata_imagenet_100']

for name in names:

    pickle_in = open(path + name, 'rb')
    history = pickle.load(pickle_in)
    #print(history)
    #acc = history['acc']
    val_acc += history['val_acc']
#    if name in [j[:len(j)-4] for j in continues]:
#       pickle_in2 = open("../../mask_net/" + name + "_100", 'rb')
#        historycont = pickle.load(pickle_in2)
#        val_acc += historycont['val_acc']
#        pickle_in2 = open("../../mask_net/" + name + "_150", 'rb')
#        historycont = pickle.load(pickle_in2)
#        val_acc += historycont['val_acc']

#    val_accs.append(val_acc)
    #loss = history['loss']
    #val_loss = history['val_loss']

    #plt.figure(figsize=(8, 8))
    #plt.subplot(2, 1, 1)
    #plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='0_newdata_imagenet') #'Validation Accuracy' byl tab
    
    #plt.subplot(2, 1, 2)
    #plt.plot(loss, label='Training Loss')
    #plt.plot(val_loss, label='Validation Loss')
    #plt.legend(loc='upper right')
    #plt.ylabel('Cross Entropy')
    #plt.ylim([0,max(plt.ylim())])
    #plt.title('Training and Validation Loss')
    #plt.show()


plt.plot([50,50], plt.ylim())
plt.plot([100,100], plt.ylim())
plt.plot([150,150], plt.ylim())
plt.plot([200,200], plt.ylim())
plt.plot([250,250], plt.ylim())
plt.legend(loc='upper left')
plt.ylabel('Accuracy')
plt.ylim([min(plt.ylim()),1])
plt.title('Validation Accuracy') # Training and 
plt.show()