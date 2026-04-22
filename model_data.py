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
_reg = np.load(_models_dir / "regression_models.npz")

def _load_reg(prefix, label, unit, display_range):
    ymin = _reg[f"{prefix}_output_ymin"].item()
    ymax = _reg[f"{prefix}_output_ymax"].item()
    return {
        "label": label, "unit": unit,
        "range": (ymin, ymax),
        "display_range": display_range,
        "W1": _reg[f"{prefix}_W1"], "B1": _reg[f"{prefix}_B1"],
        "W2": _reg[f"{prefix}_W2"], "B2": _reg[f"{prefix}_B2"].item(),
        "input_xoffset": _reg[f"{prefix}_input_xoffset"],
        "input_gain": _reg[f"{prefix}_input_gain"],
        "output_gain": 2.0 / (ymax - ymin),
        "output_xoffset": ymin,
    }

REGRESSION_MODELS = {
    "grasa":    _load_reg("grasa",  "Grasa",            "%",   (0, 6)),
    "adagua":   _load_reg("adagua", "Adicion de Agua",  "%",   (0, 30)),
    "densidad": _load_reg("dens",   "Densidad",         "g/L", (15, 40)),
    "lactosa":  _load_reg("lact",   "Lactosa",          "%",   (0, 7)),
    "sng":      _load_reg("sng",    "SNG",              "%",   (5, 12)),
}
