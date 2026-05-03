# Remates Judiciales - Scraper & API

Este proyecto automatiza la extracción de datos de **Remates Judiciales** publicados en el portal del Consejo de la Judicatura de Ecuador, y expone esta información mediante una API REST ligera y rápida.

## 🚀 Características Principales

1. **Web Scraper Automatizado (`scraper.py`)**: 
   - Utiliza **Selenium** para navegar por el portal de la función judicial.
   - Acepta automáticamente los términos y condiciones.
   - Extrae de manera asíncrona todos los remates judiciales por provincia (ej. Loja).
   - Guarda los registros extraídos tanto en formato CSV (`remates_extraidos.csv`) como en una base de datos local **SQLite** (`remates.db`).
   - Gestión robusta de logs para auditoría y revisión de errores (`scraper_debug.log`).

2. **API RESTful (`api.py`)**: 
   - Construida con **FastAPI**.
   - Conecta directamente con la base de datos local SQLite.
   - Expone endpoints para consumir los datos de los remates, listar ubicaciones y buscar por código o provincia.

## 🛠️ Requisitos Previos

- **Python 3.8+**
- Google Chrome (para la navegación automatizada)
- Las dependencias listadas en `requirements.txt`

## ⚙️ Instalación y Configuración

1. **Clona el repositorio** e ingresa al directorio del proyecto.
2. **Crea y activa un entorno virtual**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Instala las dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

## 💻 Uso

### 1. Ejecutar el Scraper

Para actualizar la base de datos con los últimos remates disponibles en el portal, ejecuta el scraper:

```powershell
python scraper.py
```
> Esto abrirá una instancia de Chrome (controlada por código), extraerá los datos y actualizará `remates.db`.

### 2. Levantar la API

Para iniciar el servidor de la API REST localmente:

```powershell
uvicorn api:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. 
Puedes acceder a la documentación interactiva (Swagger UI) navegando a:
`http://127.0.0.1:8000/docs`

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/` | Retorna el estado del servidor. |
| `GET` | `/api/remates` | Obtiene la lista completa de remates. |
| `GET` | `/api/lugares` | Obtiene una lista de las ubicaciones (ciudades/cantones) únicas. |
| `GET` | `/api/remates/{codigo}` | Obtiene los detalles de un remate usando su código específico. |
| `GET` | `/api/remates/provincia/{provincia}`| Filtra los remates pertenecientes a una ubicación o provincia determinada. |

## 📝 Notas
- Las búsquedas y filtros no distinguen entre mayúsculas y minúsculas gracias a la configuración en la API.
- La navegación en el portal web está sujeta a la disponibilidad y tiempos de respuesta de los servidores de la Judicatura.
