//
//  ViewController.swift
//  CamTracking2
//
//  Created by kuba on 30/08/2018.
//  Copyright © 2018 kuba. All rights reserved.
//
import UIKit
import CoreBluetooth //b


class ViewController: UIViewController {
    var centralManager: CBCentralManager? //b
    var peripherals = Array<CBPeripheral>() //b
    
    override var prefersStatusBarHidden: Bool { //status bar będzie zawsze aktywny
        return false
    }
    
    @IBOutlet weak var Btable: UITableView!
    
    @IBAction func buttonPopup(_ sender: UIBarButtonItem) {
        showInputDialog()
    }
    
    @IBAction func resetB(_ sender: UIBarButtonItem) {
        peripherals.removeAll()
        Btable.reloadData()
        self.centralManager?.scanForPeripherals(withServices: nil, options: nil)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
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
        //Tworzymy popup po naciśnięciu info
        //pokazujemy komunikat
        let alertController = UIAlertController(title: "Choose your device from list", message: "Devices are refreshing automatically, tap on device named TrackingCAM", preferredStyle: .alert)
        
        //tworzymy guzik ok
        let confirmAction = UIAlertAction(title: "Ok", style: .default)
        
        //dodajemy akcje do dialogbox
        alertController.addAction(confirmAction)
        
        //kończymy
        self.present(alertController, animated: true, completion: nil)
    }
}

// b wszystko na dole
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
        peripherals.append(peripheral)
        Btable.reloadData()
    }
}

extension ViewController: UITableViewDelegate, UITableViewDataSource {
    
    func tableView(_ Btable: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell:UITableViewCell = self.Btable.dequeueReusableCell(withIdentifier: "cell")! as UITableViewCell
        
        let peripheral = peripherals[indexPath.row]
        cell.textLabel?.text = peripheral.name
        return cell
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return peripherals.count
    }
    
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) { //jeśli klikniemy to przenosi nas do nastepnego ekranu
        let vc = storyboard?.instantiateViewController(withIdentifier: "CAMViewController") as! CAMViewController
        centralManager?.stopScan()
        vc.devicen = peripherals[indexPath.row].name!
        navigationController?.pushViewController(vc, animated: true)
    }
    
}
