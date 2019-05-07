# USAGE
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat --video blink_detection_demo.mp4
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat

# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

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
def showPose(im,image_points):     
# 3D model points.
  model_points = np.array([
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
  camera_matrix = np.array(
                         [[focal_length, 0, center[0]],
                         [0, focal_length, center[1]],
                         [0, 0, 1]], dtype = "double"
                         )
 
#print ("Camera Matrix :",camera_matrix)
  dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
  (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE) 
#print ("Rotation Vector:",rotation_vector)
#print ("Translation Vector:",translation_vector)
# Project a 3D point (0, 0, 1000.0) onto the image plane.
# We use this to draw a line sticking out of the nose
  (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 250, 800.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
  for p in image_points:
    cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)
  p1 = ( int(image_points[0][0]), int(image_points[0][1]))
  p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
  distance=dist.euclidean(p1,p2)  
  cv2.line(im, p1, p2, (255,0,0), 2)
  return im ,distance
def get_predictor():
#
# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
  print("[INFO] loading facial landmark predictor...")
  detector = dlib.get_frontal_face_detector()
  predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
  return detector,predictor

def process_oneframe(frame,detector,predictor):
  (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
  #print(lStart)
  (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
  (mStart,mEnd)=face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
  #print(mStart,mEnd)
  #frame = cv2.imread('snapshotGrey%s.jpg'%(i),1)#read image in grey scale
	#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# detect faces in the grayscale frame
  rects = detector(frame, 0)
  detectFace=len(rects)
  ear=0
  yawningRatio=0
  distance=0
	#print(rects)
	# We now need to loop over each of the faces in the frame and 
	# then apply facial landmark detection to each of them
  for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
        shape = predictor(frame, rect)
        shape = face_utils.shape_to_np(shape)
        image_points=np.array([
			shape[30],     # Nose tip
            shape[8],     # Chin
            shape[45],     # Left eye left corner
            shape[36],     # Right eye right corne
            shape[54],     # Left Mouth corner
            shape[48]      # Right mouth corner
			],dtype='double')
        frame,distance=showPose(frame,image_points)
        print(distance)
		#print("******************************")
		# extract the left and right eye coordinates, then use the
		# coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        mouth=shape[mStart:mEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        yawningRatio=detect_yanwing(mouth)
        ear = (leftEAR + rightEAR) / 2.0
        # compute the convex hull for the left and right eye, then
		# visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        mouthHull=cv2.convexHull(mouth)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame,[mouthHull],-1,(0,255,0),)

  return ear,yawningRatio,frame,detectFace,distance
# loop over frames from the video stream
count=0
#main function
EYE_AR_THRESH = 0.27       # threshold to decide the eyes are closed
EYE_AR_CONSEC_FRAMES = 2   # number of frames that eyes are closed to determine a blink
MOUTH_YA_CONSEC_FRAMES=9   # number of frames that mouth is open to determine the driver is yawning
MOUTH_YAWNING_THRESH=0.7   # threshold to decide the mouth is open
# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0
mouthCounter=0
totalYawn=0
s=''
ear=0
i=1
detector,predictor=get_predictor()
cap=cv2.VideoCapture(0)

while True:
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale
	# channels)
	if(i>=24):
		i=1
	ret,frame=cap.read()
	ear,yawningRatio,frame,detectFace,distance=process_oneframe(frame,detector,predictor)
	i=i+1
	if yawningRatio>MOUTH_YAWNING_THRESH:
			mouthCounter+=1
	else:
			mouthCounter=0
	if mouthCounter>=MOUTH_YA_CONSEC_FRAMES:
			totalYawn+=1
			mouthCounter=0
	if ear < EYE_AR_THRESH:
			COUNTER += 1
        
		# otherwise, the eye aspect ratio is not below the blink
		# threshold
	else:
			# if the eyes were closed for a sufficient number of
			# then increment the total number of blinks
		COUNTER=0
	if COUNTER >= EYE_AR_CONSEC_FRAMES:
		TOTAL += 1

			# reset the eye frame counter
		COUNTER = 0

		# draw the total number of blinks on the frame along with
		# the computed eye aspect ratio for the frame
	if (detectFace>0):
		if(distance<150):
		   s='yes'#detect face
		else:
			s='no'
	else:
		s='no'#not detected face, looking else where
	cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.putText(frame,"yawning:{}".format(totalYawn),(10,60),
        	cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.putText(frame, "looking ahead?: {}".format(s), (300, 60),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	else:
		continue

# do a bit of cleanup
cv2.destroyAllWindows()
cap.release()
