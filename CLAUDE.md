# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web interface for the DLP NIRScan Nano EVM (Texas Instruments NIR sensor) used in the **Proyecto Smart Milk** at Universidad Nacional de Frontera (Sullana, Peru). The system acquires NIR spectra from milk samples (900-1700nm), computes reflectance/absorbance, and classifies samples as healthy or mastitis-affected using a neural network.

## Running the Application

```bash
pip install -r requirements.txt
python main.py
# Server starts at http://localhost:8000
```

**Platform note:** The sensor communication layer (`spectrum_library.py`) depends on `dlpspec.dll` (TI DLP Spectrum Library), hardcoded to `C:/ti/DLPSpectrumLibrary_2.0.3/src/dlpspec.dll`. This only works on Windows with the TI SDK installed. The web UI, data processing, and ML prediction work on any platform.

## Architecture

**FastAPI backend** (`main.py`) serves a single-page HTML frontend (`templates/index.html`) with Plotly.js interactive charts.

### Data Pipeline

```
Sensor (USB HID) → scan.py → raw bytes
    → spectrum_library.py (ctypes → dlpspec.dll) → wavelength[] + intensity[]
    → main.py: reflectance = intensity / reference_signal (from reference_data.py)
    → Savitzky-Golay filter (scipy, window=11, poly=3)
    → predict_mastitis() using neural network weights (from model_data.py)
    → JSON response with chart_data + prediction → Plotly.js renders in browser
```

### Key Modules

- **`main.py`** — FastAPI app, all API endpoints, signal processing (reflectance, absorbance, SG filter), ML prediction
- **`scan.py`** — `Spectrometer` class, USB HID communication with NIRScan Nano (VID `0x0451`, PID `0x4200`)
- **`usb.py`** — Low-level HID read/write command construction
- **`util.py`** — Byte manipulation utilities (`shiftBytes`)
- **`spectrum_library.py`** — ctypes wrapper for `dlpspec_scan_interpret()`, defines `scanResults` C struct
- **`reference_data.py`** — 228-point reference signal (wavelengths + intensities from cal2.xlsx), used to compute reflectance
- **`model_data.py`** + **`model_weights.npz`** — Neural network extracted from MATLAB `model.mat` (ClassificationNeuralNetwork)
- **`templates/index.html`** — Complete frontend: Plotly.js charts, prediction panel, sensor controls

### ML Model

Extracted from MATLAB's `ClassificationNeuralNetwork`. Architecture: 228 inputs → 15 hidden (ReLU) → 2 outputs (Softmax). Classes: "Sana" / "Mastitis". Input is SG-filtered reflectance spectrum, standardized with embedded Mu/Sigma.

### API Endpoints

- `GET /` — Serve index.html
- `GET /api/status` — Connection and data state
- `POST /api/check-connection` — Initialize USB HID connection to sensor
- `POST /api/perform-scan` — Full pipeline: scan → interpret → reflectance → filter → predict → return chart_data + prediction
- `POST /api/save-data?filename=X` — Save to static/{data,json,csv,plots}/

### State

Backend uses global variables (`spectrometer`, `device_connected`, `scan_data`, `reference_data`, `interpreted_data`). Single-user, not thread-safe.

## Output File Format

Files saved as `{sanitized_name}_{YYYYMMDD_HHMMSS}.{ext}`. CSV includes columns: `wavelength_nm`, `intensity`, `reflectance`, `reflectance_savgol`, `absorbance`. DAT files are raw binary concatenation of scan_data + reference calibration bytes from the device.

## Language

UI and code comments are in Spanish. The project targets a Spanish-speaking research team.
