from RedBlueProcessImage import TraditionalDetection
# from process_image import TraditionalDetection
import time
import cv2

if __name__ == "__main__":
    print("test: start")
    detector = TraditionalDetection()
    color = 'b'
    # pic path
    file_path = 'all/images/'
    label_path = 'all/labels/'
    # list of file number's that want to test
    # y = [1,44,55,77,133,199,244,277,299,344,399,400,407,438,420,443]
    # y =[1]

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))

    start = time.time()
    counter = 0
    true_positive = 0
    false_positive = 0
    failed = 0
    for x in range(2000, 11032+1):
        picName = str(x) + '.png'
        image = detector.load_image(file_path, picName)
        bbox_list = []
        with open(label_path + str(x) + '.txt') as f:
            for line in f:
                data = line.split()
                label = data[0]
                if label == 'blue':
                    left = int(data[4])
                    up = int(data[5])
                    right = int(data[6])
                    bottom = int(data[7])
                    bbox_list.append([left, up, right, bottom])
                    cv2.rectangle(image, (left, up), (right, bottom), (0, 255, 0), 3)
        # print(bbox_list)
        target = detector.process_image(image, color)
        # print(target)
        image = detector.image
        # print('!!!!!')

        if counter % 10 == 0:
            end = time.time()
            fps = str(10 / (end - start))[:4]
            start = end
        counter += 1

        if target == [-1, -1]:
            failed += 1
        else:
            in_range = False
            for bbox in bbox_list:
                # print(bbox, target)
                if bbox[0] <= target[0] <= bbox[2] and bbox[1] <= target[1] <= bbox[3]:
                    in_range = True
            if in_range:
                true_positive += 1
            else:
                false_positive += 1
        cv2.circle(image,(target[0],target[1]), 20, (0,0,255), -1)
        print(target)
        print('FPS: ' + fps)
        print('True: ', true_positive , '          ' , 'False: ' , false_positive, '           ', 'Failed: ', failed)

        # out.write(temp1)

        # if x in [2000, 2001]: cv2.imshow('frame', image)
        cv2.imshow('frame', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("test end")
