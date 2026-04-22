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
_reg = np.load(_models_dir / "regression_models.npz")

REGRESSION_MODELS = {
    "grasa": {
        "label": "Grasa",
        "unit": "%",
        "range": (0.23, 4.8),
        "display_range": (0, 6),
        "W1": _reg["grasa_W1"], "B1": _reg["grasa_B1"],
        "W2": _reg["grasa_W2"], "B2": _reg["grasa_B2"].item(),
        "input_xoffset": _reg["grasa_input_xoffset"],
        "input_gain": _reg["grasa_input_gain"],
        "output_gain": _reg["grasa_output_gain"].item(),
        "output_xoffset": _reg["grasa_output_xoffset"].item(),
    },
    "adagua": {
        "label": "Adicion de Agua",
        "unit": "%",
        "range": (0.38, 28.84),
        "display_range": (0, 30),
        "W1": _reg["adagua_W1"], "B1": _reg["adagua_B1"],
        "W2": _reg["adagua_W2"], "B2": _reg["adagua_B2"].item(),
        "input_xoffset": _reg["adagua_input_xoffset"],
        "input_gain": _reg["adagua_input_gain"],
        "output_gain": _reg["adagua_output_gain"].item(),
        "output_xoffset": _reg["adagua_output_xoffset"].item(),
    },
    "densidad": {
        "label": "Densidad",
        "unit": "g/L",
        "range": (15.32, 38.63),
        "display_range": (15, 40),
        "W1": _reg["dens_W1"], "B1": _reg["dens_B1"],
        "W2": _reg["dens_W2"], "B2": _reg["dens_B2"].item(),
        "input_xoffset": _reg["dens_input_xoffset"],
        "input_gain": _reg["dens_input_gain"],
        "output_gain": _reg["dens_output_gain"].item(),
        "output_xoffset": _reg["dens_output_xoffset"].item(),
    },
    "lactosa": {
        "label": "Lactosa",
        "unit": "%",
        "range": (2.93, 5.6),
        "display_range": (0, 7),
        "W1": _reg["lact_W1"], "B1": _reg["lact_B1"],
        "W2": _reg["lact_W2"], "B2": _reg["lact_B2"].item(),
        "input_xoffset": _reg["lact_input_xoffset"],
        "input_gain": _reg["lact_input_gain"],
        "output_gain": _reg["lact_output_gain"].item(),
        "output_xoffset": _reg["lact_output_xoffset"].item(),
    },
    "sng": {
        "label": "SNG",
        "unit": "%",
        "range": (5.78, 10.7),
        "display_range": (5, 12),
        "W1": _reg["sng_W1"], "B1": _reg["sng_B1"],
        "W2": _reg["sng_W2"], "B2": _reg["sng_B2"].item(),
        "input_xoffset": _reg["sng_input_xoffset"],
        "input_gain": _reg["sng_input_gain"],
        "output_gain": _reg["sng_output_gain"].item(),
        "output_xoffset": _reg["sng_output_xoffset"].item(),
    },
}
