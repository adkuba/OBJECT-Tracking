import os, random
from shutil import copyfile

'''
basePath = '/home/kuba/Pictures/training_todo/konie_raw'
destPath = '/home/kuba/Pictures/training_todo/konie_training'

yes = os.listdir(basePath + '/YES')
no = os.listdir(basePath + '/NO')

#25 procent to validation
procent_validation = 0.25

yesVal = random.choices(yes, k=int(len(yes)*procent_validation))
noVal = random.choices(no, k=int(len(no)*procent_validation))

for f in yesVal:
    copyfile(basePath + '/YES/' + f, destPath + '/validation/YES/' + f)

for f in noVal:
    copyfile(basePath + '/NO/' + f, destPath + '/validation/NO/' + f)

for f in yes:
    if f not in yesVal:
        copyfile(basePath + '/YES/' + f, destPath + '/train/YES/' + f)

for f in no:
    if f not in noVal:
        copyfile(basePath + '/NO/' + f, destPath + '/train/NO/' + f)
'''

#teraz merge folderu auta i konie

folder1 = '/home/kuba/Pictures/training_todo/konie_training'
folder2 = '/home/kuba/Pictures/training_todo/auta_training'
dest = '/home/kuba/Pictures/training_todo/auta_konie_training'

counter_yes = 0
counter_no = 0

#train

for f in os.listdir(folder1 + '/train/YES'):
    copyfile(folder1 + '/train/YES/' + f, dest + '/train/YES/' + str(counter_yes) + '.png')
    counter_yes += 1

for f in os.listdir(folder2 + '/train/YES'):
    copyfile(folder2 + '/train/YES/' + f, dest + '/train/YES/' + str(counter_yes) + '.png')
    counter_yes += 1

for f in os.listdir(folder1 + '/train/NO'):
    copyfile(folder1 + '/train/NO/' + f, dest + '/train/NO/' + str(counter_no) + '.png')
    counter_no += 1

for f in os.listdir(folder2 + '/train/NO'):
    copyfile(folder2 + '/train/NO/' + f, dest + '/train/NO/' + str(counter_no) + '.png')
    counter_no += 1

#validation

counter_yes = 0
counter_no = 0

for f in os.listdir(folder1 + '/validation/YES'):
    copyfile(folder1 + '/validation/YES/' + f, dest + '/validation/YES/' + str(counter_yes) + '.png')
    counter_yes += 1

for f in os.listdir(folder2 + '/validation/YES'):
    copyfile(folder2 + '/validation/YES/' + f, dest + '/validation/YES/' + str(counter_yes) + '.png')
    counter_yes += 1

for f in os.listdir(folder1 + '/validation/NO'):
    copyfile(folder1 + '/validation/NO/' + f, dest + '/validation/NO/' + str(counter_no) + '.png')
    counter_no += 1

for f in os.listdir(folder2 + '/validation/NO'):
    copyfile(folder2 + '/validation/NO/' + f, dest + '/validation/NO/' + str(counter_no) + '.png')
    counter_no += 1