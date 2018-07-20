from shutil import copy
import numpy as np
from sklearn.model_selection import train_test_split
from os import listdir, remove
import glob
import os

# src_dir = 'all/'
# copy('all/images/1.png', 'split/train/images/')
for sub in ['train', 'val', 'test']:
    for child in ['images', 'labels']:
        directory = 'split/' + sub + '/' + child + '/'
        if not os.path.exists(directory):
            os.mkdir(directory)

paths = ['split/test/images/*', 'split/test/labels/*', 'split/train/images/*',
         'split/train/labels/*', 'split/val/images/*', 'split/val/labels/*']
# remove
for path in paths:
    files = glob.glob(path)
    for f in files:
        remove(f)

# copy
all_images = listdir('all/images')
all_labels = listdir('all/labels')
all_images.sort()
all_labels.sort()
# all_labels = []
# for image in all_images:
#     all_labels.append(image.split('.')[0] + '.txt')

train_ratio = 0.8
val_ratio = 0.1
test_ratio = 0.1

image_train, image_test, label_train, label_test = train_test_split(all_images, all_labels, test_size=val_ratio+test_ratio, random_state=42)
image_val, image_test, label_val, label_test = train_test_split(image_test, label_test, test_size=test_ratio/(val_ratio+test_ratio), random_state=42)

for image in image_test:
    copy('all/images/' + image, 'split/test/images/')
for label in label_test:
    copy('all/labels/' + label, 'split/test/labels/')

for image in image_train:
    copy('all/images/' + image, 'split/train/images/')
for label in label_train:
    copy('all/labels/' + label, 'split/train/labels/')

for image in image_val:
    copy('all/images/' + image, 'split/val/images/')
for label in label_val:
    copy('all/labels/' + label, 'split/val/labels/')
