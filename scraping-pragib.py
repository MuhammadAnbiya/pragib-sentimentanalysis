from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime, timedelta

# Fungsi untuk membuat rentang tanggal
def generate_date_ranges(start_date, end_date, interval_days=1):
    date_ranges = []
    current_start_date = start_date
    while current_start_date <= end_date:
        current_end_date = min(current_start_date + timedelta(days=interval_days - 1), end_date)
        date_ranges.append((current_start_date, current_end_date))
        current_start_date = current_end_date + timedelta(days=1)
    return date_ranges

# Konfigurasi WebDriver
chrome_profile_path = "/home/muhammadanbiya/.config/google-chrome/Default"

options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")  # Tambahkan agar bisa berjalan tanpa GUI
options.add_argument("--disable-gpu")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("✅ WebDriver berhasil diinisialisasi.")
except Exception as e:
    print(f"❌ Gagal menginisialisasi WebDriver: {e}")
    exit(1)

# Fungsi untuk membuka Google News dan melakukan pencarian
def search_google_news():
    try:
        driver.get("https://www.google.com/?hl=en")
        print("✅ Berhasil membuka Google.")

        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys("Prabowo Gibran kinerja 2024")
        search_box.send_keys(Keys.RETURN)
        print("✅ Berhasil memasukkan kata kunci.")

        # Tunggu tombol News muncul dan klik
        news_tab = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href,"tbm=nws")]')))
        news_tab.click()
        print("✅ Berhasil membuka tab News.")

        # Tunggu tombol Tools muncul dan klik
        tools_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Tools"]')))
        tools_button.click()
        print("✅ Berhasil membuka menu Tools.")

        # Tunggu opsi Sort by Date muncul dan klik
        sort_span = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="AozSsc"]//span')))
        sort_span.click()
        print("✅ Berhasil memilih 'Sort by Date'.")

    except Exception as e:
        print(f"❌ Gagal melakukan pencarian: {e}")
        driver.quit()
        exit(1)

# Fungsi untuk mengatur rentang tanggal
def set_date_range(start, end):
    try:
        date_picker = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "gTl8xb")))
        date_picker.click()

        custom_range = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Custom range..."]')))
        custom_range.click()

        start_date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "OouJcb")))
        start_date_input.clear()
        start_date_input.send_keys(start.strftime("%m/%d/%Y"))

        end_date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rzG2be")))
        end_date_input.clear()
        end_date_input.send_keys(end.strftime("%m/%d/%Y"))

        go_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//g-button/span[text()="Go"]')))
        go_button.click()
        print(f"✅ Rentang tanggal: {start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}")
        time.sleep(5)

    except Exception as e:
        print(f"⚠️ Gagal mengatur rentang tanggal {start} - {end}: {e}")

# Fungsi untuk mengambil data berita
def scrape_news():
    news_data = []
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        try:
            news_elements = driver.find_elements(By.CLASS_NAME, "SoaBEf")
            for news_element in news_elements:
                try:
                    title_element = news_element.find_element(By.CLASS_NAME, "n0jPhd")
                    source_element = news_element.find_element(By.CLASS_NAME, "MgUUmf")
                    link_element = news_element.find_element(By.CSS_SELECTOR, 'a.WlydOe')
                    
                    news_data.append([
                        title_element.text, source_element.text, datetime.today().strftime("%Y-%m-%d"), link_element.get_attribute('href')
                    ])
                except Exception as e:
                    print(f"⚠️ Gagal mengambil salah satu berita: {e}")

        except Exception as e:
            print(f"❌ Gagal mengambil daftar berita: {e}")

        try:
            next_page_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'pnnext')))
            next_page_button.click()
            time.sleep(3)
        except Exception:
            print("✅ Tidak ada halaman berikutnya.")
            break

    return news_data

# Fungsi untuk menyimpan hasil ke CSV
def save_to_csv(news_data, filename="prabowo-gibran.csv"):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Judul Berita', 'Nama Media', 'Waktu Terbit', 'Link Berita'])
            csv_writer.writerows(news_data)
        print(f"✅ Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"❌ Gagal menyimpan ke CSV: {e}")

# Eksekusi Program
search_google_news()

start_date = datetime(2024, 10, 20)
end_date = datetime.today()
date_ranges = generate_date_ranges(start_date, end_date)

all_news_data = []

for start, end in date_ranges:
    set_date_range(start, end)
    news_data = scrape_news()
    all_news_data.extend(news_data)

save_to_csv(all_news_data)

driver.quit()
print("✅ WebDriver ditutup.")
