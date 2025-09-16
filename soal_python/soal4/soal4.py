# soal1.py
import sys
import os

# Menambahkan path ke direktori parent untuk mengimpor modul callme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import MqttHelper, MyScheduler, time dari callme
from function.callme import MqttHelper, MyScheduler, time


# Fungsi utama
def main():
    NAME = "sendy"
    mqtt_helper = MqttHelper(NAME) # Inisialisasi MqttHelper dengan nama

    scheduler = MyScheduler(mqtt_helper.interval) # Inisialisasi MyScheduler dengan interval dari mqtt_helper

    while True:
        scheduler.interval = mqtt_helper.interval # Update interval scheduler
        mqtt_helper.publishData() # Publish data menggunakan mqtt_helper
        time.sleep(scheduler.interval)


# Jalankan fungsi utama
if __name__ == "__main__":
    main()
