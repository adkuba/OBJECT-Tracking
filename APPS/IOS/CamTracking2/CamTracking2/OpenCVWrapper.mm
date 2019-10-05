//
//  OpenCVWrapper.m
//  CamTracking2
//
//  Created by kuba on 07/09/2018.
//  Copyright © 2018 kuba. All rights reserved.
//

#import "OpenCVWrapper.h"
#import <opencv2/opencv.hpp>
#import <opencv2/core.hpp>
#import <opencv2/imgcodecs/ios.h>
#import <opencv2/tracking.hpp>
#import <opencv2/imgproc/imgproc.hpp>


using namespace cv;
using namespace std;

@implementation OpenCVWrapper

Rect2d bbox;
Ptr<Tracker> tracker = TrackerKCF::create();
int w, h;
int procent;
int xf = 200;
int yf = 300;
int widthf = 500;
int heightf = 500;
int scale = 3;

void recscale () {
    bbox.x *= scale;
    bbox.y *= scale;
    bbox.width *= scale;
    bbox.height *= scale;
}

+ (NSString *)openCVVersionString {
    
    return [NSString stringWithFormat:@"OpenCV Version %s",  CV_VERSION];
}

- (void) start: (UIImage *) image {
    Mat startf; UIImageToMat(image, startf);
    w = startf.size().width/ scale;
    h = startf.size().height/ scale;
}

- (UIImage *) inittracker:  (UIImage *) image {
    Mat initframe; UIImageToMat(image, initframe);
    Mat grayr; resize(initframe, grayr, cv::Size(w, h));
    cvtColor(grayr, grayr, CV_BGR2GRAY);
    bbox.x = xf;
    bbox.y = yf;
    bbox.width = widthf;
    bbox.height = heightf;
    tracker->init(grayr, bbox);
    recscale();
    rectangle(initframe, bbox, Scalar( 255, 0, 0 ), 2, 1 );
    return MatToUIImage(initframe);
}

- (void) trackerreset {
    tracker->clear();
    tracker = TrackerKCF::create();
}

- (void) frameinicx: (int) rectx{
    xf = w * rectx /100;
}

- (void) frameinicy: (int) recty{
    yf = h * recty /100;
}

- (void) frameinicw: (int) rectw{
    widthf = w * rectw /100;
}

- (void) frameinich: (int) recth{
    heightf = h * recth /100;
}

- (UIImage *) trackerstart: (UIImage *) image {
    
    Mat frame; UIImageToMat(image, frame);
    Mat res_frame; resize(frame, res_frame, cv::Size(w, h));
    cvtColor(res_frame, res_frame, CV_BGR2GRAY);
    // Define initial bounding box
    
    // Uncomment the line below to select a different bounding box
    // bbox = selectROI(frame, false);
    // Display bounding box.
    
        // Update the tracking result
        bool ok = tracker->update(res_frame, bbox);
        procent = (bbox.x + bbox.width/2) *100 / w;
        recscale();
    
        if (ok)
        {
            // Tracking success : Draw the tracked object
            rectangle(frame, bbox, Scalar( 255, 0, 0 ), 2, 1 );
        }
        else {
            procent = 50;
        }
    
    
    return MatToUIImage(frame);
}

- (int) miejsce {
    return procent;
}

@end
