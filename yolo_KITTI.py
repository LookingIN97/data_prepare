import os
from glob import glob
import cv2
from shutil import copy

# resolution
width = 640
height = 480

# save
counter = 0
for temp_path in glob('all/images/*.png'):
    number = int(temp_path.split('/')[-1].split('.')[0])
    if number > counter:
        counter = number
counter += 1

# paths
dataset_list = ['july1_2red', 'july1_2blue']
for data_name in dataset_list:
    path_list = glob('label_' + data_name + '/*.txt')
    save_directory = 'all/labels/'
    class_path = 'label_' + data_name + '/classes.txt'

    # read classes
    # class_dic = {}
    # with open(class_path) as f:
    #     for i, line in enumerate(f):
    #         class_dic[i] = line.strip()
    class_dic = {15: 'blue'}

    for path in path_list:
        directory, file_name = path.split('/')
        if file_name == 'classes.txt':
            continue
        if file_name.split('.')[0] == 'frame4608':
            continue
        print(data_name + '/' + file_name.split('.')[0] + '.png')
        copy(data_name + '/' + file_name.split('.')[0] + '.png', 'all/images/' + str(counter) + '.png')
        output_string = ''
        with open(path) as f:
            for line in f:
                line = line.strip()
                line_list = line.split(' ')
                line_list = list(map(float, line_list))
                class_name = class_dic[int(line_list[0])]
                # bounding box
                # left, up, right, bottom
                left = int((line_list[1] - line_list[3]/2) * width)
                right = int((line_list[1] + line_list[3]/2) * width)
                up = int((line_list[2] - line_list[4]/2) * height)
                bottom = int((line_list[2] + line_list[4]/2) * height)
                bbox = [left, up, right, bottom]
                bbox = list(map(str, bbox))
                # write .txt files
                class_name = 'red'
                output_string += class_name + ' ' + ' '.join(['0'] * 3) + ' ' + ' '.join([b for b in bbox]) + ' ' + ' '.join(['0'] * 8) + '\n'
        with open(save_directory + str(counter) + '.txt', 'w') as label_file:
            label_file.write(output_string)
        print('all/labels/' + str(counter) + '.txt')
        counter += 1

