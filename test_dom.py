from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

try:
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    # 1. Autenticación
    driver.get("https://remates.funcionjudicial.gob.ec/rematesjudiciales-web/pages/public/portal.jsf")
    time.sleep(3)
    
    checkbox = driver.find_element(By.ID, "pagoDiferido")
    driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", checkbox)
    time.sleep(1)
    
    continuar_btn = driver.find_element(By.ID, "btn_aceptar_solicitud2")
    driver.execute_script("arguments[0].click();", continuar_btn)
    time.sleep(4)
    
    with open("dom.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    print("DOM guardado en dom.html")
finally:
    try:
        driver.quit()
    except:
        pass
