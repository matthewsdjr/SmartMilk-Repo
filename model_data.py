"""
Modelo ClassificationNeuralNetwork extraido de model.mat
Red neuronal: 228 inputs -> 15 hidden (ReLU) -> 2 outputs (Softmax)
Clasificacion: vaca sana vs vaca con mastitis
"""
import numpy as np
from pathlib import Path

_data = np.load(Path(__file__).parent / "model_weights.npz")
W1 = _data["W1"]      # (15, 228)
B1 = _data["B1"]      # (15,)
W2 = _data["W2"]      # (2, 15)
B2 = _data["B2"]      # (2,)
MU = _data["MU"]      # (228,) media para estandarizacion
SIGMA = _data["SIGMA"]  # (228,) desv. estandar para estandarizacion

CLASS_NAMES = ["Sana", "Mastitis"]
