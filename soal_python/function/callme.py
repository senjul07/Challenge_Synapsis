# callme.py
import os
import time
import json
import requests #
import random
import string

from threading import Thread
from datetime import datetime, timezone, timedelta



# -------------------------------
# CLASS UNTUK SOAL 1
# -------------------------------
# Class untuk helper CRUD
class CrudHelper:
    # Import modul mysql & flask di dalam class karena hanya dipake di soal 1
    import mysql.connector
    from mysql.connector import Error
    from flask import Flask, Response, request

    # Konfigurasi database
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "thisismySQLpassword"
    DB_NAME = "ProjectDB"


    # Fungsi koneksi ke database
    def getConnection():
        try:
            conn = CrudHelper.mysql.connector.connect(
                host=CrudHelper.DB_HOST,
                user=CrudHelper.DB_USER,
                password=CrudHelper.DB_PASSWORD,
                database=CrudHelper.DB_NAME
            )
            return conn
        except CrudHelper.Error:
            return False


    # Fungsi untuk menghasilkan ID node random (NODE-(5 huruf/angka random))
    def generateNodeID():
        rand_str = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        return f"NODE-{rand_str}" # Return string "NODE-xxxxx"


    # Fungsi untuk membaca semua node dari database
    def readAllNodes():
        try:
            conn = CrudHelper.getConnection()
            if not conn:
                return False

            cursor = conn.cursor(dictionary=True) # pakai dictionary=True supaya hasil fetchnya berupa dict
            cursor.execute("SELECT id, name, updated_at FROM nodeDB") # ambil data dari table nodeDB
            rows = cursor.fetchall() # ambil semua hasil query

            nodes = [] # list untuk menampung data node
            for row in rows:
                nodes.append({ # masukkan data ke list nodes
                    "node_id": row["id"],
                    "name": row["name"],
                    "total_sensor": 0,  # Placeholder soalnya gaada di table
                    "updated_at": row["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if row["updated_at"] else None
                })

            cursor.close()
            conn.close()
            return nodes

        except CrudHelper.Error:
            return False


    # Fungsi untuk memasukkan node baru ke database
    def insertNode(name):
        try:
            conn = CrudHelper.getConnection()
            if not conn:
                return False

            node_id = CrudHelper.generateNodeID() # generate ID node baru
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # ambil waktu sekarang

            cursor = conn.cursor() # buat cursor
            sql = "INSERT INTO nodeDB (id, name, updated_at) VALUES (%s, %s, %s)" # query insert
            cursor.execute(sql, (node_id, name, updated_at)) # execute query
            conn.commit() # commit perubahan ke database

            cursor.close()
            conn.close()
            return True
        except CrudHelper.Error:
            return False
        

    # Fungsi untuk memperbarui node di database
    def updateNode(node_id, name):
        try:
            conn = CrudHelper.getConnection()
            if not conn:
                return False

            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # ambil waktu sekarang
            cursor = conn.cursor() # buat cursor
            sql = "UPDATE nodeDB SET name=%s, updated_at=%s WHERE id=%s" # query update
            cursor.execute(sql, (name, updated_at, node_id)) # execute query
            conn.commit() # commit perubahan ke database

            check_data = cursor.rowcount  # cek berapa baris terhapus

            cursor.close()
            conn.close()

            return check_data > 0   # kalo ada baris yang kena, return True
        except CrudHelper.Error:
            return False


    # Fungsi untuk menghapus node dari database
    def deleteNode(node_id):
        try:
            conn = CrudHelper.getConnection()
            if not conn:
                return False

            cursor = conn.cursor() # buat cursor
            sql = "DELETE FROM nodeDB WHERE id=%s" # query delete
            cursor.execute(sql, (node_id,)) # execute query
            conn.commit() # commit perubahan ke database

            check_data = cursor.rowcount # cek berapa baris terhapus

            cursor.close()
            conn.close()

            return check_data > 0   # kalo ada baris yang kena, return True
        except CrudHelper.Error:
            return False


    # Fungsi untuk membuat response JSON
    def makeResponse(status, message, data): # data berupa list of dict
        resp = {
            "status": status,
            "message": message,
            "data": data
        }
        return CrudHelper.Response(json.dumps(resp), mimetype="application/json") # return response JSON
    

# -------------------------------
# SOAL 2: Scheduler
# -------------------------------
# Class untuk scheduler
class MyScheduler:
    # Inisialisasi scheduler dengan interval dalam detik
    def __init__(self, interval):
        if interval <= 0: # Jika interval <= 0, raise ValueError
            raise ValueError("Interval harus > 0")
        self.interval = interval


    # Untuk menjalankan fungsi secara periodik
    def run(self, func, *args, **kwargs):
        while True:
            func(*args, **kwargs)
            time.sleep(self.interval)


# Class untuk sampling data weather dari openweathermap.org
class OpenWeatherHelper:
    # Fungsi untuk sampling data weather
    def samplingWeather(api_key, city):
        ts = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") # timestamp lokal GMT+7
        log_folder = os.path.join(os.path.dirname(__file__), "../log") # path folder log
        os.makedirs(log_folder, exist_ok=True) # buat folder log kalo belum ada
        log_path = os.path.join(log_folder, "data_weather.json") # path file log

        # Ambil koordinat kota
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}" # URL untuk geocoding
        try:
            r_geo = requests.get(geo_url, timeout=10) # request ke API geocoding
            r_geo.raise_for_status() # raise error untuk status code 4xx/5xx
            geo_data = r_geo.json() # parse response JSON
            if len(geo_data) == 0: # kalo gaada data kota
                print(f"{ts} - Failed Running Sampling Data Weather: kota '{city}' tidak ditemukan") # Print error
                return
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"] # ambil lat & lon
        except Exception as e:
            print(f"{ts} - Failed Running Sampling Data Weather: {e}")
            return

        # Ambil data weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric" # URL untuk data weather
        try:
            response = requests.get(weather_url, timeout=10) # request ke API weather
            if response.status_code == 200: # kalo sukses
                data = response.json() # parse response JSON
                temp = data["main"]["temp"] # ambil temperature
                humidity = data["main"]["humidity"] # ambil humidity

                # Simpan ke log
                log_data = {
                    "city": city,
                    "temperature": temp,
                    "humidity": humidity,
                    "timestamp": ts
                }
                with open(log_path, "a") as f: # buka file log untuk append
                    json.dump(log_data, f) # simpan data sebagai JSON
                    f.write("\n") # tulis data baru di baris baru

                print(f"{ts} - Success Running Sampling Data Weather with Result Temperature {temp} °C & Humidity {humidity} %")
            else:
                print(f"{ts} - Failed Running Sampling Data Weather with Status Code {response.status_code} - {response.text}")
        except Exception as e:
            print(f"{ts} - Failed Running Sampling Data Weather with Error - {e}")


# -------------------------------
# SOAL 3: Modbus
# -------------------------------
# Class untuk helper Modbus
class ModbusHelper:
    # Import modul pymodbus di dalam class karena hanya dipake di soal 3
    from pymodbus.server.sync import StartTcpServer
    from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.client.sync import ModbusTcpClient
    from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
    from pymodbus.constants import Endian


    # Fungsi untuk membaca data weather dari file JSON
    def readWeatherJson(path=None):
        if path is None:
            log_folder = os.path.join(os.path.dirname(__file__), "../log") # path folder log
            path = os.path.join(log_folder, "data_weather.json") # path file log

        if not os.path.exists(path): # kalo file gaada
            return None, None

        try:
            with open(path, "r") as f: # buka file log
                lines = f.readlines() # baca semua baris
                if not lines: # kalo file kosong
                    return None, None
                last_line = lines[-1].strip() # ambil baris terakhir
                data = json.loads(last_line) # parse JSON

                temp = float(data.get("temperature", 0)) # ambil temperature
                hum = float(data.get("humidity", 0)) # ambil humidity
                return temp, hum # return temperature & humidity
        except Exception as e:
            print(f"Error reading weather json: {e}")
            return None, None


    # Konversi float ke register (2 register 16-bit)
    def floatToRegister(value):
        builder = ModbusHelper.BinaryPayloadBuilder(byteorder=ModbusHelper.Endian.Big, wordorder=ModbusHelper.Endian.Big) # Build payload
        builder.add_32bit_float(value) # add float ke payload
        return builder.to_registers() # return sebagai list of register (2 register 16-bit)


    # Konversi register (2 register 16-bit) ke float
    def registerToFloat(registers):
        decoder = ModbusHelper.BinaryPayloadDecoder.fromRegisters(registers, byteorder=ModbusHelper.Endian.Big, wordorder=ModbusHelper.Endian.Big) # Decode dari register
        return round(decoder.decode_32bit_float(), 2) # return sebagai float, dibuletin 2 desimal


    # Fungsi untuk mendapatkan timestamp lokal (GMT+7)
    def getTimestampGmt7():
        return datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") # return timestamp lokal GMT+7
    

    # Fungsi untuk mendapatkan timestamp UTC
    def getTimestampUtc():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # return timestamp UTC
    

# -------------------------------
# SOAL 4: MQTTT
# -------------------------------
# Class untuk helper MQTT
class MqttHelper:
    # Import modul paho-mqtt & csv di dalam class karena hanya dipake di soal 4
    import csv
    import paho.mqtt.client as mqtt


    # Inisialisasi MQTT Helper
    def __init__(self, name):
        self.name = name
        self.broker = "test.mosquitto.org" # Mosquitto public broker
        self.port = 1883 # default MQTT port
        self.topic_data = f"mqtt/{self.name}/data" # topic untuk publish data
        self.topic_cmd = f"mqtt/{self.name}/command" # topic untuk subscribe command
        self.interval = 5 # default interval dalam detik
        self.active = True # status aktif/inaktif untuk publish data

        self.client = MqttHelper.mqtt.Client() # buat client MQTT
        self.client.on_message = self.onMessage # set callback untuk pesan masuk
        self.client.connect(self.broker, self.port, 60) # koneksi ke broker
        self.client.subscribe(self.topic_cmd) # subscribe ke topic command
        self.client.loop_start() # start loop di background thread


    # Fungsi untuk menghasilkan payload data
    def generatePayload(self):
        temp, hum = ModbusHelper.readWeatherJson() # baca dari log data_weather.json
        if temp is None or hum is None:
            temp, hum = 0.0, 0.0 # kalo gaada data, set 0.0

        payload = {
            "nama": self.name,
            "data": {
                "sensor1": random.randint(0, 100), # random int 0-100
                "sensor2": round(random.uniform(0, 1000), 2), # random float 0.00-1000.00
                "sensor3": random.choice([True, False]), # random boolean
                "sensor4": round(float(temp), 2), # dari log data_weather.json
                "sensor5": round(float(hum), 2), # dari log data_weather.json
            },
            "timestamp": ModbusHelper.getTimestampUtc(), # timestamp UTC
        }
        return payload


    # Fungsi untuk mencatat log ke file CSV
    def logToCsv(self, payload, status):
        log_folder = os.path.join(os.path.dirname(__file__), "../log") # path folder log
        os.makedirs(log_folder, exist_ok=True) # buat folder log kalo belum ada
        file_name = f"mqtt_log_{datetime.now().strftime('%d%m%y')}.csv" # nama file log per tanggal
        log_path = os.path.join(log_folder, file_name) # path file log

        ts = ModbusHelper.getTimestampGmt7() # timestamp lokal GMT+7
        row = [
            ts,
            payload["data"]["sensor1"],
            payload["data"]["sensor2"],
            payload["data"]["sensor3"],
            payload["data"]["sensor4"],
            payload["data"]["sensor5"],
            status,
        ]

        file_exists = os.path.exists(log_path) # cek apakah file sudah ada
        with open(log_path, "a", newline="") as f: # buka file log untuk append
            writer = MqttHelper.csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow( # tulis header kalo file baru
                    ["timestamp", "sensor1", "sensor2", "sensor3", "sensor4", "sensor5", "status"]
                )
            writer.writerow(row) # tulis data


    # Fungsi untuk publish data ke mqtt broker
    def publishData(self):
        ts = ModbusHelper.getTimestampGmt7() # timestamp lokal GMT+7
        if not self.active:
            print(f"{ts} | Action: Publish | State: Inactive")
            return

        payload = self.generatePayload() # generate payload
        payload_str = json.dumps(payload) # convert payload ke string JSON

        result = self.client.publish(self.topic_data, payload_str) # publish ke broker
        status = "Success" if result.rc == MqttHelper.mqtt.MQTT_ERR_SUCCESS else "Failed" # cek status publish

        print(f"{ts} | Action: Publish | Topic: {self.topic_data} | Data: {payload_str} | State: {status}") 
        self.logToCsv(payload, status) # log ke CSV


    # Callback untuk pesan masuk
    def onMessage(self, client, userdata, message):
        ts = ModbusHelper.getTimestampGmt7() # timestamp lokal GMT+7
        try:
            payload = json.loads(message.payload.decode()) # parse JSON
        except Exception:
            print(f"{ts} | Action: Subscribe | Topic: {message.topic} | Data: Invalid JSON")
            return

        print(f"{ts} | Action: Subscribe | Topic: {message.topic} | Data: {payload}")

        if "command" in payload:
            cmd = payload["command"] # ambil command
            if cmd == "pause": # kalo command "pause", stop publish
                self.active = False
            elif cmd == "resume": # kalo command "resume", lanjut publish
                self.active = True
            elif cmd.startswith("set_interval:"): # kalo command "set_interval:x"
                try:
                    new_interval = int(cmd.split(":")[1]) # ambil nilai interval
                    self.interval = new_interval # set interval baru
                    print(f"{ts} | Interval changed to {self.interval} seconds")
                except ValueError:
                    print(f"{ts} | Invalid interval value in command")