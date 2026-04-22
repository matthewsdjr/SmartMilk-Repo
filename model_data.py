"""
Modelos de prediccion extraidos de archivos MATLAB .mat

Modelo de clasificacion (mastitis):
  ClassificationNeuralNetwork: 228 -> 15 (ReLU) -> 2 (Softmax)

Modelos de regresion (calidad de leche):
  Neural Network Toolbox: 228 -> 15 (tansig) -> 1 (purelin)
  Con normalizacion mapminmax en entrada y salida.
"""
import numpy as np
from pathlib import Path

_models_dir = Path(__file__).parent / "models"

# --- Modelo de clasificacion: Mastitis ---
_cls = np.load(_models_dir / "model_weights.npz")
W1 = _cls["W1"]        # (15, 228)
B1 = _cls["B1"]        # (15,)
W2 = _cls["W2"]        # (2, 15)
B2 = _cls["B2"]        # (2,)
MU = _cls["MU"]        # (228,) media para estandarizacion
SIGMA = _cls["SIGMA"]  # (228,) desv. estandar para estandarizacion
CLASS_NAMES = ["Sana", "Mastitis"]

# --- Modelos de regresion: calidad de leche ---
# Input: reflectancia con filtro Savitzky-Golay (window=19, poly=2)
# Normalizacion: mapminmax en entrada y salida

def _load_model(filename, label, unit, display_range):
    data = np.load(_models_dir / filename)
    ymin = data["output_ymin"].item()
    ymax = data["output_ymax"].item()
    return {
        "label": label, "unit": unit,
        "range": (ymin, ymax),
        "display_range": display_range,
        "W1": data["W1"], "B1": data["B1"],
        "W2": data["W2"], "B2": data["B2"].item(),
        "input_xoffset": data["input_xoffset"],
        "input_gain": data["input_gain"],
        "output_gain": 2.0 / (ymax - ymin),
        "output_xoffset": ymin,
    }

MODEL_GRASA    = _load_model("grasa_model.npz",  "Grasa",           "%",   (0, 6))
MODEL_ADAGUA   = _load_model("adagua_model.npz", "Adicion de Agua", "%",   (0, 30))
MODEL_DENSIDAD = _load_model("dens_model.npz",   "Densidad",        "g/L", (15, 40))
MODEL_LACTOSA  = _load_model("lact_model.npz",   "Lactosa",         "%",   (0, 7))
MODEL_SNG      = _load_model("sng_model.npz",    "SNG",             "%",   (5, 12))
