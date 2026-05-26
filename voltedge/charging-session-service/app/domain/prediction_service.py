from dataclasses import dataclass
from datetime import datetime, timezone
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import logging

logger = logging.getLogger("voltedge.charging-session")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.joblib")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "risk_encoder.joblib")

# Value Object — input features til ML model
@dataclass(frozen=True)
class ChargerFeatures:
    charger_id: str
    total_incidents_24h: int
    critical_count_24h: int
    high_count_24h: int
    critical_ratio: float
    avg_value: float

# Value Object — forudsigelsesresultat
@dataclass(frozen=True)
class PredictionResult:
    charger_id: str
    risk_score: float
    risk_level: str
    recommendation: str
    based_on_incidents: int
    predicted_at: datetime

def _generate_training_data():
    """
    Genererer syntetiske træningsdata baseret på realistiske VoltEdge-mønstre.
    Labels: low, medium, high, critical
    """
    np.random.seed(42)
    X, y = [], []

    # LOW risk — få incidents, ingen kritiske, normal belastning
    for _ in range(200):
        total = np.random.randint(0, 2)
        critical = 0
        high = np.random.randint(0, 2)
        ratio = 0.0
        avg_val = np.random.uniform(0, 10)
        X.append([total, critical, high, ratio, avg_val])
        y.append("low")

    # MEDIUM risk — nogle incidents, få høje, moderat belastning
    for _ in range(200):
        total = np.random.randint(2, 4)
        critical = 0
        high = np.random.randint(1, 3)
        ratio = np.random.uniform(0, 0.25)
        avg_val = np.random.uniform(10, 22)
        X.append([total, critical, high, ratio, avg_val])
        y.append("medium")

    # HIGH risk — mange incidents, nogle kritiske, høj belastning
    for _ in range(200):
        total = np.random.randint(3, 6)
        critical = np.random.randint(1, 3)
        high = np.random.randint(1, 4)
        ratio = np.random.uniform(0.25, 0.5)
        avg_val = np.random.uniform(22, 40)
        X.append([total, critical, high, ratio, avg_val])
        y.append("high")

    # CRITICAL risk — mange incidents, overvægt af kritiske, meget høj belastning
    for _ in range(200):
        total = np.random.randint(5, 10)
        critical = np.random.randint(3, 7)
        high = np.random.randint(1, 4)
        ratio = np.random.uniform(0.5, 1.0)
        avg_val = np.random.uniform(40, 80)
        X.append([total, critical, high, ratio, avg_val])
        y.append("critical")

    return np.array(X), np.array(y)

def train_and_save_model():
    """Træner RandomForest model og gemmer den til disk."""
    logger.info("Træner ML risikomodel...")
    X, y = _generate_training_data()

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X, y_encoded)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    logger.info(f"ML model gemt: {MODEL_PATH}")

    return model, encoder

def load_or_train_model():
    """Loader model fra disk, eller træner en ny hvis den ikke findes."""
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        logger.info("Loader eksisterende ML model fra disk")
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
    else:
        logger.info("Ingen model fundet — træner ny model")
        model, encoder = train_and_save_model()
    return model, encoder

RECOMMENDATIONS = {
    "critical": "kræver øjeblikkelig inspektion",
    "high": "bør inspiceres inden for 4 timer",
    "medium": "bør overvåges tæt",
    "low": "ser ud til at fungere normalt"
}

# Domain Service — forudsiger risiko via ML model
class PredictionService:

    def __init__(self):
        self.model, self.encoder = load_or_train_model()

    def predict(self, features: ChargerFeatures) -> PredictionResult:
        X = np.array([[
            features.total_incidents_24h,
            features.critical_count_24h,
            features.high_count_24h,
            features.critical_ratio,
            features.avg_value
        ]])

        probabilities = self.model.predict_proba(X)[0]
        predicted_index = np.argmax(probabilities)
        risk_level = self.encoder.inverse_transform([predicted_index])[0]
        risk_score = round(float(np.max(probabilities)), 2)

        return PredictionResult(
            charger_id=features.charger_id,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendation=f"Lader {features.charger_id} {RECOMMENDATIONS[risk_level]}",
            based_on_incidents=features.total_incidents_24h,
            predicted_at=datetime.now(timezone.utc)
        )