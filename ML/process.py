#data generator using mask rcnn
#it goes frame by frame and creates single picture for frame containing combined pisctures of the same category objects
#works best with 15 fps mp4 videos 
import tensorflow as tf 
import numpy as np
from cv2 import cv2
import os

#paths
MODEL_NAME = 'mask_rcnn_inception_v2_coco'
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'
videos_folder_path = 'VID/15FPS/to_do'
processed = [ '55', '79', '53', '76', '48', '57' ] #already processed videos in folder

#loading frozen graph
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
     serialized_graph = fid.read()
     od_graph_def.ParseFromString(serialized_graph)
     tf.import_graph_def(od_graph_def, name='')

#running on single frame
def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [ 'num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks' ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
            #running
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
            output_dict = sess.run(tensor_dict, feed_dict={image_tensor: image})
            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.int64)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            output_dict['detection_masks'] = output_dict['detection_masks'][0]
            return output_dict

#scanning videos directory
for vid in os.listdir(videos_folder_path):
    cont = False
    for p in processed:
        if p in vid:
            cont = True
            break
    if cont:
        continue

    obiekty = [] #cut images
    licznikF = 1
    cap = cv2.VideoCapture(videos_folder_path + "/" + vid) #reading videos
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) #number of frames
    path = videos_folder_path + "/" + vid[:len(vid)-4] #setting path to save
    os.mkdir(path) #creating folder to save pictures
    cap.set(1, licznikF)

    #loop for current video
    while True:
        hasFrame, frame = cap.read()
        if not hasFrame:
            print("Done processing!")
            break
        
        chunksize = 14 #224/15 = 14,99
        size = 224 
        sizem = 1000
        frame = cv2.resize(frame, (sizem, sizem))

        frame_np_expanded = np.expand_dims(frame, axis=0)
        output = run_inference_for_single_image(frame_np_expanded, detection_graph)
        for idx, wynik in enumerate(output['detection_scores']):
            if wynik > 0.7: #if score is higher than 70%
                if output['detection_classes'][idx] == 3: #3 means car, see coco labels
                    box = output['detection_boxes'][idx]
                    ymin = int(box[0] * sizem)
                    ymax = int(box[2] * sizem)
                    xmin = int(box[1] * sizem)
                    xmax = int(box[3] * sizem)
                    boximg = frame[ymin:ymax, xmin:xmax] #0:2 1:3
                    boximg = cv2.resize(boximg, (211, 211)) #14*15 = 210
                    boxmask = np.zeros(shape=[size, size, 3], dtype=np.uint8)
                    fromy = 1
                    for line in output["detection_masks"][idx]:
                        fromx = 1
                        for val in line:
                            if val > 0.8: #overlaying with proper square
                                boxmask[fromy:fromy+chunksize, fromx:fromx+chunksize] = boximg[fromy:fromy+chunksize, fromx:fromx+chunksize]
                            fromx += chunksize
                        fromy += chunksize
                    obiekty.append(boxmask) #adding objects to list
            else:
                break

        #saving pictures form obiekty to one combined picture with name as frame count
        if len(obiekty) > 0:
            vis = np.zeros((224, 224*len(obiekty), 3), np.uint8) #blank img
            pixels = 0
            for ob in obiekty:
                vis[:224, pixels:pixels+224, :3] = ob #saving img
                pixels += 224
            cv2.imwrite(path + "/" + str(licznikF) + ".png", vis) #saving

        print("vid: {} -> {}/{} DONE".format(vid, licznikF, length))
        licznikF += 1
        obiekty.clear()

    cap.release()