//
//  CameraBuffer.swift
//  CamTracking2
//
//  Created by Jakub Adamski on 07/09/2018.
//  Copyright © 2018 Jakub Adamski. All rights reserved.
//  Recording manager

import UIKit
import AVFoundation
import Photos

protocol CameraBufferDelegate: class {
    func captured(image: UIImage)
}

class CameraBuffer: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    
    weak var delegate: CameraBufferDelegate?
    let opencvWrapper = OpenCVWrapper();
    private let sessionQueue = DispatchQueue(label: "session queue")
    private let context = CIContext()
    private lazy var captureSession: AVCaptureSession = {
        let session = AVCaptureSession()
        session.sessionPreset = AVCaptureSession.Preset.high
        guard
            let backCamera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
            let Vinput = try? AVCaptureDeviceInput(device: backCamera)
            else { return session }
        session.addInput(Vinput)
        
        guard
            let microphone = AVCaptureDevice.default(for: .audio),
            let micInput = try? AVCaptureDeviceInput(device: microphone)
            else {return session}
        session.addInput(micInput)
        
        return session
    }()
    
    
    let videoOutput = AVCaptureVideoDataOutput()
    
    override init() {
        super.init()
        sessionQueue.async { [unowned self] in
            self.videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "MyQueue"))
            self.captureSession.addOutput(self.videoOutput)
            self.captureSession.startRunning()
        }
    }
    
    private func imageFromSampleBuffer(sampleBuffer: CMSampleBuffer) -> UIImage? {
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return nil }
        let ciImage = CIImage(cvPixelBuffer: imageBuffer)
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return nil }
        return UIImage(cgImage: cgImage)
    }
    
 var lastor = 1
 var trans = true
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        
        guard let uiImage = imageFromSampleBuffer(sampleBuffer: sampleBuffer) else { return }
        DispatchQueue.main.async { [unowned self] in
            self.delegate?.captured(image: uiImage)
        }
 
        let writable = canWrite()
        if writable,
            sessionAtSourceTime == nil {
            
            // start writing
            sessionAtSourceTime = CMSampleBufferGetPresentationTimeStamp(sampleBuffer)
            videoWriter.startSession(atSourceTime: sessionAtSourceTime!)
        }
        
        if output == videoOutput {
            if trans {
            switch UIDevice.current.orientation {
                
            case .landscapeRight:
                connection.videoOrientation = .landscapeLeft
                lastor = 1
                trans = false
                
            case .landscapeLeft:
                connection.videoOrientation = .landscapeRight
                lastor = 0
                trans = false
                
            case .portrait:
                if lastor == 1 {
                    connection.videoOrientation = .landscapeLeft
                    trans = false
                }
                else {
                    connection.videoOrientation = .landscapeRight
                    trans = false
                }
                
            case .portraitUpsideDown:
                if lastor == 1 {
                    connection.videoOrientation = .landscapeLeft
                    trans = false
                }
                else {
                    connection.videoOrientation = .landscapeRight
                    trans = false
                }
                
            default:
                connection.videoOrientation = .landscapeLeft
                trans = false
            }
            }
        }
    
        if writable,
            output == videoOutput,
            (videoWriterInput.isReadyForMoreMediaData) {
            // write video buffer
            videoWriterInput.append(sampleBuffer)
            
        } else if writable,
            output == audioDataOutput,
            (audioWriterInput.isReadyForMoreMediaData) {
            // write audio buffer
            audioWriterInput?.append(sampleBuffer)
            //print("audio buffering")
        }
        
    }
   
    var audioDataOutput: AVCaptureAudioDataOutput!
    var sessionAtSourceTime: CMTime!
    var videoWriterInput: AVAssetWriterInput!
    var audioWriterInput: AVAssetWriterInput!
    var videoWriter: AVAssetWriter!
    var outputFileLocation: URL!
    var isRecording = false
    
    func setUpWriter() {
        do {
            outputFileLocation = videoFileLocation()
            videoWriter = try AVAssetWriter(outputURL: outputFileLocation!, fileType: AVFileType.mov)
            
            // add video input
            videoWriterInput = AVAssetWriterInput(mediaType: AVMediaType.video, outputSettings: [
                AVVideoCodecKey : AVVideoCodecType.h264,
                AVVideoWidthKey : 1920,
                AVVideoHeightKey : 1080,
                AVVideoCompressionPropertiesKey : [
                    AVVideoAverageBitRateKey : 2300000,
                ],
                ])
            
            videoWriterInput.expectsMediaDataInRealTime = true
            
            if videoWriter.canAdd(videoWriterInput) {
                videoWriter.add(videoWriterInput)
                print("video input added")
            } else {
                print("no input added")
            }
            
            // add audio input
            audioWriterInput = AVAssetWriterInput(mediaType: AVMediaType.audio, outputSettings: nil)
            
            audioWriterInput.expectsMediaDataInRealTime = true
            
            if videoWriter.canAdd(audioWriterInput!) {
                videoWriter.add(audioWriterInput!)
            }
            
            videoWriter.startWriting()
        
        } catch let error {
            debugPrint(error.localizedDescription)
            
        }
    }
    
    func canWrite() -> Bool {
        return isRecording && videoWriter != nil && videoWriter?.status == .writing
    }
    
    //video file location method
    func videoFileLocation() -> URL {
        let outputFileName = NSUUID().uuidString
        let documentsPath = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0] as NSString
        let videoOutputUrl = URL(fileURLWithPath: documentsPath.appendingPathComponent(outputFileName)).appendingPathExtension("mov")
        do {
            if FileManager.default.fileExists(atPath: videoOutputUrl.path) {
                try FileManager.default.removeItem(at: videoOutputUrl)
            }
        } catch {
            print(error)
        }
        
        return videoOutputUrl
    }
    
    // MARK: Start recording
    func start() {
        guard !isRecording else { return }
        isRecording = true
        sessionAtSourceTime = nil
        setUpWriter()
    }
    
    // MARK: Stop recording
    var urll: URL!
    func stop() {
        guard isRecording else { return }
        isRecording = false
        videoWriterInput.markAsFinished()
        videoWriter.finishWriting { [weak self] in
            self?.sessionAtSourceTime = nil
            guard let url = self?.videoWriter.outputURL else { return }
            self?.urll = url
        }
        captureSession.stopRunning()
        captureSession.startRunning()
    }
    
    func stanrec () -> String {
        if videoWriter.status == .writing {
            return "status writing"
        } else if videoWriter.status == .failed {
            return "status failed"
        } else if videoWriter.status == .cancelled {
            return "status cancelled"
        } else if videoWriter.status == .unknown {
            return "status unknown"
        } else {
            return "status completed"
        }
    }
}

extension CAMViewController {
    override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
        cameraBuffer.trans = true
    }
}
