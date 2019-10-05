//
//  CAMViewController.swift
//  CamTracking2
//
//  Created by Jakub Adamski on 31/08/2018.
//  Copyright © 2018 Jakub Adamski. All rights reserved.
//  Main screen with tracker

import UIKit
import CoreBluetooth
import AVFoundation
import Photos

//special characteristics for my Bluetooth device
let BService = CBUUID(string: "0xFFE0")
let BCharacteristic = CBUUID(string: "0xFFE1")

class CAMViewController: UIViewController , CameraBufferDelegate {
    
    var cameraBuffer:CameraBuffer!
    var centralManager: CBCentralManager?
    var devicen = "" //device name set by ViewController
    var device: CBPeripheral? //Bluetooth device
    var devicechara: CBCharacteristic?
    var timer = Timer() //timer for battery checking via Bluetooth
    var frame: UIImage?
    let overlay = UIView()
    var lastPoint = CGPoint.zero
    let opencvWrapper = OpenCVWrapper(); //opencv include

    @IBOutlet weak var camView: UIImageView!
    @IBOutlet weak var name: UIBarButtonItem!
    @IBOutlet weak var state: UIBarButtonItem!
    @IBOutlet weak var message: UIBarButtonItem!
    
    //Info popup
    @IBAction func infob(_ sender: UIButton) {
        let alertinf = UIAlertController(title: "App description", message: "TODO", preferredStyle: .alert)
        alertinf.addAction(UIAlertAction(title: "Ok", style: .default, handler: nil))
        self.present(alertinf, animated: true)
    }
    
    //function sends simple message requesting baterry information
    @objc func update() {
        device?.writeValue("p".data(using: .utf8)!, for: devicechara!, type: CBCharacteristicWriteType(rawValue: 1)!)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        name.title = devicen
        state.title = " - "
        let centralQueue: DispatchQueue = DispatchQueue(label: "com.iosbrain.centralQueueName", attributes: .concurrent)
        
        //Bluetooth manager and timer manager
        centralManager = CBCentralManager(delegate: self, queue: centralQueue)
        timer = Timer.scheduledTimer(timeInterval: 3, target: self, selector: #selector(update), userInfo: nil, repeats: true)
      
        //Video recording code in CameraBuffer
        cameraBuffer = CameraBuffer()
        cameraBuffer.delegate = self
        Recstate.setTitle("Start rec", for: .normal)
        
        overlay.layer.borderColor = UIColor.white.cgColor
        overlay.backgroundColor = UIColor.clear.withAlphaComponent(0.5)
        overlay.isHidden = true
        self.camView.addSubview(overlay)
        
        //adding back button
        self.navigationItem.hidesBackButton = true
        let newBackButton = UIBarButtonItem(title: "Back", style: UIBarButtonItem.Style.plain, target: self, action: #selector(CAMViewController.back(sender:)))
        self.navigationItem.leftBarButtonItem = newBackButton
        newBackButton.tintColor = UIColor.white
 
        let height: CGFloat = 40 //whatever height you want to add to the existing height
        let bounds = self.navigationController!.navigationBar.bounds
        self.navigationController?.navigationBar.frame = CGRect(x: 0, y: 0, width: bounds.width, height: bounds.height + height)
    }
    
    //reseting tracker
    @IBAction func TReset(_ sender: UIBarButtonItem) {
    readytotrack = false
    trackerreset = true
    opencvWrapper.trackerreset()
    }
    
    @IBOutlet weak var Recstate: UIButton!
    
    //recording and saving video
    @IBAction func Rec(_ sender: UIButton) {
        if cameraBuffer.isRecording {
            cameraBuffer.stop()
            Recstate.setTitle("Start rec", for: .normal)
            PHPhotoLibrary.requestAuthorization { status in
                if status == .authorized {
                    // Save the movie file to the photo library and cleanup.
                    PHPhotoLibrary.shared().performChanges({
                        let options = PHAssetResourceCreationOptions()
                        options.shouldMoveFile = true
                        let creationRequest = PHAssetCreationRequest.forAsset()
                        creationRequest.addResource(with: .video, fileURL: self.cameraBuffer.urll, options: options)
                    }, completionHandler: { success, error in
                        if success {
                            let alertController = UIAlertController(title: "Your video was successfully saved", message: nil, preferredStyle: .alert)
                            let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
                            alertController.addAction(defaultAction)
                            self.present(alertController, animated: true, completion: nil)
                        }
                        if !success {
                            let alertController = UIAlertController(title: "Error saving", message: nil, preferredStyle: .alert)
                            let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
                            alertController.addAction(defaultAction)
                            self.present(alertController, animated: true, completion: nil)
                        }
                    }
                    )
                }
            }
        }
        else {
            cameraBuffer.start()
            Recstate.setTitle("Stop rec", for: .normal)
            let alertController = UIAlertController(title: "Recording started", message: nil, preferredStyle: .alert)
            let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
            alertController.addAction(defaultAction)
            self.present(alertController, animated: true, completion: nil)
        }
 
    }
    
    //tracker manager
    var place: Int32 = 50
    var stateT = true
    var readytotrack = false
    var counter = 1
    var move = false
    func captured(image: UIImage) {
        //sending first image only to get size information
        if counter == 1 {
            opencvWrapper.start(image)
            counter += 1
        }
        //init the tracker
        if touchstate {
            camView.image = opencvWrapper.inittracker(image)
            touchstate = false
            readytotrack = true
        }
        //tracking function miejsce sends information where tracked object is 0 - left 50 - center 100 - right
        if touchstate == false && readytotrack == false {
            camView.image = image
        }
        if readytotrack {
            if stateT {
                stateT = false
                DispatchQueue.main.async {
                    self.camView.image =  self.opencvWrapper.trackerstart(image)
                    self.place = self.opencvWrapper.miejsce()
                    self.stateT = true
                }
            }
            ruch()
        }
    }
    
    //sending special information to my device about how to move motor
    func ruch () {
        if place < 40 && move == false {
            moveleft()
        }
    
        if place > 60 && move == false {
            moveright()
        }
        
        if place >= 40 && place <= 60 && move {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2){
                self.device?.writeValue("b".data(using: .utf8)!, for:
                    self.devicechara!, type: CBCharacteristicWriteType(rawValue: 1)!)
                self.move = false
            }
        }
    }
    
    func moveright () {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            self.device?.writeValue("r".data(using: .utf8)!, for:
                self.devicechara!, type: CBCharacteristicWriteType(rawValue: 1)!)
            self.move = true
        }
    }
    func moveleft () {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            self.device?.writeValue("l".data(using: .utf8)!, for: self.devicechara!, type: CBCharacteristicWriteType(rawValue: 1)!)
            self.move = true
        }
    }
    
    //starting to draw rectangle on screen
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        if trackerreset {
            //Save original tap Point
            if let touch = touches.first {
                lastPoint = touch.location(in: self.camView)
            }
        }
    }
    
    //drawing...
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        //Get the current known point and redraw
        if trackerreset {
        if let touch = touches.first {
            let currentPoint = touch.location(in: camView)
            reDrawSelectionArea(fromPoint: lastPoint, toPoint: currentPoint)
        }
        }
    }
    var rect: CGRect?
    func reDrawSelectionArea(fromPoint: CGPoint, toPoint: CGPoint) {
        overlay.isHidden = false
        //Calculate rect from the original point and last known point
        let rectwidth = toPoint.x - fromPoint.x
        let rectheight = toPoint.y - fromPoint.y
        rect = CGRect(x: fromPoint.x, y: fromPoint.y, width: rectwidth, height: rectheight)
        overlay.frame = rect!
    }
    
    //end of drawing - start tracker
    var touchstate = false
    var trackerreset = true
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        if trackerreset {
        overlay.isHidden = true
            
            //coordinates
            let px = (rect?.minX)! * 100 / camView.bounds.width
            let py = (rect?.minY)! * 100 / camView.bounds.height
            let pw = (rect?.width)! * 100 / camView.bounds.width
            let ph = (rect?.height)! * 100 / camView.bounds.height
            opencvWrapper.frameinicx(Int32(px))
            opencvWrapper.frameinicy(Int32(py))
            opencvWrapper.frameinicw(Int32(pw))
            opencvWrapper.frameinich(Int32(ph))
            
        touchstate = true
        trackerreset = false
        overlay.frame = CGRect.zero //reset overlay for next tap
        }
    }
    
    //back button
    @objc func back(sender: UIBarButtonItem) {
        //skip disconnection if none was created
        if (device != nil){
            centralManager?.cancelPeripheralConnection(device!)
        }
        
        for subview in (navigationController?.navigationBar.subviews)! {
            if subview is UIVisualEffectView {
                subview.removeFromSuperview()
            }
        }
        
        for subview in (navigationController?.toolbar.subviews)! {
            if subview is UIVisualEffectView {
                subview.removeFromSuperview()
            }
        }
        // Go back to the previous ViewController
        _ = navigationController?.popViewController(animated: true)
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
}

extension CAMViewController: CBCentralManagerDelegate,CBPeripheralDelegate {
    //scaning
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if (central.state == .poweredOn){
            centralManager?.scanForPeripherals(withServices: nil, options: nil)
        }
    }
    
    //trying to connect with device
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
    
        if peripheral.name == devicen {
            device = peripheral
            device?.delegate = self
            centralManager?.stopScan()
            centralManager?.connect(device!)
        }
    }

    //checking if connection is established
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        DispatchQueue.main.async {
            self.state.title = "OK.1"
        }
        device?.discoverServices ([BService])
    }
    
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        //error notification
    }
    
    //checking if I conneted to the right spec device part 1
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        for service in peripheral.services! {
            if service.uuid == BService {
                DispatchQueue.main.async {
                    self.state.title = "OK.2"
                }
                peripheral.discoverCharacteristics(nil, for: service)
            }
        }
    }
    
    //checking if I conneted to the right spec device part 2
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        for characteristic in service.characteristics! {
            if characteristic.uuid == BCharacteristic {
                DispatchQueue.main.async {
                    self.state.title = "OK"
                }
                peripheral.setNotifyValue(true, for: characteristic)
                devicechara=characteristic
            }
        }
    }
    
    //special functions to check battery state every 3 seconds
    func percent(chara: CBCharacteristic) -> String {
        let data = chara.value!
        let value = String(decoding: data, as: UTF8.self)
        let min = 2.5
        let max = 4.2 - min
        let result = (Double(value)!-min)/max * 100
        return "\(String(format: "%.0f", result)) %"
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        if characteristic.uuid == BCharacteristic {
            DispatchQueue.main.async {
                self.message.title = self.percent(chara: characteristic)
            }
        }
    }
}
