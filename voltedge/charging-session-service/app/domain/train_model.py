"""
Kør dette script manuelt for at (gen)træne ML modellen:
    python -m app.domain.train_model
"""
from app.domain.prediction_service import train_and_save_model
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    train_and_save_model()
    print("Model trænet og gemt.")