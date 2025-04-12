from flask import Flask, request, jsonify
import torch
import torch.nn as nn
import joblib
import numpy as np
import pennylane as qml

# Load scaler
scaler = joblib.load("scaler.pkl")

# Quantum circuit and model definition (same as training)
n_qubits = 10  # set to the number you used during training
dev = qml.device("default.qubit", wires=n_qubits)

@qml.qnode(dev, interface="torch")
def quantum_circuit(inputs, weights):
    qml.AngleEmbedding(features=inputs, wires=range(n_qubits))
    qml.StronglyEntanglingLayers(weights, wires=range(n_qubits))
    return qml.expval(qml.PauliZ(0))

class QuantumFraudDetector(nn.Module):
    def __init__(self, n_qubits, n_layers):
        super().__init__()
        self.n_layers = n_layers
        self.weight_shapes = {"weights": (n_layers, n_qubits, 3)}
        self.qnode = qml.qnn.TorchLayer(quantum_circuit, self.weight_shapes)

    def forward(self, x):
        return torch.sigmoid(self.qnode(x))

# Initialize model and load weights
n_layers = 3
model = QuantumFraudDetector(n_qubits, n_layers)
model.load_state_dict(torch.load("model.pth", map_location=torch.device("cpu")))
model.eval()

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Quantum Fraud Detection API is running"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get JSON input
        input_data = request.get_json()
        features = np.array(input_data["features"]).reshape(1, -1)

        # Scale input
        scaled = scaler.transform(features)

        # Convert to tensor
        input_tensor = torch.tensor(scaled, dtype=torch.float32)

        # Predict
        with torch.no_grad():
            output = model(input_tensor).item()

        prediction = int(output > 0.5)

        return jsonify({
            "prediction": prediction,
            "confidence": float(output)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
