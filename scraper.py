import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(filename='scraper_debug.log', level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

def extraer_remates():
    logging.info("Iniciando Selenium con opciones predeterminadas (sin webdriver_manager)...")
    
    # Configuración de Chrome
    chrome_options = Options()
    # Ejecutar en segundo plano si lo deseas descomentando la siguiente línea:
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    # Selenium 4.6.0+ gestiona los drivers automáticamente
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    lista_remates = []
    
    try:
        # 1. Autenticación / Aceptar Términos
        portal_url = "https://remates.funcionjudicial.gob.ec/rematesjudiciales-web/pages/public/portal.jsf"
        logging.info(f"Cargando {portal_url}...")
        driver.get(portal_url)
        
        # Esperar y marcar el checkbox "He leído y estoy de acuerdo"
        logging.info("Aceptando términos y condiciones...")
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "pagoDiferido")))
        # Scroll para asegurar que sea clickeable
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1) 
        driver.execute_script("arguments[0].click();", checkbox)
        
        # Esperar y hacer clic en Continuar
        continuar_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn_aceptar_solicitud2")))
        driver.execute_script("arguments[0].click();", continuar_btn)
        
        # 2. Pantalla de Búsqueda -> Elegimos "Búsqueda por Geografía"
        logging.info("Esperando a que cargue el Dashboard o el Mapa directamente...")
        # Esperamos por el ícono del mapa O por el área de Loja, lo que ocurra primero
        indicador = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mapIcon, area[alt='Loja']")))
        
        if indicador.get_attribute("id") == "mapIcon":
            logging.info("Estamos en el Dashboard. Haciendo clic en mapIcon por JS...")
            driver.execute_script("arguments[0].click();", indicador)
            # Esperamos a que cargue el mapa de provincias
            logging.info("Seleccionando la provincia de LOJA en el mapa...")
            area_loja = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "area[alt='Loja']")))
            driver.execute_script("arguments[0].click();", area_loja)
        else:
            logging.info("El mapa ya estaba cargado por la sesión de JSF. Seleccionando LOJA...")
            driver.execute_script("arguments[0].click();", indicador)
        
        # Esperar a que la carga AJAX termine (el popup "Espere...")
        logging.info("Esperando a que termine el popup 'Espere...' de AJAX...")
        time.sleep(1) # Pequeña pausa para que el popup se levante
        try:
            WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Espere...')]")))
        except:
            pass
        
        time.sleep(2) # Dar tiempo adicional por seguridad a que el DOM refresque la tabla
        
        # 4. Leer resultados
        logging.info("Esperando tabla de resultados...")
        wait.until(EC.presence_of_element_located((By.ID, "tablaResultados")))
        time.sleep(2) # Dar tiempo a que el AJAX pueble la tabla

        while True:
            # Extraer filas de la página actual
            filas = driver.find_elements(By.XPATH, "//tbody[contains(@id, 'tablaResultados:tb')]/tr")
            logging.info(f"Extrayendo {len(filas)} registros de la página actual...")
            
            for fila in filas:
                columnas = fila.find_elements(By.TAG_NAME, "td")
                if len(columnas) >= 10:
                    item = {
                        "codigo": columnas[2].text.strip(),
                        "fecha": columnas[3].text.strip(),
                        "ubicacion": columnas[4].text.strip(),
                        "tipo_bien": columnas[5].text.strip(),
                        "avaluo": columnas[9].text.strip()
                    }
                    lista_remates.append(item)
            
            # Revisar paginación (botón siguiente)
            try:
                # El botón Next de rich faces suele tener la clase rf-ds-btn-next o id tablaResultados:down_ds_next
                # Verificamos si no está deshabilitado
                btn_siguiente = driver.find_element(By.XPATH, "//a[contains(@class, 'rf-ds-btn-next')]")
                clases_btn = btn_siguiente.get_attribute("class")
                
                if "rf-ds-btn-next-dis" in clases_btn: # Ejemplo de subclase deshabilitada en RichFaces, o no es visible
                    break
                else:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn_siguiente)
                    time.sleep(0.5)
                    btn_siguiente.click()
                    logging.info("Pasando a la siguiente página asíncona...")
                    time.sleep(3) # Esperar a que AJAX cargue la nueva página
            except:
                # Si no se encuentra el botón de siguiente, terminamos
                break

        logging.info(f"Extracción finalizada. Total registros {len(lista_remates)}.")

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        logging.error(f"Ocurrió un error o no se encontraron más datos: {e}\n{trace}")
        with open("error.txt", "w", encoding="utf-8") as f:
            f.write(trace)
        try:
            driver.save_screenshot("error_screenshot.png")
            logging.info("Captura de error guardada en error_screenshot.png")
        except:
            pass

    finally:
        logging.info("Cerrando navegador...")
        driver.quit()
        
    return lista_remates

if __name__ == "__main__":
    datos = extraer_remates()
    
    if datos:
        df = pd.DataFrame(datos)
        logging.info(df.head())
        # Exportar a CSV (Backup)
        archivo_salida = "remates_extraidos.csv"
        df.to_csv(archivo_salida, index=False, encoding="utf-8-sig")
        logging.info(f"¡Datos exportados exitosamente a {archivo_salida}!")
        
        # --- NUEVO: GUARDAR EN SQLITE ---
        import sqlite3
        try:
            logging.info("Conectando a base de datos SQLite (remates.db)...")
            conexion = sqlite3.connect("remates.db")
            cursor = conexion.cursor()
            
            # Crear tabla si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS remates (
                    codigo TEXT PRIMARY KEY,
                    fecha TEXT,
                    ubicacion TEXT,
                    tipo_bien TEXT,
                    avaluo TEXT
                )
            ''')
            
            # Insertar datos (Ignora si ya existe el código)
            registros_insertados = 0
            for remate in datos:
                cursor.execute('''
                    INSERT OR IGNORE INTO remates (codigo, fecha, ubicacion, tipo_bien, avaluo)
                    VALUES (?, ?, ?, ?, ?)
                ''', (remate['codigo'], remate['fecha'], remate['ubicacion'], remate['tipo_bien'], remate['avaluo']))
                if cursor.rowcount > 0:
                    registros_insertados += 1
                    
            conexion.commit()
            logging.info(f"¡Guardados {registros_insertados} registros NUEVOS en la base de datos SQLite!")
        except Exception as db_err:
            logging.error(f"Error al guardar en SQLite: {db_err}")
        finally:
            if 'conexion' in locals():
                conexion.close()
    else:
        logging.error("No se extrajeron datos para guardar.")
