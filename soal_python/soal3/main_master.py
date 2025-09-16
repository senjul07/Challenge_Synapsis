# main_master.py
import sys
import os

# Menambahkan path ke direktori parent untuk mengimpor modul callme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import ModbusHelper, MyScheduler, time, Thread dari callme
from function.callme import ModbusHelper, MyScheduler, time, Thread

SLAVE_IP = "127.0.0.1"
PORT = 5020
READ_INTERVAL = 5
CONTROL_INTERVAL = 30

class ModbusMaster:
    # Inisialisasi Modbus Master
    def __init__(self, ip=SLAVE_IP, port=PORT): # default ip localhost, port 5020
        self.client = ModbusHelper.ModbusTcpClient(ip, port=port) # koneksi ke slave
        self.status_toggle = 0


    # Fungsi untuk membaca register dari slave
    def readRegisters(self):
        rr_temp = self.client.read_holding_registers(0, 2) # baca register 0 dan 1 (suhu)
        rr_hum = self.client.read_holding_registers(2, 2) # baca register 2 dan 3 (humidity)
        rr_status = self.client.read_holding_registers(4, 1) # baca register 4 (status)

        temp = ModbusHelper.registerToFloat(rr_temp.registers) if rr_temp.isError() == False else None # konversi temp ke float
        hum = ModbusHelper.registerToFloat(rr_hum.registers) if rr_hum.isError() == False else None # konversi hum ke float
        status = rr_status.registers[0] if rr_status.isError() == False else None # status
        status_str = "RUNNING" if status==1 else "OFF" if status==0 else "UNKNOWN"
        ts = ModbusHelper.getTimestampGmt7() # ambil timestamp GMT+7
        print(f"{ts} | Suhu: {temp}°C | Hum: {hum}% | Status: {status_str}")


    # Fungsi untuk mengontrol register status di slave
    def controlRegister(self):
        self.client.write_register(4, self.status_toggle) # tulis ke register 4 (status)
        self.status_toggle = 0 if self.status_toggle==1 else 1 # toggle status


    # Fungsi untuk menjalankan Modbus Master
    def run(self):
        read_scheduler = MyScheduler(READ_INTERVAL) # scheduler untuk baca register
        control_scheduler = MyScheduler(CONTROL_INTERVAL) # scheduler untuk kontrol register

        Thread(target=read_scheduler.run, args=(self.readRegisters,), daemon=True).start() # jalankan read scheduler di thread terpisah
        Thread(target=control_scheduler.run, args=(self.controlRegister,), daemon=True).start() # jalankan control scheduler di thread terpisah

        while True:
            time.sleep(1)


# Jalankan Modbus Master
if __name__ == "__main__":
    master = ModbusMaster()
    master.run()