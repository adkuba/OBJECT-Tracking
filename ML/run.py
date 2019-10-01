#------------------------------
#add following when you have errors with Nvidia GPU, works for me
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = True  # to log device placement (on which device the operation ran)
                                    # (nothing gets printed in Jupyter, only if you run it standalone)
sess = tf.Session(config=config)
set_session(sess)  # set this TensorFlow session as the default session for Keras

#------------------------------
#tensorflow lite model
import numpy as np
import tensorflow as tf
from cv2 import cv2
import time

interpreter = tf.lite.Interpreter(model_path = 'l_detect.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

cap = cv2.VideoCapture("VID1_15fps.mp4")
while cv2.waitKey(1) < 0:
  times = time.time()
  hasFrame, frame = cap.read()
  if not hasFrame:
    print("Done processing !!!")
    break

  frame = cv2.resize(frame, (300, 300))
  frameo = frame.copy()
  frame = np.expand_dims(frame, axis=0)
  frame = (2.0 / 255.0) * frame - 1.0
  frame = frame.astype('float32')

  interpreter.set_tensor(input_details[0]['index'], frame)
  interpreter.invoke()

  boxes = interpreter.get_tensor(
  output_details[0]['index'])
  classes = interpreter.get_tensor(
  output_details[1]['index'])
  scores = interpreter.get_tensor(
  output_details[2]['index'])
  num = interpreter.get_tensor(
  output_details[3]['index'])
  
  for id, i in enumerate(scores[0]):
    if i < 0:
      break
    if i > 0.5:
      pt1 = (int(boxes[0][id][1]*300), int(boxes[0][id][0]*300))
      pt2 = (int(boxes[0][id][3]*300), int(boxes[0][id][2]*300))
      cv2.rectangle(frameo, pt1, pt2, (0, 255, 0), 2)

  cv2.imshow("lite", frameo)  
  timee = time.time()
  print(timee-times)

#------------------------------
#object detection boxes
import numpy as np
import os, sys
import tensorflow as tf
from cv2 import cv2

cap = cv2.VideoCapture("/home/kuba/Videos/carVID/15FPS/1.mp4")
MODEL_NAME = '/home/kuba/Desktop/ssdlite_mobilenet_v2_coco_2018_05_09'
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in ['num_detections', 'detection_boxes', 'detection_scores','detection_classes', 'detection_masks']:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
      image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
      output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})

      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict

while cv2.waitKey(1) < 0:
  hasFrame, frame = cap.read()
  frame = cv2.resize(frame, (600,400))
  if not hasFrame:
    print("Done processing !!!")
    break
  
  output_dict = run_inference_for_single_image(frame, detection_graph)
  print(output_dict)
  cv2.imshow('object detection', frame)
  cv2.waitKey(0)

#------------------------------
#object detection mask
import tensorflow as tf 
import numpy as np
from cv2 import cv2

MODEL_NAME = '/home/kuba/Documents/gitfolders/Tracking_python_data/mask_net/mask_rcnn_inception_v2_coco'
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
image_path = '/home/kuba/Downloads/2.jpg'
imgcv2 = cv2.imread(image_path)

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
     serialized_graph = fid.read()
     od_graph_def.ParseFromString(serialized_graph)
     tf.import_graph_def(od_graph_def, name='')

def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [ 'num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks' ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
            output_dict = sess.run(tensor_dict, feed_dict={image_tensor: image})
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.int64)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            output_dict['detection_masks'] = output_dict['detection_masks'][0]
            print(output_dict['num_detections']) 
            return output_dict

image_np_expanded = np.expand_dims(imgcv2, axis=0)
output = run_inference_for_single_image(image_np_expanded, detection_graph)

chunksize = 40
size = chunksize*15
sizem = 1000
imgcv2 = cv2.resize(imgcv2, (sizem, sizem))

for idx, wynik in enumerate(output['detection_scores']):
    if wynik > 0.9:
        if output['detection_classes'][idx] != -1: #car - 3, 19 - horse, 1 - human
            print("indeks: {}".format(output['detection_classes'][idx]))
            box = output['detection_boxes'][idx]
            ymin = int(box[0] * sizem)
            ymax = int(box[2] * sizem)
            xmin = int(box[1] * sizem)
            xmax = int(box[3] * sizem)
            boximg = imgcv2[ymin:ymax, xmin:xmax] #0:2 1:3
            boximg = cv2.resize(boximg, (size, size))
            boxmask = np.zeros(shape=[size, size, 3], dtype=np.uint8)
            cv2.imshow(str(idx), boximg)
            cv2.waitKey(0)
            fromy = 1
            for line in output["detection_masks"][idx]:
                fromx = 1
                for val in line:
                    if val > 0.8:
                        boxmask[fromy:fromy+chunksize, fromx:fromx+chunksize] = boximg[fromy:fromy+chunksize, fromx:fromx+chunksize]
                    fromx += chunksize
                fromy += chunksize
            cv2.imshow(str(idx)+"mask", boxmask)
            cv2.waitKey(0)
    else:
        break

#------------------------------
#object classifier

import numpy as np
import tensorflow as tf
from cv2 import cv2
import time

labels = open('output_labels.txt', 'r')
interpreter = interpreter = tf.lite.Interpreter(model_path = 'classify.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

times = time.time()
image = cv2.imread('img1.jpg')
imagec = cv2.resize(image, (192, 192))
imagec = np.expand_dims(imagec, axis=0)
imagec = (2.0 / 255.0) * imagec - 1.0
imagec = imagec.astype('float32')

interpreter.set_tensor(input_details[0]['index'], imagec)
interpreter.invoke()
scores = interpreter.get_tensor(
    output_details[0]['index'])

timee = time.time()
print("Time: {}".format(timee-times))
labels_list = labels.read().splitlines()
scores_list = [j for i in scores for j in i]
for wyn in sorted(scores_list)[::-1]:
    print("{}: {}".format(labels_list[scores_list.index(wyn)], wyn))
cv2.imshow("Image", image)
cv2.waitKey(0)