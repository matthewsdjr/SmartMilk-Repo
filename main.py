#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor FastAPI para la interfaz web del sensor NIRScan Nano.
Proyecto Smart Milk - Universidad Nacional de Frontera.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import time
from datetime import datetime

from scan import Spectrometer, NNO_FILE_REF_CAL_COEFF, NNO_FILE_SCAN_DATA
from spectrum_library import scan_interpret
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from reference_data import REFERENCE_WAVELENGTHS, REFERENCE_SIGNAL
from model_data import W1, B1, W2, B2, MU, SIGMA, CLASS_NAMES

app = FastAPI(title="NIRScan Nano Web Interface", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el estado del sensor
spectrometer = None
device_connected = False
scan_data = None
reference_data = None
interpreted_data = None

# Interpolador de referencia (constante, se construye una sola vez)
_ref_interpolator = interp1d(
    REFERENCE_WAVELENGTHS, REFERENCE_SIGNAL,
    kind='linear', fill_value='extrapolate'
)
print(f"Referencia cargada: {len(REFERENCE_WAVELENGTHS)} puntos, rango {REFERENCE_WAVELENGTHS[0]:.1f} - {REFERENCE_WAVELENGTHS[-1]:.1f} nm")

def compute_reflectance(sample_wavelengths, sample_intensities):
    """Calcular reflectancia interpolando la referencia a los wavelengths de la muestra"""
    ref_at_sample = _ref_interpolator(sample_wavelengths)
    ref_at_sample = np.where(ref_at_sample == 0, 1e-10, ref_at_sample)
    return np.array(sample_intensities) / ref_at_sample

def compute_absorbance(reflectance):
    """Calcular absorbancia desde reflectancia: A = -log10(R)"""
    r_clipped = np.clip(reflectance, 1e-10, None)
    return -np.log10(r_clipped)

def predict_mastitis(reflectance_sg):
    """Predecir mastitis usando la red neuronal extraida de model.mat.
    Input: reflectancia filtrada con Savitzky-Golay (228 puntos).
    Output: dict con clase, probabilidades y confianza.
    """
    x_std = (reflectance_sg - MU) / SIGMA
    hidden = np.maximum(0, W1 @ x_std + B1)  # ReLU
    logits = W2 @ hidden + B2
    exp_logits = np.exp(logits - logits.max())  # Softmax estable
    probs = exp_logits / exp_logits.sum()
    pred_idx = int(np.argmax(probs))
    return {
        "class": CLASS_NAMES[pred_idx],
        "class_index": pred_idx,
        "probability_sana": round(float(probs[0]) * 100, 2),
        "probability_mastitis": round(float(probs[1]) * 100, 2),
        "confidence": round(float(probs[pred_idx]) * 100, 2)
    }
print(f"Modelo cargado: {W1.shape[1]} inputs -> {W1.shape[0]} hidden -> {W2.shape[0]} clases ({', '.join(CLASS_NAMES)})")

# Crear directorios necesarios
def ensure_directories():
    """Crear directorios necesarios si no existen"""
    directories = ['static', 'static/data', 'static/json', 'static/csv', 'static/plots']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

ensure_directories()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Servir la página principal"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/status")
async def get_status():
    """Obtener estado actual del sistema"""
    global device_connected, scan_data, interpreted_data
    
    return {
        "device_connected": device_connected,
        "scan_data_available": scan_data is not None,
        "interpreted_data_available": interpreted_data is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/check-connection")
async def check_connection():
    """Verificar conectividad con el sensor"""
    global spectrometer, device_connected
    
    try:
        print("Intentando conectar al dispositivo NIRScan Nano...")
        spectrometer = Spectrometer(0x0451, 0x4200)  # NIRScan Nano VendorID/ProductID
        
        if spectrometer.connected_flag:
            device_connected = True
            return {
                "success": True,
                "message": "Dispositivo conectado exitosamente!",
                "vendor_id": "0x0451",
                "product_id": "0x4200"
            }
        else:
            device_connected = False
            return {
                "success": False,
                "message": "No se pudo conectar al dispositivo"
            }
            
    except Exception as e:
        device_connected = False
        return {
            "success": False,
            "message": f"Error al conectar: {str(e)}"
        }

@app.post("/api/perform-scan")
async def perform_scan():
    """Realizar escaneo del sensor"""
    global spectrometer, device_connected, scan_data, reference_data, interpreted_data
    
    if not device_connected:
        raise HTTPException(status_code=400, detail="Dispositivo no conectado")
    
    try:
        print("🔄 Iniciando escaneo...")
        start_time = time.time()
        
        # Realizar escaneo
        spectrometer.perform_scan()
        
        # Obtener datos del escaneo
        print("📥 Obteniendo datos del escaneo...")
        scan_data = spectrometer.get_file(NNO_FILE_SCAN_DATA)
        
        # Obtener datos de calibración
        print("📥 Obteniendo datos de calibración...")
        reference_data = spectrometer.get_file(NNO_FILE_REF_CAL_COEFF)
        
        scan_time = time.time() - start_time
        
        # Interpretar datos automáticamente
        print("🔄 Interpretando datos del espectro...")
        data_json = scan_interpret(scan_data)
        interpreted_data = json.loads(data_json)
        
        # Calcular reflectancia con filtro Savitzky-Golay
        n = interpreted_data['length']
        wavelengths = np.array(interpreted_data['wavelength'][:n])
        intensities = np.array(interpreted_data['intensity'][:n])
        reflectance = compute_reflectance(wavelengths, intensities)
        window_length = min(11, n if n % 2 == 1 else n - 1)
        reflectance_sg = savgol_filter(reflectance, window_length, 3)

        # Absorbancia con filtro SG
        absorbance = compute_absorbance(reflectance)
        absorbance_sg = savgol_filter(absorbance, window_length, 3)

        # Prediccion de mastitis
        prediction = predict_mastitis(reflectance_sg)

        return {
            "success": True,
            "message": f"Escaneo completado en {scan_time:.2f} segundos",
            "spectrum_length": n,
            "wavelength_range": f"{wavelengths[0]:.2f} - {wavelengths[-1]:.2f} nm",
            "chart_data": {
                "wavelengths": wavelengths.tolist(),
                "reflectance": reflectance.tolist(),
                "reflectance_sg": reflectance_sg.tolist(),
                "absorbance": absorbance.tolist(),
                "absorbance_sg": absorbance_sg.tolist()
            },
            "prediction": prediction
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error durante el escaneo: {str(e)}"
        }

@app.post("/api/save-data")
async def save_data(filename: str):
    """Guardar datos en múltiples formatos"""
    global scan_data, reference_data, interpreted_data
    
    if interpreted_data is None:
        raise HTTPException(status_code=400, detail="No hay datos para guardar")
    
    if not filename.strip():
        raise HTTPException(status_code=400, detail="El nombre del archivo no puede estar vacío")
    
    try:
        # Obtener timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        saved_files = []
        
        # Guardar archivo .dat combinado
        if scan_data and reference_data:
            byte_file_combined = bytearray(scan_data + reference_data)
            dat_filename = f"static/data/{safe_filename}_{timestamp}.dat"
            with open(dat_filename, "wb") as f:
                f.write(byte_file_combined)
            saved_files.append(dat_filename)
        
        # Guardar JSON
        json_filename = f"static/json/{safe_filename}_{timestamp}.json"
        with open(json_filename, "w", encoding='utf-8') as f:
            json.dump(interpreted_data, f, indent=2, ensure_ascii=False)
        saved_files.append(json_filename)
        
        # Guardar CSV con reflectancia y absorbancia
        csv_filename = f"static/csv/{safe_filename}_{timestamp}.csv"
        n = interpreted_data['length']
        wl = np.array(interpreted_data['wavelength'][:n])
        inten = np.array(interpreted_data['intensity'][:n])
        refl = compute_reflectance(wl, inten)
        window_length = min(11, n if n % 2 == 1 else n - 1)
        refl_sg = savgol_filter(refl, window_length, 3)
        absor = compute_absorbance(refl)
        df = pd.DataFrame({
            'wavelength_nm': wl,
            'intensity': inten,
            'reflectance': refl,
            'reflectance_savgol': refl_sg,
            'absorbance': absor
        })
        df.to_csv(csv_filename, index=False)
        saved_files.append(csv_filename)
        
        # Guardar gráfico PNG
        plot_filename = f"static/plots/{safe_filename}_{timestamp}.png"
        create_and_save_plot(interpreted_data, safe_filename, plot_filename)
        saved_files.append(plot_filename)
        
        return {
            "success": True,
            "message": f"Datos guardados exitosamente con el nombre: {safe_filename}",
            "files": saved_files,
            "timestamp": timestamp
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al guardar datos: {str(e)}"
        }

def create_and_save_plot(data, filename, filepath):
    """Crear y guardar gráfico con reflectancia y filtro Savitzky-Golay"""
    try:
        n = data["length"]
        wavelengths = np.array(data["wavelength"][:n])
        intensities = np.array(data["intensity"][:n])

        reflectance = compute_reflectance(wavelengths, intensities)
        window_length = min(11, n if n % 2 == 1 else n - 1)
        reflectance_sg = savgol_filter(reflectance, window_length, 3)

        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        axes[0].plot(wavelengths, intensities, linewidth=1.5, color='blue')
        axes[0].set_title(f'Espectro NIR - {filename} - Intensidad', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Intensidad (ADC)', fontsize=12)
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(wavelengths, reflectance, linewidth=1, color='gray', alpha=0.5, label='Reflectancia')
        axes[1].plot(wavelengths, reflectance_sg, linewidth=2, color='red', label='Reflectancia (Savitzky-Golay)')
        axes[1].set_title(f'Espectro NIR - {filename} - Reflectancia', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Reflectancia (R)', fontsize=12)
        axes[1].set_xlabel('Longitud de Onda (nm)', fontsize=12)
        axes[1].legend(fontsize=11)
        axes[1].grid(True, alpha=0.3)

        scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.02, 0.01, f'Escaneo: {scan_timestamp} | Filtro SG: window=11, poly=3', fontsize=9, style='italic')
        fig.tight_layout(rect=[0, 0.03, 1, 1])

        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

    except Exception as e:
        print(f"Error al guardar gráfico: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
