from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseModel(ABC):
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        """Fits the model on training data."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts target classes."""
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts class probabilities."""
        pass

    @abstractmethod
    def save(self, filepath: str):
        """Serializes the model to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str):
        """Deserializes the model from disk."""
        pass
