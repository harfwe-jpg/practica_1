# 🚗 Detector Vehicular YOLOv8 con Flask

Detector de vehículos en tiempo real usando **YOLOv8**, con interfaz web moderna y registro automático en JSON.

## ✨ Características

✅ **Detección en Tiempo Real**: Usa YOLOv8 nano para detección rápida
✅ **Interfaz Web Moderna**: Dark mode con glassmorphism y animaciones fluidas
✅ **HTML Integrado**: Toda la interfaz en un único archivo Python
✅ **Guardado Automático en JSON**: Registra todas las detecciones
✅ **Control en Vivo**: Ajusta confianza sin reiniciar
✅ **Múltiples Cámaras**: Selecciona entre diferentes fuentes
✅ **Estadísticas Instantáneas**: Contador de vehículos detectados
✅ **Descarga de Datos**: Exporta detecciones a JSON

## 📋 Requisitos Previos

- Python 3.8+
- Cámara web conectada
- 4GB RAM mínimo (8GB recomendado)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto
```bash
cd tu_carpeta_proyecto
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**Nota**: La primera ejecución descargará el modelo YOLOv8 (~35MB)

## 🎯 Uso

### Ejecutar el servidor
```bash
python vehicle_detector.py
```

El servidor se iniciará en `http://localhost:5000`

### Interfaz Web

1. **Abre el navegador** en http://localhost:5000
2. **Selecciona la cámara** (si tienes múltiples)
3. **Ajusta el nivel de confianza** (recomendado 50%)
4. **Haz clic en "Iniciar"** para comenzar la detección
5. **Observa los resultados** en tiempo real
6. **Descarga los datos** en JSON cuando termines

## 📊 Estructura de Datos JSON

Cada detección se guarda con la siguiente estructura:

```json
[
  {
    "timestamp": "2024-06-24T15:30:45.123456",
    "class": "car",
    "confidence": 0.95,
    "box": [125.5, 200.3, 425.8, 480.2]
  },
  {
    "timestamp": "2024-06-24T15:30:45.234567",
    "class": "truck",
    "confidence": 0.87,
    "box": [50.2, 100.1, 600.5, 450.3]
  }
]
```

### Campos

- **timestamp**: Hora exacta de la detección (ISO 8601)
- **class**: Tipo de vehículo (car, truck, bus, motorcycle)
- **confidence**: Confianza de la detección (0-1)
- **box**: Coordenadas [x1, y1, x2, y2] del área detectada

## 🎨 Personalización

### Cambiar el modelo YOLOv8
Edita la línea en `vehicle_detector.py`:
```python
config.model = YOLO('yolov8n.pt')  # nano
# Opciones:
# 'yolov8s.pt'  - small (más rápido, menos preciso)
# 'yolov8m.pt'  - medium (balance)
# 'yolov8l.pt'  - large (más preciso, más lento)
```

### Cambiar colores de la interfaz
En la sección `<style>` del HTML:
```css
/* Cyan actual */
color: #00bcd4;

/* Cambia a otros colores */
color: #ffc107;  /* Dorado */
color: #4caf50;  /* Verde */
color: #e91e63;  /* Rosa */
```

### Ajustar velocidad de frames
```python
# En capture_video():
if frame_count % 2 == 0:  # Procesa cada 2 frames
# Cambiar a:
if frame_count % 3 == 0:  # Procesa cada 3 frames (más rápido)
if frame_count % 1 == 0:  # Procesa cada frame (más preciso)
```

## 🔧 Solución de Problemas

### "No se encuentra la cámara"
```bash
# Verifica las cámaras disponibles en Windows:
dxdiag  # En hardware
# En Linux:
ls /dev/video*
```

### Bajo rendimiento
- Reduce la resolución: Edita `CAP_PROP_FRAME_WIDTH` y `CAP_PROP_FRAME_HEIGHT`
- Usa `yolov8n.pt` (nano) en lugar de versiones más grandes
- Aumenta `frame_count % 3` para procesar menos frames

### Error de memoria
- Reduce el límite de detecciones guardadas en memoria:
```python
config.detections = config.detections[-200:]  # En lugar de 500
```

## 📈 Casos de Uso

✅ Monitoreo de estacionamientos
✅ Control de tráfico vehicular
✅ Análisis de flujo de vehículos
✅ Seguridad en zonas restringidas
✅ Recopilación de datos para ML
✅ Proyectos académicos

## 📝 Registro de Cambios

**v1.0.0** (Inicial)
- Detección YOLOv8 en tiempo real
- Interfaz web completa integrada
- Guardado en JSON automático
- Control de confianza en vivo
- Estadísticas instantáneas

## 📧 Notas

- Las detecciones se guardan automáticamente cuando detienes la captura
- El archivo JSON se crea con timestamp para fácil identificación
- La interfaz actualiza cada 500ms para balance entre rendimiento y precisión

## 🎓 Créditos

- **YOLOv8**: Ultralytics
- **OpenCV**: Intel
- **Flask**: Pallets

---

**¡Disfruta detectando vehículos! 🚗🚕🚙**
