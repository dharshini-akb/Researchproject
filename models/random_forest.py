import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from models.base_model import BaseModel
from config import system_config
from utils import logger

log = logger.get_logger("random_forest")

class RandomForestModel(BaseModel):
    def __init__(self):
        self.model = None
        self.calibrated_model = None
        self.feature_names = None

    def fit(self, X: pd.DataFrame, y: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        """
        Fits the Random Forest Classifier on training data and performs probability calibration using validation set.
        """
        self.feature_names = list(X.columns)
        
        # Instantiate Random Forest
        rf_kwargs = system_config.RF_PARAMS.copy()
        log.info(f"Instantiating Random Forest model with params: {rf_kwargs}")
        self.model = RandomForestClassifier(**rf_kwargs)
        
        # Fit Base Model
        log.info("Fitting base Random Forest model...")
        self.model.fit(X, y)
        
        # Fit Calibrated Classifier on training data
        log.info("Fitting calibrated Random Forest classifier (using 5-fold cross-validation calibration)...")
        self.calibrated_model = CalibratedClassifierCV(
            estimator=self.model,
            method='sigmoid',
            cv=5
        )
        # We fit the calibrated model on the training data
        self.calibrated_model.fit(X, y)
        log.info("Random Forest fitting and calibration completed.")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.calibrated_model is None:
            raise ValueError("Model is not fitted yet.")
        return self.calibrated_model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.calibrated_model is None:
            raise ValueError("Model is not fitted yet.")
        return self.calibrated_model.predict_proba(X)

    def save(self, filepath: str):
        """
        Saves the model to a joblib file.
        """
        log.info(f"Saving Random Forest model to {filepath}...")
        state = {
            "model": self.model,
            "calibrated_model": self.calibrated_model,
            "feature_names": self.feature_names
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(state, filepath)
        log.info("Model saved successfully.")

    def load(self, filepath: str):
        """
        Loads the model from a joblib file.
        """
        log.info(f"Loading Random Forest model from {filepath}...")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at {filepath}")
        state = joblib.load(filepath)
        self.model = state["model"]
        self.calibrated_model = state["calibrated_model"]
        self.feature_names = state["feature_names"]
        log.info("Model loaded successfully.")
