# Interfaz Web - NIRScan Nano

Interfaz web moderna para el sensor NIRScan Nano del Proyecto Smart Milk.

## 🚀 Características

- **Interfaz web moderna** con diseño responsive
- **Verificación de conectividad** del sensor en tiempo real
- **Escaneo automático** con visualización del espectro
- **Guardado automático** en múltiples formatos (JSON, CSV, DAT, PNG)
- **Visualización de gráficos** en tiempo real
- **Notificaciones interactivas** para el usuario

## 📁 Estructura del Proyecto

```
web_interface/
├── main.py              # Servidor FastAPI
├── templates/
│   └── index.html       # Interfaz web principal
├── static/              # Archivos estáticos (se crea automáticamente)
│   ├── data/           # Archivos .dat
│   ├── json/           # Archivos JSON
│   ├── csv/            # Archivos CSV
│   └── plots/          # Gráficos PNG
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

## 🛠️ Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verificar que el sensor esté conectado** al puerto USB

## 🚀 Uso

### 1. Iniciar el servidor
```bash
python main.py
```

### 2. Abrir la interfaz web
Abrir el navegador y ir a: `http://localhost:8000`

### 3. Usar la interfaz

#### **Paso 1: Verificar Conexión**
- Hacer clic en "Verificar Conexión Sensor"
- El indicador de estado cambiará a verde si el sensor está conectado

#### **Paso 2: Realizar Escaneo**
- Una vez conectado, hacer clic en "Iniciar Escaneo"
- El sistema realizará el escaneo automáticamente
- Se mostrará el gráfico del espectro en tiempo real

#### **Paso 3: Guardar Datos**
- Ingresar el nombre de la muestra en el campo de texto
- Hacer clic en "Guardar Datos"
- Los archivos se guardarán en los directorios correspondientes

## 🎯 Funcionalidades

### **Verificación de Conectividad**
- ✅ Verifica si el sensor NIRScan Nano está conectado
- ✅ Muestra estado visual (rojo/verde)
- ✅ Información del dispositivo (Vendor ID, Product ID)

### **Escaneo Automático**
- 🔄 Realiza escaneo completo del sensor
- 📊 Interpreta datos automáticamente
- 📈 Genera gráfico del espectro en tiempo real
- ⏱️ Muestra tiempo de escaneo

### **Guardado de Datos**
- 💾 Guarda en formato **JSON** (datos estructurados)
- 📊 Guarda en formato **CSV** (datos tabulares)
- 🔧 Guarda en formato **DAT** (archivo binario original)
- 🖼️ Guarda gráfico en formato **PNG** (alta resolución)

### **Visualización**
- 📈 Gráfico interactivo del espectro NIR
- 📊 Información detallada del escaneo
- 🎨 Diseño moderno y responsive

## 🔧 Configuración

### **Puerto del Servidor**
Por defecto el servidor se ejecuta en el puerto 8000. Para cambiar:

```python
# En main.py, línea final
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### **Configuración del Sensor**
El sensor está configurado para:
- **Vendor ID:** 0x0451
- **Product ID:** 0x4200

## 📱 Diseño Responsive

La interfaz se adapta automáticamente a:
- 🖥️ Pantallas de escritorio
- 📱 Tablets
- 📱 Dispositivos móviles

## 🎨 Características del Diseño

- **Header:** Logo UNF, título del proyecto, logos de patrocinadores
- **Panel izquierdo:** Controles del sensor y estado de conexión
- **Panel derecho:** Visualización del espectro e información del escaneo
- **Footer:** Campo de entrada para nombre de muestra y botones de acción

## 🔍 Solución de Problemas

### **Error de Conexión**
- Verificar que el sensor esté conectado al USB
- Verificar que no haya otros programas usando el sensor
- Reiniciar el servidor si es necesario

### **Error de Escaneo**
- Asegurar que el sensor esté conectado antes del escaneo
- Verificar que no haya interferencias en el puerto USB
- Revisar los logs del servidor para más detalles

### **Error de Guardado**
- Verificar permisos de escritura en el directorio
- Asegurar que el nombre del archivo sea válido
- Verificar espacio disponible en disco

## 📞 Soporte

Para problemas técnicos o consultas:
- Revisar los logs del servidor en la consola
- Verificar la conectividad del sensor
- Consultar la documentación del sensor NIRScan Nano

## 🔄 Actualizaciones

Para actualizar la interfaz:
1. Detener el servidor (Ctrl+C)
2. Actualizar los archivos
3. Reiniciar el servidor: `python main.py`

---

**Proyecto Smart Milk - Universidad Nacional de Frontera**
*Desarrollado con FastAPI y tecnologías web modernas*
