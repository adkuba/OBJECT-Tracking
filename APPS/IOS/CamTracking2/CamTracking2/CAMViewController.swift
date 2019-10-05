//
//  CAMViewController.swift
//  CamTracking2
//
//  Created by kuba on 31/08/2018.
//  Copyright © 2018 kuba. All rights reserved.
//

import UIKit
import CoreBluetooth
import AVFoundation
import Photos

let BService = CBUUID(string: "0xFFE0")
let BCharacteristic = CBUUID(string: "0xFFE1")


class CAMViewController: UIViewController , CameraBufferDelegate {
    
    var cameraBuffer:CameraBuffer!
    
    var centralManager: CBCentralManager?
    var devicen = ""
    var device: CBPeripheral?
    var devicechara: CBCharacteristic?
    var timer = Timer()
    var frame: UIImage?
    let overlay = UIView()
    var lastPoint = CGPoint.zero
    let opencvWrapper = OpenCVWrapper();


    @IBOutlet weak var camView: UIImageView!
    @IBOutlet weak var name: UIBarButtonItem!
    @IBOutlet weak var state: UIBarButtonItem!
    @IBOutlet weak var message: UIBarButtonItem!
    
    
    
    
    @IBAction func infob(_ sender: UIButton) {
        let alertinf = UIAlertController(title: "App description", message: "Ładny opis tego ekranu", preferredStyle: .alert)
        
        alertinf.addAction(UIAlertAction(title: "Ok", style: .default, handler: nil))
        
        self.present(alertinf, animated: true)
    }
    
    
    @objc func update() {
        
        device?.writeValue("p".data(using: .utf8)!, for: devicechara!, type: CBCharacteristicWriteType(rawValue: 1)!)
    }
    
    

    override func viewDidLoad() {
        super.viewDidLoad()
        
        name.title = devicen
        state.title = " - "
        
        let centralQueue: DispatchQueue = DispatchQueue(label: "com.iosbrain.centralQueueName", attributes: .concurrent)
        centralManager = CBCentralManager(delegate: self, queue: centralQueue)
        timer = Timer.scheduledTimer(timeInterval: 3, target: self, selector: #selector(update), userInfo: nil, repeats: true)
        
      
        cameraBuffer = CameraBuffer()
        cameraBuffer.delegate = self
        Recstate.setTitle("Start rec", for: .normal)
        
        overlay.layer.borderColor = UIColor.white.cgColor
        overlay.backgroundColor = UIColor.clear.withAlphaComponent(0.5)
        overlay.isHidden = true
        self.camView.addSubview(overlay)
        
        self.navigationItem.hidesBackButton = true
        let newBackButton = UIBarButtonItem(title: "Back", style: UIBarButtonItemStyle.plain, target: self, action: #selector(CAMViewController.back(sender:)))
        self.navigationItem.leftBarButtonItem = newBackButton
        newBackButton.tintColor = UIColor.white
        
        // Find size for blur effect.
        let statusBarHeight = UIApplication.shared.statusBarFrame.size.height
        let boundsN = self.navigationController?.navigationBar.bounds.insetBy(dx: 0, dy: -(statusBarHeight)).offsetBy(dx: 0, dy: -(statusBarHeight))
        // Create blur effect.
        let visualEffectViewN = UIVisualEffectView(effect: UIBlurEffect(style: .dark))
        visualEffectViewN.frame = boundsN!
        // Set navigation bar up.
        self.navigationController?.navigationBar.isTranslucent = true
        self.navigationController?.navigationBar.setBackgroundImage(UIImage(), for: .default)
        self.navigationController?.navigationBar.addSubview(visualEffectViewN)
        self.navigationController?.navigationBar.sendSubview(toBack: visualEffectViewN)
        
        let boundsT = self.navigationController?.toolbar.bounds
        let visualEffectViewT = UIVisualEffectView(effect: UIBlurEffect(style: .dark))
        visualEffectViewT.frame = boundsT!
        self.navigationController?.toolbar.isTranslucent = true
        self.navigationController?.toolbar.setBackgroundImage(UIImage(), forToolbarPosition: .bottom, barMetrics: .default)
        self.navigationController?.toolbar.addSubview(visualEffectViewT)
        self.navigationController?.toolbar.sendSubview(toBack: visualEffectViewT)
        
        let height: CGFloat = 40 //whatever height you want to add to the existing height
        let bounds = self.navigationController!.navigationBar.bounds
        self.navigationController?.navigationBar.frame = CGRect(x: 0, y: 0, width: bounds.width, height: bounds.height + height)
    
    }
    
    
    @IBAction func TReset(_ sender: UIBarButtonItem) {
    readytotrack = false
    trackerreset = true
    opencvWrapper.trackerreset()
    }
    
    @IBOutlet weak var Recstate: UIButton!
    
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

    
    var miejsce: Int32 = 50
    var stan = true
    var readytotrack = false
    var licznik = 1
    var move = false
    func captured(image: UIImage) {
        if licznik == 1 {
            opencvWrapper.start(image)
            licznik += 1
        }
        if touchstate {
            camView.image = opencvWrapper.inittracker(image)
            touchstate = false
            readytotrack = true
        }
        if touchstate == false && readytotrack == false {
            camView.image = image
        }
        
        if readytotrack {
            if stan {
                stan = false
                DispatchQueue.main.async {
                    self.camView.image =  self.opencvWrapper.trackerstart(image)
                    self.miejsce = self.opencvWrapper.miejsce()
                    self.stan = true
                }
            }
            ruch()
        }
    }
    
 
    func ruch () {
            if miejsce < 40 && move == false {
                moveleft()
            }
    
            if miejsce > 60 && move == false {
                    moveright()
            }
        if miejsce >= 40 && miejsce <= 60 && move {
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
    
    
   override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
    if trackerreset {
        //Save original tap Point
        if let touch = touches.first {
            lastPoint = touch.location(in: self.camView)
        }
    }
    }
    
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
    
    var touchstate = false
    var trackerreset = true
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        if trackerreset {
        overlay.isHidden = true
            
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
    
    
    
    @objc func back(sender: UIBarButtonItem) {
        
        centralManager?.cancelPeripheralConnection(device!)
        
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
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if (central.state == .poweredOn){
            centralManager?.scanForPeripherals(withServices: nil, options: nil)
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        
        if peripheral.name == devicen {
            device = peripheral
            device?.delegate = self
            centralManager?.stopScan()
            centralManager?.connect(device!)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        
        DispatchQueue.main.async {
            self.state.title = "OK.1"
        }
        device?.discoverServices ([BService])
    }
    
    
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        //wyswietlac error że się rozłączyło
    }
    
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
