import cv2
import glob
from shutil import copy
import os

if __name__ == "__main__":
    print("test: start")
    # pic path
    # file_path ='all/images/'
    # label_path = 'all/labels/'
    file_path = 'july17_blue1/'
    label_path = 'label_' + file_path
    file_save = 'new_' + file_path
    label_save = 'new_' + label_path
    if not os.path.exists(file_save):
        os.makedirs(file_save)
    if not os.path.exists(label_save):
        os.makedirs(label_save)
    path_list = glob.glob(label_path + '*.txt')
    for path in path_list:
        if path.split('/')[-1] == 'classes.txt':
            continue
        x = path.split('/')[-1].split('.')[0]
        picName = x + '.jpg'
        image = cv2.imread(file_path + picName)
        bbox_list = []
        with open(label_path + x + '.txt') as f:
            print(label_path + x + '.txt')
            for line in f:
                line_list = line.split(' ')
                line_list = list(map(float, line_list))
                if line_list[0] == 15.0:
                    left = int((line_list[1] - line_list[3] / 2) * 640)
                    right = int((line_list[1] + line_list[3] / 2) * 640)
                    up = int((line_list[2] - line_list[4] / 2) * 480)
                    bottom = int((line_list[2] + line_list[4] / 2) * 480)
                    bbox_list.append([up, left, bottom, right])
                    cv2.rectangle(image, (left, up), (right, bottom), (0, 255, 0), 2)
                    print([up, left, bottom, right])
                print(line_list)


        cv2.imshow('frame', image)
        key = cv2.waitKey(5000) & 0xFF
        if key == ord('s'):
            copy(file_path + picName, file_save + picName)
            copy(label_path + x + '.txt', label_save + picName)
            continue
        elif key == ord('k'):
            continue
        elif key == ord('q'):
            break
        # if cv2.waitKey(5000) & 0xFF == ord('k'):
        #     continue
        # if cv2.waitKey(5000) & 0xFF == ord('q'):
        #     break
