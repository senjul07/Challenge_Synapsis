# main_slave.py
import sys
import os

# Menambahkan path ke direktori parent untuk mengimpor modul callme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import ModbusHelper, time, Thread dari callme
from function.callme import ModbusHelper, time, Thread

UPDATE_INTERVAL = 5  # detik


class ModbusSlave:
    # Inisialisasi Modbus Slave
    def __init__(self, port=5020): # default port 5020
        # Register: 0=suhu, 1=humidity, 2=status
        self.store = ModbusHelper.ModbusSlaveContext(
            hr=ModbusHelper.ModbusSequentialDataBlock(0, [0]*6) # 6 register (0 - 1 untuk suhu, 2 - 3 untuk humidity, 4 untuk status, 5 untuk spare)
        )
        self.context = ModbusHelper.ModbusServerContext(slaves=self.store, single=True) # single slave
        self.status = 0
        self.port = port


    # Fungsi untuk update sensor
    def updateSensor(self):
        while True:
            temp, hum = ModbusHelper.readWeatherJson() # ambil data json dari file data_weather.json
            if temp is not None and hum is not None:
                self.store.setValues(3, 0, ModbusHelper.floatToRegister(temp))  # suhu
                self.store.setValues(3, 2, ModbusHelper.floatToRegister(hum))   # humidity
            # baca status register 2 (client bisa write)
            try:
                reg_status = self.store.getValues(3, 4, count=1)[0] # status
                if reg_status in [0, 1]:
                    self.status = reg_status # update status
            except:
                pass
            print("DEBUG: temp =", temp, "hum =", hum, "status =", self.status)
            time.sleep(UPDATE_INTERVAL)


    # Fungsi untuk menjalankan Modbus Slave
    def run(self):
        print(f"Starting Modbus Slave on port {self.port}...")
        Thread(target=self.updateSensor, daemon=True).start() # jalankan update sensor di thread terpisah
        # identitas slave
        identity = ModbusHelper.ModbusDeviceIdentification()
        identity.VendorName = "PT Synapsis Synergi Digital"
        identity.ProductCode = "WeatherModbus"
        identity.VendorUrl = "www.synapsis.id"
        identity.ProductName = "Weather Sensor Modbus Slave"
        identity.ModelName = "Slave-001"
        identity.MajorMinorRevision = "1.0"
        ModbusHelper.StartTcpServer(context=self.context, identity=identity, address=("0.0.0.0", self.port)) # jalankan server


# Jalankan Modbus Slave
if __name__ == "__main__":
    slave = ModbusSlave()
    slave.run()

