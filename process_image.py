# Author: Wenchen Zhang

import numpy as np
import cv2


class TraditionalDetection:
    def __init__(self):
        self.tracker = None
        self.is_tracking = False

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

    def load_image(self, file_path, file_name, width=640, height=480):

        # load the image with picture's name and path
        image = cv2.imread(file_path + file_name)

        if image is not None:
            # resize to specific resolution
            image = cv2.resize(image, (width, height))
            return image
        else:
            print("image not loaded")


    #convert pic to binary
    def rgb_select(self, image, color):
        if color == 'b':
            thresh=(110, 255)
            color_channel = image[:,:,0]
        elif color == 'r':
            color_channel = image[:,:,2]
            thresh=(70, 255)
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
            if (area > 30)and(area<1600) and (len(i)>=5):

                ellipse = cv2.fitEllipse(i)
                # remove really large ellipse, which probaly is fasle positive, like a refelction from wall
                # also ellipse width is less than 10
                if((ellipse[1][0]*ellipse[1][1]) < 1700) and (ellipse[1][0] < 35 ):

                    all_element_list.append(ellipse)

                ################
                    # cv2.ellipse(temp,ellipse,(255,0,222),1) # draw contours to pic "temp"



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
    def get_pairs(self, pairs, all_element_list):

        ellipse_center_list = []

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
                    # x distance between centers inrange 60,300 and y centers 0,80,
                    # also height/distance need  to less than 2, incase false positive : two small ellipse with long distance
                    if (     abs(int(xcenter_i-xcenter_j)) in range(30,200)     )   and   (     abs(int(ycenter_i-ellipse_j[0][1]) ) in range(0,45)    )   and   (  (abs(xcenter_i-xcenter_j)  / ((height_i + height_j)) ) < 3  ):
                        # length two ellipse's semi axes are similar, ie the height is similar
                        if(abs(int(height_i-height_j)) < 13) or ((abs(int(height_i-height_j)) in range (7,13) ) and int(height_i+height_j)<44 ) :

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
                                # cv2.ellipse(temp,ellipse_i,(200,200,200),2)
                                # cv2.ellipse(temp,ellipse_j,(200,200,200),2)


        # check no other light in between
        # silly function not very useful,
        # can be deleted for less run time
        ellipse_center_list = list(set(ellipse_center_list))
        for i in pairs:
            light_in_between = (((((e[0])>i[0][0][0] and e[1]>i[0][0][1]) and (e[0]<i[1][0][0] and e[1] < i[1][0][1])) or ((e[0]<i[0][0][0] and e[1]<i[0][0][1]) and (e[0]>i[1][0][0] and e[1] > i[1][0][1]))) for e in ellipse_center_list)
            if any(light_in_between):
                pairs.remove(i)


        return pairs


    # limit to only one pair, by area two ellipse contains
    # choose the pair that have the biggest area
    # get the mid point coordinate between two ellipse centers in a pair
    # return the mid points' coor in aim_list
    # ellipse--> ((xc,yc),(a,b),theta)
            #xc : x coordinate of the center
            # yc : y coordinate of the center
            # a : width
            # b : height
            # theta : rotation angle
    def get_aim(self, aim_list, pairs):

        # maxArea use two ellise height^2 * x distance
        # height gain more weight in deciding the final aim
        maxArea = 0
        x =0
        y =0
        for i in pairs:
            targetArea = (abs(i[0][0][0]-i[1][0][0])*(i[0][1][1]*i[1][1][1])*(i[0][1][1]*i[1][1][1]))
            if maxArea < targetArea:
                maxArea = targetArea
                x = int((i[0][0][0]+i[1][0][0])/2)
                y = int((i[0][0][1]+i[1][0][1])/2)
        aim =(x,y)
        aim_list.append(aim)

        return aim_list

    # enhanced method to get aiming, when no pair had returned from get paired
    # use one single light to get an approxmate target
    # get the ellipse with biggest height
    # return target's coor in aim_list
    def enhanced_get_aim(self, aim_list, all_element_list):
        ellipse_list = []
        for i in all_element_list:
            if int(i[-1]) not in range(20,165):
                ellipse_list.append(i)

        if len(ellipse_list) == 0:
            return aim_list

        if len(ellipse_list)>1:
            maxlength = 0
            for i in ellipse_list:
                if maxlength < i[1][1]:
                    maxArea = i[1][1]
                    if i[-1] < 90:
                        elp_center = (i[0][0]-20, i[0][1]-10)
                    else:
                        elp_center = (i[0][0]+20, i[0][1]-10)

        else:
            if ellipse_list[0][-1] < 90:
                elp_center = (ellipse_list[0][0][0]-20, ellipse_list[0][0][1]-10)
            else:
                elp_center = (ellipse_list[0][0][0]+20, ellipse_list[0][0][1]-10)

        target = (int(elp_center[0]),int(elp_center[1]))
        aim_list.append(target)

        return aim_list


    # function to get long distance target
    # take original pic and choosen color as input (same as proccessImage),
    # direct return the aim_list
    def long_distance_get_aim(self, image, color):

        aim = []
        # with a really low thresh
        if color == 'b':
            thresh=(95, 255)
            color_channel = image[:,:,0]
        elif color == 'r':
            color_channel = image[:,:,2]
            thresh=(99, 255)
        binary_output = np.zeros_like(color_channel)
        binary_output[(color_channel > thresh[0]) & (color_channel <= thresh[1])] = 1

        im2, contours, hierarchy = cv2.findContours(binary_output,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)



    #   fit all contours as a cycle, save required cycle in cycle_list
        cycle_list = []
        aim = []
        bigest_area = 0
        biggestCycleCenter=(-1,-1)

        for i in contours:
            area = cv2.contourArea(i)

    #         print('area: ',area)
            if (area > 4) and (area < 150):

                # cycles = cv2.minEnclosingCircle(i)
                (x,y),radius = cv2.minEnclosingCircle(i)


    #         remove the biggest cycle and smallest
                if (radius < 14) and (radius > 1.8):
                    cycle_list.append([(x,y),radius])

                    # get the biggest area cycle,
                    # then save its center coor, use it as aim target when no pair formed
                    if bigest_area < area:
                        bigest_area = area
                        biggestCycleCenter = (int(x),int(y))



    #    pair up the cycles in cycle_list
        pairs = []
        itr = len(cycle_list)-1
        for i in range(0, itr):
            for j in range(i+1,itr+1):
                radius_i = cycle_list[i][1]
                radius_j = cycle_list[j][1]
    #             print("radius_j: ",radius_j)
                center_i = (int(cycle_list[i][0][0]),int(cycle_list[i][0][1]))
                center_j = (int(cycle_list[j][0][0]),int(cycle_list[j][0][1]))
    #             print("center_j: ",center_j)
                dist = abs(center_i[0]-center_j[0])+abs(center_i[1]-center_j[1])

        # similar radius and proper distance and not in the same vertical line
                if (abs(radius_i-radius_j)<1.8) and ((dist > 10) and (dist < 50)) and (abs(center_i[0]-center_j[0]) > 10):

                    # cv2.circle(temp,center_i,int(radius_i),(222,255,222),1)
                    # cv2.circle(temp,center_j,int(radius_j),(222,255,222),1)
                    midpoint = (int(0.5*(center_i[0]+center_j[0])),int(0.5*(center_i[1]+center_j[1])))
                    pairs.append([cycle_list[i],cycle_list[j],midpoint])

        # print("pairs: ",pairs)
        if len(pairs) >1:
            tempSumRadius = 0

            for i in pairs:
                # print("i: ",i)
                sumRadius = i[0][1]+i[1][1]
                if tempSumRadius <= sumRadius:
                    tempSumRadius = sumRadius
                    tempMid = i[-1]
            aim.append(tempMid)


        elif len(pairs) == 1:
            aim.append(pairs[0][-1])


        else:
            # set the biggest cycle center as aim point, when no pair formed.
            aim.append(biggestCycleCenter)

        # print("aim: ", aim)
        return aim





    # main function for aiming target
    # input: image, from camera or from load_image
    # output: list of all targets coordinates: aim_list
    def process_image(self, image, color):

        #convert to binary pic with selected color

        rgb_binary = self.rgb_select(image, color)

        #im2: binary pic with contours drawn
        #contours: list of groups of points of contour, original contours select from binary pic
        im2, contours, hierarchy = cv2.findContours(rgb_binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # all_element_list: ellipses that passed filters(restrictions)
        all_element_list = []
        all_element_list = self.get_ellipse(all_element_list,contours)

        # list that stores all target coordinates
        aim_list = []

    #             when there is no ellipse, could be because of long distance,
    #             use a function to find target in long distance
        if len(all_element_list) == 0 :
            aim_list = self.long_distance_get_aim(image,color)
        else:
            # use list pairs to store all desired paired up ellipse
            pairs = []
            pairs = self.get_pairs(pairs,all_element_list)




        #   if pairs == none
        #   then use enhanced_get_aim method to get an approxmate target
            if len(pairs) == 0:
                aim_list = self.enhanced_get_aim(aim_list,all_element_list)
    #             when there is still no target, could be because of long distance,
    #             use a function to find target in long distance
                if len(aim_list) ==0:
                    aim_list = self.long_distance_get_aim(image,color)

            else:
                aim_list = self.get_aim(aim_list,pairs)


        # the final result
        return aim_list




#####################################
# end of program ###################
#####################################




####################
# below part for test only

if __name__ == '__main__':
    print("test: start")

    # choose light color, blue or red

    # if choose to detect blue coloe
    color = 'b'
    # if choose to detect red color
    # color = 'r'

    # pic path
    # file_path ='july1_2blue/'
    # file_path ='july1_2red/'
    # file_path ='july1_mix/'
    # file_path ='july1_high/'
    file_path ='jun28_blue/'
    # file_path ='jun28_red/'


    # make a video
    cap = cv2.VideoCapture(0)

    videoName = color + 'Output.avi'

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(videoName,fourcc, 20.0, (640,480))

    for x in range(1,5100):
        # picName = 'sentry_view' + str(x) + '.png'
        picName = 'frame' + str(x) +'.png'
        image = load_image(file_path,picName)
        temp = image.copy()
        # temp = image.copy()

        ###########################################
        # ideal output: targets' coor           ###
        all_target = process_image(image,color) ###
        ###########################################

        if len(all_target) != 0:
            # test and print target on temp pic
            for i in all_target:
                # print(all_target)
                cv2.circle(temp,(i[0],i[1]), 15, (0,0,255), -1)

        cv2.putText(temp,str(x),(200,350), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 255))
        # cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # out put pic with target drawn on
        newFileName = str(x) + '.png'
        # cv2.imwrite(newFileName,temp)
        out.write(temp)




    print("test end")
