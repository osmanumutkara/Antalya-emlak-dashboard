from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.chrome.options import Options

# --- TEXTCONTENT FONKSİYONU ---
def get_text_js(driver, element, timeout=3):
    """React sitelerinde .text yerine textContent ile güvenli metin okuma"""
    t0 = time.time()
    text = ""
    while text.strip() == "" and time.time() - t0 < timeout:
        text = driver.execute_script("return arguments[0].textContent;", element)
        time.sleep(0.1)
    return text.strip()


options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


url="https://www.emlakjet.com/satilik-konut/antalya"

ilan_linkleri = []
tum_veriler = []


for sayfa in range(1,51):
    url = f"https://www.emlakjet.com/satilik-konut/antalya/?sayfa={sayfa}"
    driver.get(url)
    time.sleep(3)

    for i in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    ilan_kartlari = driver.find_elements(By.TAG_NAME, "a")

    for kart in ilan_kartlari:
        href = kart.get_attribute("href")
        if href and "/ilan/" in href:
            ilan_linkleri.append(href)

    ilan_linkleri = list(set(ilan_linkleri))

print("Toplam link:", len(ilan_linkleri))
print(ilan_linkleri[:10])


# 2) Her ilan sayfasına tek tek gir
for link in ilan_linkleri:
    driver.get(link)
    time.sleep(2)

    print("\n=========================")
    print(link)

    # --- FİYAT ---
    try:
        wrap = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class^='styles_topWrap']")
            )
        )
        fiyat_el = wrap.find_element(By.CSS_SELECTOR, "span[class^='styles_price']")
        fiyat = get_text_js(driver, fiyat_el)
    except:
        fiyat = "Bulunamadı"

    print("Fiyat:", fiyat)

    # --- ADRES ---
    try:
        adres_el = driver.find_element(By.CSS_SELECTOR,
            "span[class^='styles_location']")
        adres = get_text_js(driver, adres_el)
    except:
        adres = "Bulunamadı"

    print("Adres:", adres)

    # --- TABLO ---
    
    veriler = {}

    try:
        # Sayfadaki TÜM <li> elemanlarına bak
        satirlar = driver.find_elements(By.TAG_NAME, "li")

        for s in satirlar:
            try:
                key_el = s.find_element(By.CSS_SELECTOR, "span[class^='styles_key']")
                val_el = s.find_element(By.CSS_SELECTOR, "span[class^='styles_value']")

                key = get_text_js(driver, key_el)
                value = get_text_js(driver, val_el)

                veriler[key] = value
            except:
                # Bu <li>'de key/value yoksa geç
                pass

    except:
        veriler ={}

    print("Tablo:", veriler)
    kayit = {
    "Link": link,
    "Fiyat": fiyat,
    "Adres": adres}

    # Tablodaki tüm key-value'ları kayda ekle
    for k, v in veriler.items():
        kayit[k] = v

    # Kaydı büyük listeye ekle
    tum_veriler.append(kayit)

df = pd.DataFrame(tum_veriler)
df.to_excel("emlakjet_antalya.xlsx", index=False)
print("\nExcel başarıyla oluşturuldu: emlakjet_antalya.xlsx")


