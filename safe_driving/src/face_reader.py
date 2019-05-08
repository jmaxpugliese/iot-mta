#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import dlib
import numpy

from scipy.spatial import distance as dist
from imutils import face_utils

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold
EYE_AR_THRESH = 0.27
EYE_AR_CONSEC_FRAMES = 2
MOUTH_YA_CONSEC_FRAMES=9
MOUTH_YAWNING_THRESH=0.7

DAT_FILENAME = 'shape_predictor_68_face_landmarks.dat'

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart,mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

def eye_aspect_ratio(eye):
  # compute the euclidean distances between the two sets of
  # vertical eye landmarks (x, y)-coordinates
  A = dist.euclidean(eye[1], eye[5])
  B = dist.euclidean(eye[2], eye[4])

  # compute the euclidean distance between the horizontal
  # eye landmark (x, y)-coordinates
  C = dist.euclidean(eye[0], eye[3])

  # compute the eye aspect ratio
  ear = (A + B) / (2.0 * C)

  # return the eye aspect ratio
  return ear

def detect_yanwing(mouth):
  A=dist.euclidean(mouth[2],mouth[10])
  B=dist.euclidean(mouth[3],mouth[9])
  C=dist.euclidean(mouth[4],mouth[8])
  D=dist.euclidean(mouth[0],mouth[6])
  E=dist.euclidean(mouth[1],mouth[5])
  F=dist.euclidean(mouth[11],mouth[7])
  yanwing_ratio=(A+B+C)/(D+E+F)
  return yanwing_ratio 

def showPose(im, image_points):     
  # 3D model points.
  model_points = numpy.array([
      (0.0, 0.0, 0.0),             # Nose tip
      (0.0, -330.0, -65.0),        # Chin
      (-225.0, 170.0, -135.0),     # Left eye left corner
      (225.0, 170.0, -135.0),      # Right eye right corne
      (-150.0, -150.0, -125.0),    # Left Mouth corner
      (150.0, -150.0, -125.0)      # Right mouth corner
    
  ])
  # Camera internals
  size=im.shape
  focal_length = size[1]
  center = (size[1]/2, size[0]/2)
  camera_matrix = numpy.array(
    [[focal_length, 0, center[0]],
    [0, focal_length, center[1]],
    [0, 0, 1]], dtype = "double"
  )
  
  #print ("Camera Matrix :",camera_matrix)
  dist_coeffs = numpy.zeros((4,1)) # Assuming no lens distortion
  (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE) 

  # Project a 3D point (0, 0, 1000.0) onto the image plane.
  # We use this to draw a line sticking out of the nose
  (nose_end_point2D, jacobian) = cv2.projectPoints(numpy.array([(0.0, 250, 800.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
  for p in image_points:
    cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)
  p1 = ( int(image_points[0][0]), int(image_points[0][1]))
  p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
  distance=dist.euclidean(p1,p2)  
  cv2.line(im, p1, p2, (255,0,0), 2)

  return im ,distance

def process_frame(detector,predictor,gray_frame):
  eyes_open = True
  looking_forward = True
  distance=0
  frame = []
  # detect faces in the grayscale frame
  
  rects = detector(gray_frame, 0)
  #print(rects)
  # We now need to loop over each of the faces in the frame and 
  # then apply facial landmark detection to each of them
  if len(rects) > 0:
    for rect in rects:
      # determine the facial landmarks for the face region, then
      # convert the facial landmark (x, y)-coordinates to a NumPy
      # array
      
      shape = predictor(gray_frame, rect)
      
      shape = face_utils.shape_to_np(shape)

      image_points=numpy.array([
          shape[30],     # Nose tip
          shape[8],     # Chin
          shape[45],     # Left eye left corner
          shape[36],     # Right eye right corne
          shape[54],     # Left Mouth corner
          shape[48]      # Right mouth corner
        ], dtype='double')

      frame, distance=showPose(gray_frame, image_points)
      
      # extract the left and right eye coordinates, then use the
      # coordinates to compute the eye aspect ratio for both eyes
      leftEye = shape[lStart:lEnd]
      rightEye = shape[rStart:rEnd]
      mouth=shape[mStart:mEnd]
      leftEAR = eye_aspect_ratio(leftEye)
      rightEAR = eye_aspect_ratio(rightEye)
      yawningRatio=detect_yanwing(mouth)
      
      # average the eye aspect ratio together for both eyes
      ear = (leftEAR + rightEAR) / 2.0

      # compute the convex hull for the left and right eye, then
      # visualize each of the eyes
      leftEyeHull = cv2.convexHull(leftEye)
      rightEyeHull = cv2.convexHull(rightEye)
      mouthHull=cv2.convexHull(mouth)
      cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
      cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
      cv2.drawContours(frame,[mouthHull],-1,(0,255,0),1)

      # check to see if the eye aspect ratio is below the blink
      # threshold, and if so, increment the blink frame ounter
      # @TODO
      # if yawningRatio>MOUTH_YAWNING_THRESH:
      #   mouthCounter+=1
      # else:
      #   mouthCounter=0
      # if mouthCounter>=MOUTH_YA_CONSEC_FRAMES:
      #   totalYawn+=1
      #   mouthCounter=0

      # if lower, eyes are closed
      if ear < EYE_AR_THRESH:
        eyes_open = False
          
      # # otherwise, the eye aspect ratio is not below the blink
      # # threshold
      # else:
      #   # if the eyes were closed for a sufficient number of
      #   # then increment the total number of blinks
      #   if COUNTER >= EYE_AR_CONSEC_FRAMES:
      #     TOTAL += 1

      #   # reset the eye frame counter
      #   COUNTER = 0
      # draw the total number of blinks on the frame along with
      # the computed eye aspect ratio for the frame

  # if no rects, then looking away
  print(distance)
  if len(rects) > 0:
    if distance < 200:
      looking_forward = True
    else:
      looking_forward = False
  else:
   looking_forward = False
    
  if len(frame) > 0:
    cv2.putText(frame, "eyes open: {}".format(eyes_open), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame,"yawning:{}".format(3),(10,60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, "looking ahead?: {}".format(looking_forward), (300, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
     #show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

  return (eyes_open, looking_forward)
vc = cv2.VideoCapture(0)
vc.set(3,640)
vc.set(4,480)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(DAT_FILENAME)
while True:
    ret, frame = vc.read()
    eyes_open,looking_forward=process_frame(detector,predictor,frame)
