import cv2
import csv
import numpy as np
from .tracker import EuclideanDistTracker

class VehicleCounter():
    def __init__(self, file, video_dim, fps, lineDim, threshold, showVideo, theox, theoy, thedx, thedy):
        # print(' in vehicle counter INIT')
        self.file = file
        self.video_dim = video_dim
        self.fps = fps
        self.lineDim = lineDim
        self.showVideo = showVideo
        self.tracker = EuclideanDistTracker()
        self.middle_line_position = 155
        self.up_line_position = 155 - threshold
        self.down_line_position = 155 + threshold
        self.required_class_names = []
        self.required_class_index = [2, 3, 5, 7]
        self.temp_up_list = []
        self.temp_down_list = []
        self.temp_up_list2 = []
        self.temp_down_list2 = []
        self.detected_classNames = []
        self.up_list = [0, 0, 0, 0]
        self.down_list = [0, 0, 0, 0]
        self.up_list2 = [0, 0, 0, 0]
        self.down_list2 = [0, 0, 0, 0]
        self.oxcoord = theox
        self.oycoord = theoy
        self.dxcoord = thedx
        self.dycoord = thedy
        self.ox2coord = 389
        self.oy2coord = 140
        self.dx2coord = 539
        self.dy2coord = 206
        # self.ox2coord = theox2
        # self.oy2coord = theoy2
        # self.dx2coord = thedx2
        # self.dy2coord = thedy2
        # print('printing the x')
        # print(self.oxcoord)

    def find_center(self, x, y, w, h):
        # print('in find_center')
        x1 = int(w/2)
        y1 = int(h/2)
        cx = x+x1
        cy = y+y1
        return cx, cy

    def postProcess(self, outputs, img):
        # Function for finding the detected objects from the network output
        # print(' in post process')
        np.random.seed(42)
        confThreshold = 0.2
        nmsThreshold = 0.2
        classesFile = "D:/video/model/coco.names"
        classNames = open(classesFile).read().strip().split('\n')
        colors = np.random.randint(0, 255, size=(
            len(classNames), 3), dtype='uint8')
        height, width = img.shape[:2]
        # print('heigt width')
        # print(height, width)
        boxes = []
        classIds = []
        confidence_scores = []
        detection = []

        for output in outputs:
            for det in output:
                scores = det[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if classId in self.required_class_index:
                    if confidence > confThreshold:
                        # print(classId)
                        w, h = int(det[2]*width), int(det[3]*height)
                        x, y = int((det[0]*width)-w /
                                   2), int((det[1]*height)-h/2)
                        boxes.append([x, y, w, h])
                        classIds.append(classId)
                        confidence_scores.append(float(confidence))

        # Apply Non-Max Suppression
        indices = cv2.dnn.NMSBoxes(
            boxes, confidence_scores, confThreshold, nmsThreshold)
        # print('the indice is ', indices)

        try:
            indices.flatten()

        except:
            NameError

        else:
            for i in indices.flatten():
                x, y, w, h = boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]
                # print('the indiceXX is ', indices)
                color = [int(c) for c in colors[classIds[i]]]
                name = classNames[classIds[i]]
                self.detected_classNames.append(name)
                # Draw classname and confidence score

                cv2.putText(img, f'{name.upper()} {int(confidence_scores[i]*100)}%',
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                # Draw bounding rectangle
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
                detection.append(
                    [x, y, w, h, self.required_class_index.index(classIds[i])])

        # Update the tracker for each object
        boxes_ids = self.tracker.update(detection)
        for box_id in boxes_ids:
            self.count_vehicle(box_id, img)
            # print (box_id)

    def start(self):
        # print('in start')
        cap = cv2.VideoCapture(self.file)
        font_color = (0, 0, 255)
        font_size = 0.5
        font_thickness = 2
        # Model Files
        modelConfiguration = 'D:/video/model/yolov3-320.cfg'
        modelWeigheights = 'D:/video/model/yolov3-320.weights'

        # configure the network model
        net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeigheights)

        # Configure the network backend

        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        while True:
            success, img = cap.read()

            img = cv2.resize(img, (0, 0), None, .5, .5)

            ih, iw, channels = img.shape
            blob = cv2.dnn.blobFromImage(
                img, 1 / 255, (320, 320), [0, 0, 0], 1, crop=False)

            # Set the input of the network
            net.setInput(blob)
            layersNames = net.getLayerNames()
            outputNames = [(layersNames[i - 1])
                           for i in net.getUnconnectedOutLayers()]
            # Feed data to the network
            outputs = net.forward(outputNames)

            # Find the objects from the network output
            self.postProcess(outputs, img)

            # print('coords')
            # print(self.oxcoord)

            # from pt2, pt1, pt3, pt4
            cv2.line(img, (self.oxcoord, self.oycoord),
                     (self.dxcoord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.oxcoord, self.oycoord),
                     (self.dxcoord, self.oycoord), (187, 0, 255), 2)
            cv2.line(img, (self.dxcoord, self.oycoord),
                     (self.dxcoord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.dxcoord, self.dycoord),
                     (self.oxcoord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.oxcoord, self.dycoord),
                     (self.oxcoord, self.oycoord), (187, 0, 255), 2)

            cv2.line(img, (self.ox2coord, self.oycoord),
                     (self.dx2coord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.ox2coord, self.oycoord),
                     (self.dx2coord, self.oycoord), (187, 0, 255), 2)
            cv2.line(img, (self.dx2coord, self.oycoord),
                     (self.dx2coord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.dx2coord, self.dycoord),
                     (self.ox2coord, self.dycoord), (187, 0, 255), 2)
            cv2.line(img, (self.ox2coord, self.dycoord),
                     (self.ox2coord, self.oycoord), (187, 0, 255), 2)

            # Draw the crossing lines
            # cv2.line(img, (0, self.middle_line_position), (iw, self.middle_line_position), (255, 0, 255), 2)
            # cv2.line(img, (0, self.middle_line_position), (iw, self.middle_line_position), (255, 0, 255), 2)
            # cv2.line(img, (0, self.up_line_position), (iw, self.up_line_position), (0, 0, 255), 2)
            # cv2.line(img, (0, self.down_line_position), (iw, self.down_line_position), (0, 0, 255), 2)

            # Draw counting texts in the frame
            cv2.putText(img, "Up", (110, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        font_size, font_color, font_thickness)
            cv2.putText(img, "Down", (160, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        font_size, font_color, font_thickness)
            cv2.putText(img, "Up2", (210, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        font_size, font_color, font_thickness)
            cv2.putText(img, "Down2", (260, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        font_size, font_color, font_thickness)

            cv2.putText(img, "Car:        "+str(self.up_list[0])+"     " + str(self.down_list[0])+"     " + str(
                self.up_list[0])+"     " + str(self.down_list[0]), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
            cv2.putText(img, "Motorbike:  "+str(self.up_list[1])+"     " + str(self.down_list[1])+"     " + str(
                self.up_list[1])+"     " + str(self.down_list[1]), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
            cv2.putText(img, "Bus:        "+str(self.up_list[2])+"     " + str(self.down_list[2])+"     " + str(
                self.up_list[2])+"     " + str(self.down_list[2]), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
            cv2.putText(img, "Truck:      "+str(self.up_list[3])+"     " + str(self.down_list[3])+"     " + str(
                self.up_list[3])+"     " + str(self.down_list[3]), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)

            # Show the frames
            cv2.imshow('Output', img)

            if cv2.waitKey(1) == ord('q'):
                break

        # print("Data saved at 'data.csv'")
        # Finally realese the capture object and destroy all active windows
        cap.release()
        cv2.destroyAllWindows()

    def count_vehicle(self, box_id, img):
        # print('in count-vehicle')
        x, y, w, h, id, index = box_id

        # Find the center of the rectangle for detection
        center = self.find_center(x, y, w, h)
        ix, iy = center

        # slope =  (self.dycoord - self.oycoord) / ( self.dxcoord - self.oxcoord)

        # print("slope is", slope)

        # liney = self.oycoord +  ( self.dxcoord - self.oxcoord) * (ix - self.oxcoord) /  (self.dycoord  - self.oycoord )
        slope = (self.dycoord - self.oycoord) / (self.dxcoord - self.oxcoord)
        liney = (slope * ix) - (slope * self.oxcoord) + self.oycoord

        # print('box x is ', ix, 'id is ', ID, 'dx is ', self.dxcoord, 'box y is ', iy, 'liney is ', liney)

        if (liney > iy) and (ix > self.oxcoord) and (ix < self.dxcoord) and (iy > self.oycoord) and (iy < self.dycoord):

            print('top triangle here', 'id is ', id, ' iy = ', iy, 'liney = ',
                  liney, ' ox = ', self.oxcoord, 'dx = ', self.dxcoord)
            if id not in self.temp_up_list:
                self.temp_up_list.append(id)
                print('added to up list')

        elif (liney < iy) and (ix > self.oxcoord) and (ix < self.dxcoord) and (iy > self.oycoord) and (iy < self.dycoord):
            print('bottom triangle here', 'id is ', id, ' iy = ', iy,
                  'liney = ', liney, ' ox = ', self.oxcoord, 'dx = ', self.dxcoord)
            if id not in self.temp_down_list:
                self.temp_down_list.append(id)
                print('added to down list')

        elif (liney > iy and (iy < self.oycoord) or (ix > self.dxcoord)):
            # print("above")
            if id in self.temp_down_list:
                print("an upper")
                self.temp_down_list.remove(id)
                self.up_list[index] = self.up_list[index]+1

        elif (liney < iy) and ((ix < self.oxcoord) or (iy > self.dycoord)):
            # print("below")
            if id in self.temp_up_list:
                print("an downer")
                self.temp_up_list.remove(id)
                self.down_list[index] = self.down_list[index] + 1

        # Find the current position of the vehicle
        #    car is below upline and car is above middleline
        # if (iy > self.up_line_position) and (iy < self.middle_line_position):

        #   if id not in self.temp_up_list:
        #        self.temp_up_list.append(id)
        #   car is above down line and car is below middle line

        # elif iy < self.down_line_position and iy > self.middle_line_position:
        #   if id not in self.temp_down_list:
        #       self.temp_down_list.append(id)

        # elif iy < self.up_line_position:
        #    if id in self.temp_down_list:
        #        self.temp_down_list.remove(id)
        #        self.up_list[index] = self.up_list[index]+1

        # elif iy > self.down_line_position:
        #    if id in self.temp_up_list:
        #        self.down_list[index] = self.down_list[index] + 1

        # New way is to find the cross product, turn line and point into two vectors

        # y1 = self.lineDim[0][1]
        # x2 =  self.lineDim[1][0]
        # y2 = self.lineDim[1][1]
        # xA = ix
        # yA = iy
        # v1 = (x1 - x2,y2-y1)
        # v2 = (x2-xA , y2-yA )
        # xp = v1[0] * v2[1] - v1[1] * v2[0]
        # if(xp > 0):
        #    print('left of line')
        # if(xp < 0):
        #     print('right of line')
        # else:
        #     print('on the line')

        # Draw circle in the middle of the rectangle
        cv2.circle(img, center, 2, (0, 0, 255), -1)  # end here


# Initialize the videocapture object
# cap = cv2.VideoCapture('C:/Program Files (x86)/Projects/CADSR/VehicleDetection/raw_video/movie2corel.mp4')
# input_size = 320

# Detection confidence threshold
# confThreshold =0.2
# nmsThreshold= 0.2

# font_color = (0, 0, 255)
# font_size = 0.5
# font_thickness = 2

# Middle cross line position
# middle_line_position = 125
# up_line_position = middle_line_position - 15
# down_line_position = middle_line_position + 15


# Store Coco Names in a list
# classesFile = "C:/Program Files (x86)/Projects/CADSR/VehicleDetection/model/coco.names"
# classNames = open(classesFile).read().strip().split('\n')
# print(classNames)
# print(len(classNames))

# class index for our required detection classes
# required_class_index = [2, 3, 5, 7]

# detected_classNames = []

# ## Model Files
# modelConfiguration = 'C:/Program Files (x86)/Projects/CADSR/VehicleDetection/model/yolov3-320.cfg'
# modelWeigheights = 'C:/Program Files (x86)/Projects/CADSR/VehicleDetection/model/yolov3-320.weights'

# # configure the network model
# net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeigheights)

# # Configure the network backend

# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Define random colour for each class
# np.random.seed(42)
# colors = np.random.randint(0, 255, size=(len(classNames), 3), dtype='uint8')


# Function for finding the center of a rectangle
# def find_center(x, y, w, h):
#     x1=int(w/2)
#     y1=int(h/2)
#     cx = x+x1
#     cy=y+y1
#     return cx, cy

# List for store vehicle count information
# temp_up_list = []
# temp_down_list = []
# up_list = [0, 0, 0, 0]
# down_list = [0, 0, 0, 0]

# # Function for count vehicle
# def count_vehicle(box_id, img):

#     x, y, w, h, id, index = box_id

#     # Find the center of the rectangle for detection
#     center = find_center(x, y, w, h)
#     ix, iy = center

#     # Find the current position of the vehicle
#     if (iy > up_line_position) and (iy < middle_line_position):

#         if id not in temp_up_list:
#             temp_up_list.append(id)

#     elif iy < down_line_position and iy > middle_line_position:
#         if id not in temp_down_list:
#             temp_down_list.append(id)

#     elif iy < up_line_position:
#         if id in temp_down_list:
#             temp_down_list.remove(id)
#             up_list[index] = up_list[index]+1

#     elif iy > down_line_position:
#         if id in temp_up_list:
#             temp_up_list.remove(id)
#             down_list[index] = down_list[index] + 1

#     # Draw circle in the middle of the rectangle
#     cv2.circle(img, center, 2, (0, 0, 255), -1)  # end here


# def realTime():
#     while True:
#         success, img = cap.read()
#         print(cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_WIDTH) )

#         img = cv2.resize(img,(0,0),None,.5,.5)

#         ih, iw, channels = img.shape
#         blob = cv2.dnn.blobFromImage(img, 1 / 255, (320,320), [0, 0, 0], 1, crop=False)

#         # Set the input of the network
#         net.setInput(blob)
#         layersNames = net.getLayerNames()
#         outputNames = [(layersNames[i - 1]) for i in net.getUnconnectedOutLayers()]
#         # Feed data to the network
#         outputs = net.forward(outputNames)

#         # Find the objects from the network output
#         postProcess(outputs,img)


#         # Draw the crossing lines
#         cv2.line(img, (0, middle_line_position), (iw, middle_line_position), (255, 0, 255), 2)
#         cv2.line(img, (0, up_line_position), (iw, up_line_position), (0, 0, 255), 2)
#         cv2.line(img, (0, down_line_position), (iw, down_line_position), (0, 0, 255), 2)

#         # Draw counting texts in the frame
#         cv2.putText(img, "Up", (110, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#         cv2.putText(img, "Down", (160, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#         cv2.putText(img, "Car:        "+str(up_list[0])+"     "+ str(down_list[0]), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#         cv2.putText(img, "Motorbike:  "+str(up_list[1])+"     "+ str(down_list[1]), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#         cv2.putText(img, "Bus:        "+str(up_list[2])+"     "+ str(down_list[2]), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#         cv2.putText(img, "Truck:      "+str(up_list[3])+"     "+ str(down_list[3]), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)

#         # Show the frames
#         cv2.imshow('Output', img)

#         if cv2.waitKey(1) == ord('q'):
#             break

#     # Write the vehicle counting information in a file and save it

#     with open("data.csv", 'w') as f1:
#         cwriter = csv.writer(f1)
#         cwriter.writerow(['Direction', 'car', 'motorbike', 'bus', 'truck'])
#         up_list.insert(0, "Up")
#         down_list.insert(0, "Down")
#         cwriter.writerow(up_list)
#         cwriter.writerow(down_list)
#     f1.close()
#     # print("Data saved at 'data.csv'")
#     # Finally realese the capture object and destroy all active windows
#     cap.release()
#     cv2.destroyAllWindows()

# image_file = 'vehicle classification-image02.png'

# def from_static_image(image):
#     img = cv2.imread(image)
#     blob = cv2.dnn.blobFromImage(img, 1 / 255, (input_x, input_y), [0, 0, 0], 1, crop=False)
#     # Set the input of the network
#     net.setInput(blob)
#     layersNames = net.getLayerNames()
#     outputNames = [(layersNames[i[0] - 1]) for i in net.getUnconnectedOutLayers()]
#     # Feed data to the network
#     outputs = net.forward(outputNames)

#     # Find the objects from the network output
#     postProcess(outputs,img)

#     # count the frequency of detected classes
#     frequency = collections.Counter(detected_classNames)
#     print(frequency)
#     # Draw counting texts in the frame
#     cv2.putText(img, "Car:        "+str(frequency['car']), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#     cv2.putText(img, "Motorbike:  "+str(frequency['motorbike']), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#     cv2.putText(img, "Bus:        "+str(frequency['bus']), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
#     cv2.putText(img, "Truck:      "+str(frequency['truck']), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)


#     cv2.imshow("image", img)

#     cv2.waitKey(0)

#     # save the data to a csv file
#     with open("static-data.csv", 'a') as f1:
#         cwriter = csv.writer(f1)
#         cwriter.writerow([image, frequency['car'], frequency['motorbike'], frequency['bus'], frequency['truck']])
#     f1.close()


# if __name__ == '__main__':
#     realTime()
#     # from_static_image(image_file)
