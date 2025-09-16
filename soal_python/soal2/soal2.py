# soal2.py
import sys
import os

# Menambahkan path ke direktori parent untuk mengimpor modul callme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import MyScheduler, OpenWeatherHelper dari callme
from function.callme import MyScheduler, OpenWeatherHelper


# Fungsi untuk main program
def main():
    while True:
        try:
            interval = int(input("Masukkan interval (detik): ")) # Minta input interval
            if interval <= 0:
                print("Interval harus angka di atas 0.")
                continue
            break
        except ValueError:
            print("Input harus berupa angka.")

    # API key
    API_KEY = "4a69dceaff90f6368033741999e52045"

    # Kota
    CITY = "Bandung"

    scheduler = MyScheduler(interval) # Inisialisasi scheduler dengan interval yang diberikan
    scheduler.run(OpenWeatherHelper.samplingWeather, API_KEY, CITY)  # Menjalankan samplingWeather secara periodik


# Menjalankan fungsi utama
if __name__ == "__main__":
    main()