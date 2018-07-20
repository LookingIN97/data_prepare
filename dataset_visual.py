import cv2

if __name__ == "__main__":
    print("test: start")
    # pic path
    # file_path ='all/images/'
    # label_path = 'all/labels/'
    file_path = 'july17_blue1/'
    label_path = 'label_july17_blue1/'
    for x in range(15010, 16000):
        picName = str(x) + '.png'
        image = cv2.imread(file_path + picName)
        bbox_list = []
        with open(label_path + str(x) + '.txt') as f:
            print(label_path + str(x) + '.txt')
            for line in f:
                data = line.split()
                label = data[0]
                if label == 'red':
                    left = int(data[4])
                    up = int(data[5])
                    right = int(data[6])
                    bottom = int(data[7])
                    bbox_list.append([up, left, bottom, right])
                    cv2.rectangle(image, (left, up), (right, bottom), (0, 255, 0), 2)
                print(data)

        if x == 15012:
            cv2.imshow('frame', image)
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break
        if cv2.waitKey(500) & 0xFF == ord('s'):
            continue
