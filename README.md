# Challenge Synapsis - Python Projects

## Struktur Direktori

```
Challenge_Synapsis/
├─ soal_python/
│  ├─ soal1/soal1.py
│  ├─ soal2/soal2.py
│  ├─ soal3/
│  │  ├─ main_master.py
│  │  └─ main_slave.py
│  ├─ soal4/soal4.py
│  ├─ log/data_weather.json
│  ├─ function/callme.py
│  └─ database/ProjectDB.sql
├─ soal_wokwi/
│  └─ link.txt
└─ documentation/
   ├─ video/  (demo hasil pengerjaan setiap soal)
   ├─ requirement.txt
   └─ readme
```

---

## Requirement

### 1. Pastikan **Python 3.8+** sudah terinstall.

Jika belum ada, install Python:

**Ubuntu/Linux**
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

**Windows**
1. Kunjungi [python.org/downloads](https://www.python.org/downloads/)
2. Download installer Python 3.8+ untuk Windows
3. Jalankan installer dan centang opsi **"Add Python to PATH"**
4. Selesai

### 2. Install package Python yang dibutuhkan dari `requirement.txt`:

**Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/documentation/
python3 -m pip install -r requirement.txt
```

**Windows**
```cmd
cd path\to\project\Challenge_Synapsis\documentation\
python -m pip install -r requirement.txt
```

---

## Cara Menjalankan Program

### Soal 1
**Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/soal_python/soal1/
python3 soal1.py
```

**Windows**
```cmd
cd path\to\project\Challenge_Synapsis\soal_python\soal1\
python soal1.py
```

***Gunakan Postman untuk testing***
```
GET:
http://127.0.0.1:8080/api/read/node

POST:
http://127.0.0.1:8080/api/create/node

PUT:
http://127.0.0.1:8080/api/update/node

DELETE:
http://127.0.0.1:8080/api/delete/node
```

### Soal 2
**Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/soal_python/soal2/
python3 soal2.py
```

**Windows**
```cmd
cd path\to\project\Challenge_Synapsis\soal_python\soal2\
python soal2.py
```

### Soal 3

**Slave (dijalankan dulu)**
- **Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/soal_python/soal3/
python3 main_slave.py
```

- **Windows**
```cmd
cd path\to\project\Challenge_Synapsis\soal_python\soal3\
python main_slave.py
```

**Master (dijalankan setelah Slave)**
- **Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/soal_python/soal3/
python3 main_master.py
```

- **Windows**
```cmd
cd path\to\project\Challenge_Synapsis\soal_python\soal3\
python main_master.py
```

> **Catatan:** Pastikan kedua program berjalan secara bersamaan. Jalankan Slave terlebih dahulu, kemudian Master.

### Soal 4
**Ubuntu/Linux**
```bash
cd path/to/project/Challenge_Synapsis/soal_python/soal4/
python3 soal4.py
```

**Windows**
```cmd
cd path\to\project\Challenge_Synapsis\soal_python\soal4\
python soal4.py
```

---

## Soal 5 (Wokwi ESP32)

- Buka file `link.txt` di `path/to/project/Challenge_Synapsis/soal_wokwi/`
- Copy link Wokwi ke browser untuk melihat dan menjalankan simulasi ESP32-S3 dengan sensor DHT22

---

## Catatan Tambahan

- Semua log hasil eksekusi disimpan di folder `log/`.
- Gunakan **Python 3.8+** untuk kompatibilitas dengan `requirement.txt`.
- Video demo setiap soal ada di folder `documentation/video/`.
