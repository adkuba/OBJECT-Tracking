//
//  ViewController.swift
//  CamTracking2
//
//  Created by Jakub Adamski on 30/08/2018.
//  Copyright © 2018 Jakub Adamski. All rights reserved.
//
import UIKit
import CoreBluetooth //Bluetooth

//Special structure enables testing camera without connection
struct Device {
    var specialname: String?
    var bl: CBPeripheral?
}

class ViewController: UIViewController {
    var centralManager: CBCentralManager? //Bluetooth
    var peripherals = Array<Device>() //Bluetooth
    
    override var prefersStatusBarHidden: Bool { //status bar always on
        return false
    }
    
    @IBOutlet weak var Btable: UITableView!
    
    @IBAction func buttonPopup(_ sender: UIBarButtonItem) {
        showInputDialog()
    }
    
    @IBAction func resetB(_ sender: UIBarButtonItem) {
        peripherals.removeAll(where: {$0.bl != nil} ) //removing all devices exept special
        Btable.reloadData()
        self.centralManager?.scanForPeripherals(withServices: nil, options: nil)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        peripherals.append(Device(specialname: "Testing", bl: nil)) //special device
        centralManager = CBCentralManager(delegate: self, queue: DispatchQueue.main)
        concheck()
        
        let height: CGFloat = 40 //whatever height you want to add to the existing height
        let bounds = self.navigationController!.navigationBar.bounds
        self.navigationController?.navigationBar.frame = CGRect(x: 0, y: 0, width: bounds.width, height: bounds.height + height)
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func showInputDialog() {
        //Creates popup after button press
        //info
        let alertController = UIAlertController(title: "Choose your device from list", message: "Devices are refreshing automatically, tap on device named TrackingCAM", preferredStyle: .alert)
        
        //button ok
        let confirmAction = UIAlertAction(title: "Ok", style: .default)
        
        //action to dialogbox
        alertController.addAction(confirmAction)
        
        //end
        self.present(alertController, animated: true, completion: nil)
    }
}

// Bluetooth from here
extension ViewController: CBCentralManagerDelegate, CBPeripheralDelegate {
    
    func concheck() {
        func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
            self.centralManager?.cancelPeripheralConnection(peripheral)
        }
    }
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if (central.state == .poweredOn){
            self.centralManager?.scanForPeripherals(withServices: nil, options: nil)
        }
        else {
            let alert = UIAlertController(title: "Bluetooth is off", message: "Power on bluetooth", preferredStyle: .alert)
            
            alert.addAction(UIAlertAction(title: "Ok", style: .default, handler: nil))
            
            self.present(alert, animated: true)
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        if !peripherals.contains(where: {$0.bl == peripheral} ){ //prevents adding the same device multiple times
            peripherals.append(Device(specialname: peripheral.name, bl: peripheral))
        }
        Btable.reloadData()
    }
}

//table update from here
extension ViewController: UITableViewDelegate, UITableViewDataSource {
    
    func tableView(_ Btable: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell:UITableViewCell = self.Btable.dequeueReusableCell(withIdentifier: "cell")! as UITableViewCell
        
        let peripheral = peripherals[indexPath.row]
        cell.textLabel?.text = peripheral.specialname
        return cell
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return peripherals.count
    }
    
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) { //going to next screen with camera
        let vc = storyboard?.instantiateViewController(withIdentifier: "CAMViewController") as! CAMViewController
        centralManager?.stopScan()
        vc.devicen = peripherals[indexPath.row].specialname!
        navigationController?.pushViewController(vc, animated: true)
    }
}
