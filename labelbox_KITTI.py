import csv
import cv2
from shutil import copy

dataset_list = ['jun28_blue', 'jun28_red']

counter = 2000
for dataset in dataset_list:
    reader = csv.reader(open(dataset + '.csv'))
    for i, row in enumerate(reader):
        if i == 0:
            header = row
        else:
            file_name = row[1].split('?alt')[0].split('%2F')[-1]
            img = cv2.imread(dataset + '/' + file_name)
            if row[2] == 'Skip':
                continue
            else:
                label_dict = eval(row[2])
            output_string = ''
            for digit, label in label_dict.items():
                # points = label_dict[digit][0]
                points = label[0]
                x_set = set()
                y_set = set()
                for point in points:
                    x_set.add(point['x'])
                    y_set.add(480-point['y'])
                # bounding box
                # left, up, right, bottom
                bbox = [min(x_set), min(y_set), max(x_set), max(y_set)]
                bbox = list(map(str, bbox))

                # one row
                this_row = digit + ' ' + ' '.join(['0'] * 3) + ' ' + ' '.join([b for b in bbox]) + ' ' + ' '.join(['0'] * 8) + '\n'
                # this_row = 'red' + ' ' + ' '.join(['0'] * 3) + ' ' + ' '.join([b for b in bbox]) + ' ' + ' '.join(['0'] * 8) + '\n'
                output_string += this_row
                # write .txt files
            print('all/labels/' + str(counter) + '.txt')
            copy(dataset + '/' + file_name, 'all/images/' + str(counter) + '.png')
            with open('all/labels/' + str(counter) + '.txt', 'w') as label_file:
                label_file.write(output_string)
            counter += 1
