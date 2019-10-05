//
//  OpenCVWrapper.h
//  CamTracking2
//
//  Created by Jakub Adamski on 07/09/2018.
//  Copyright © 2018 Jakub Adamski. All rights reserved.
//  connection swift - cpp

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

@interface OpenCVWrapper : NSObject

+ (NSString *)openCVVersionString;

- (UIImage *) trackerstart: (UIImage *) image;

- (UIImage *) inittracker: (UIImage *) image;

- (int) miejsce;

- (void) start: (UIImage *) image;

- (void) frameinicx: (int) rectx;

- (void) frameinicy: (int) recty;

- (void) frameinicw: (int) rectw;

- (void) frameinich: (int) recth;

- (void) trackerreset;

@end
