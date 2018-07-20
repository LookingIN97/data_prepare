import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt

class TraditionalDetection:
    def __init__(self):
        self.tracker = None
        self.is_tracking = False
        self.image = None
        self.frame_counter = 0
        self.stop_tracking = 25

    def tracker_creation(self, frame, bbox, n=2):
        tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        tracker_type = tracker_types[n]
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        success = tracker.init(frame, bbox)
        return tracker

    # def tracking(self, tracker, frame):
    #     success, bbox = tracker.update(frame)
    #     # if success:
    #     #     # Tracking success
    #     #     p1 = (int(bbox[0]), int(bbox[1]))
    #     #     p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    #     #     # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
    #     # else:
    #     #     # Tracking failure
    #     #     cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    #
    #     return success, bbox

    def load_image(self, file_path,file_name):

        # load the image with picture's name and path
        image = cv2.imread(file_path + file_name)

        if image is not None:
            return image
        else:
            print("image not loaded")

    #convert pic to binary
    def rgb_select(self, image, color):
        if color == 'r':
            thresh=(170, 255)
            color_channel = image[:,:,2]
        elif color == 'b':
            color_channel = image[:,:,0]
            thresh=(66, 255)
        binary_output = np.zeros_like(color_channel)
        binary_output[(color_channel > thresh[0]) & (color_channel <= thresh[1])] = 1
        return binary_output


    # filter 1
    # input list to store required ellipse, all contours from image
    # only choose contours' area that are greater than 40
    # fitEllipse
    # will return a rotated rect
    # ellipse--> ((xc,yc),(a,b),theta)
            #xc : x coordinate of the center
            # yc : y coordinate of the center
            # a : width
            # b : height
            # theta : rotation angle
    # output list that stored required ellipse
    def get_ellipse(self, all_element_list,contours):


        for i in contours:

            area = cv2.contourArea(i)
            if area > 50:
                ellipse = cv2.fitEllipse(i)
                all_element_list.append(ellipse)
        # list of ellipses which area are greater than
        return all_element_list





    def slope(self, x1, y1, x2, y2):
        return (y2-y1)/(x2-x1)



    # pair up ellipses
    # input: list to store required pairs, list of ellipse that pass perivous fileter
    # output: list of pairs of ellipses
    # [(elp1,elps2),(elps3,elps4)....]
    # ellipses have similar width that are similar, within 5
    # ellipses have similar rotation angle: after substraction, within -5,5 or not in -175,175
    # ellipses x distances are in range of (60,300)
    def get_pairs(self, all_element_list):
        ellipse_center_list = []
        pairs = []

        itr = len(all_element_list)-1
        for i in range(0, itr):
            for j in range(i+1,itr+1):
                ellipse_i = all_element_list[i]
                ellipse_j = all_element_list[j]
                angle_i = ellipse_i[2]
                angle_j = ellipse_j[2]
                xcenter_i = ellipse_i[0][0]
                xcenter_j = ellipse_j[0][0]
                ycenter_i = ellipse_i[0][1]
                ycenter_j = ellipse_j[0][1]
                height_i = ellipse_i[1][1]
                height_j = ellipse_j[1][1]

                # angle within 5 degree
                if (int(angle_i-angle_j) in range(-10,10)) or (int(angle_i-angle_j) not in range(-170,170)):
                    # x distance between centers inrange 60,300 and y centers 0,80
                    if (abs(int(xcenter_i-xcenter_j)) in range(30,150)) and (abs(int(ycenter_i-ellipse_j[0][1]) ) in range(0,40) ):
                        # length two ellipse's semi axes are similar, ie the height is similar
                        if(abs(int(height_i-height_j)) < 12) or ((abs(int(height_i-height_j)) in range (7,12) ) and int(height_i+height_j)<45 ) :

                            # the paired up ellipse's rotation angle should not be similar to their centers' connection's slope
                            # (to avoid false positive when two lights are on the same line)
                            # slpoe of line that connected two ellipse's connection
                            slp = self.slope(xcenter_i,ycenter_i,xcenter_j,ellipse_j[0][1])
                            # arctan will return an angle in randians times 57 convert to degree.
                            # and plus 90 to change axis as photo's origin is at top left but the slope's origin is at left bottom
                            deg = 90 + np.arctan(slp)*57.3
                            # difference is greater than 30 degree
                            if((abs(deg - ellipse_i[-1] ) > 30 ) and (abs(deg - ellipse_j[-1] ) > 30 )  ):
                                # add paired up ellipsee to list
                                pairs.append([ellipse_i,ellipse_j])
                                ellipse_center_list.append(ellipse_i[0])
                                ellipse_center_list.append(ellipse_j[0])
                                # cv2.ellipse(temp,ellipse_i,(200,200,200),3)
                                # cv2.ellipse(temp,ellipse_j,(200,200,200),3)


        # check no other light in between
        # dumb function not very useful,
        # can be deleted for less run time
        ellipse_center_list = list(set(ellipse_center_list))
        for i in pairs:
            light_in_between = ((((e[0])>i[0][0][0] and e[1]>i[0][0][1]) and (e[0]<i[1][0][0] and e[1] < i[1][0][1])) or ((e[0]<i[0][0][0] and e[1]<i[0][0][1]) and (e[0]>i[1][0][0] and e[1] > i[1][0][1])) for e in ellipse_center_list )
            if any(light_in_between):
                pairs.remove(i)


        return pairs

    # limit to only one pair
    # get the mid point coordinate between two ellipse centers in a pair
    # return the mid points' coor in aim_list

    def get_aim(self, pairs):

        # equal to sum of heights of ellipse in a pair
        maxSum = -1
        for i in pairs:
            x1 = i[0][0][0]
            x2 = i[1][0][0]
            y1 = i[0][0][1]
            y2 = i[1][0][1]
            area1 = i[0][1][1]
            area2 = i[1][1][1]
            if maxSum < (area1+area2):
                maxSum = area1+area2
                x = int((x1 + x2)/2)
                y = int((y1 + y2)/2)
                w = int(abs(x1 - x2) * 1.4)
                h = w * 0.5
        return [x, y, w, h]

    # enhanced method to get aiming, when no pair had returned from get paired
    # use one single light to get an approxmate target
    # return target's coor in aim_list
    def enhanced_get_aim(self, all_element_list):
        ellipse_list = []
        for i in all_element_list:
            if int(i[-1]) not in range(20,165):
                ellipse_list.append(i)
        if len(ellipse_list) == 0:
            return []
        elif len(ellipse_list)>1:
            maxArea = 0
            for i in ellipse_list:
                if maxArea < i[1][1] * i [1][0]:
                    maxArea = i[1][1] * i [1][0]
                    if i[-1] < 90:
                        elp_center = (i[0][0]-40, i[0][1]-15)
                    else:
                        elp_center = (i[0][0]+40, i[0][1]-15)
        else:
            if ellipse_list[0][-1] < 90:
                elp_center = (ellipse_list[0][0][0]-40, ellipse_list[0][0][1]-15)
            else:
                elp_center = (ellipse_list[0][0][0]+40, ellipse_list[0][0][1]-15)

        target = (int(elp_center[0]),int(elp_center[1]))

        return target




    # main function for aiming target
    # input: image, from camera or from load_image
    # output: list of all targets coordinates: aim_list
    def process_image(self, image, color):
        self.image = image
        if self.is_tracking:
            self.is_tracking, bbox = self.tracker.update(image)
            if self.is_tracking:
                self.frame_counter += 1
                x = int(bbox[0] + bbox[2] / 2)
                y = int(bbox[1] + bbox[3] / 2)
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                # print('tracking: ', bbox)
                cv2.rectangle(self.image, p1, p2, (255, 255, 255), 2, 1)
                # print('bbox: ', bbox, x, y)
                if self.frame_counter == self.stop_tracking:
                    self.frame_counter = 0
                    self.is_tracking = False
                return [x, y]

        #convert to binary pic with selected color
        rgb_binary = self.rgb_select(image, color)

        #im2: binary pic with contours drawn
        #contours: list of groups of points of contour, original contours select from binary pic
        im2, contours, hierarchy = cv2.findContours(rgb_binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # all_element_list: ellipses that passed filters(restrictions)
        all_element_list = []
        try:
            all_element_list = self.get_ellipse(all_element_list,contours)
        except:
            return [-1, -1]

        # use list pairs to store all desired paired up ellipse
        pairs = self.get_pairs(all_element_list)

    #   if pairs == none
    #   then use enhanced_get_aim method to get an approxmate target
        if len(pairs) == 0:
            try:
                [x, y] = self.enhanced_get_aim(all_element_list)
            except:
                return [-1, -1]

        else:
            [x, y, w, h] = self.get_aim(pairs)
            # self.tracker = self.tracker_creation(image, bbox=(int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)), n=1)
            # print('initial:', (int(x-w/2), int(y-h/2), int(w), int(h)))
            self.tracker = self.tracker_creation(image, bbox=(int(x-w/2), int(y-h/2), int(w), int(h)), n=2)
            self.is_tracking = True

        # the final result

        return [x, y]


#####################################
# end of program ###################
#####################################




####################
# below part for test only

if __name__ == "__main__":
    print("test: start")

    # choose light color, blue or red

    # if choose to detect blue coloe
    # color = 'b'
    # if choose to detect red color
    color = 'b'

    # pic path
    file_path ='images/'

    # list of file number's that want to test
    # y = [1,44,55,77,133,199,244,277,299,344,399,400,407,438,420,443]
    # y =[1]

    # pic path
    file_path ='jun28_blue/'

    # list of file number's that want to test
    # y = [1,44,55,77,133,199,244,277,299,344,399,400,407,438,420,443]
    # y =[1]

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc , 20.0, (640,480))

    for x in range(1,5347):
        picName = 'frame' + str(x) + '.png'
        image = load_image(file_path, picName)
        temp1 = image.copy()
        all_target = process_image(image, color)

        for i in all_target:
        # print(all_target)
            cv2.circle(temp1,(i[0],i[1]), 20, (0,0,255), -1)

        # write the flipped frame
        print(temp1.shape)
        out.write(temp1)

        cv2.imshow('frame', temp1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("test end")
