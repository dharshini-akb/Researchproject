import shap
import pandas as pd
import numpy as np
import torch
from typing import Dict
from config import system_config
from utils import logger
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel

log = logger.get_logger("shap_explainer")

class RareDiseaseExplainer:
    def __init__(self):
        self.rf_explainer = None
        self.background_data = None

    def initialize_rf_explainer(self, rf_model: RandomForestModel, background_data: pd.DataFrame):
        """
        Initializes the TreeExplainer for Random Forest.
        """
        log.info("Initializing SHAP TreeExplainer for Random Forest...")
        self.background_data = background_data
        # We explain the underlying tree classifier
        self.rf_explainer = shap.TreeExplainer(rf_model.model, data=background_data)
        log.info("Random Forest TreeExplainer initialized successfully.")

    def explain_patient_rf(self, patient_df: pd.DataFrame) -> Dict[int, Dict[str, float]]:
        """
        Computes local SHAP values for a single patient across all 3 classes.
        Returns a dict: {class_index: {feature_name: shap_value}}
        """
        if self.rf_explainer is None:
            raise ValueError("RF Explainer is not initialized.")
            
        # shap_values shape: list of 3 arrays (one per class), each [1, num_features]
        # or an array of shape [1, num_features, 3] depending on shap version
        shap_values_raw = self.rf_explainer.shap_values(patient_df)
        
        # Check output structure (list vs numpy array)
        if isinstance(shap_values_raw, list):
            # One array per class
            shap_values = shap_values_raw
        else:
            # Shape is [1, num_features, 3] -> transpose to list of [num_features]
            shap_values = [shap_values_raw[0, :, c] for c in range(3)]
            
        features = list(patient_df.columns)
        local_explanations = {}
        
        for c in range(3):
            class_shaps = shap_values[c]
            # If multi-dimensional, flatten it
            if len(class_shaps.shape) > 1:
                class_shaps = class_shaps[0]
                
            local_explanations[c] = {
                features[i]: float(class_shaps[i])
                for i in range(len(features))
            }
            
        return local_explanations

    def get_global_importance_rf(self, X: pd.DataFrame) -> Dict[int, Dict[str, float]]:
        """
        Computes average absolute SHAP value for each feature, per class.
        """
        if self.rf_explainer is None:
            raise ValueError("RF Explainer is not initialized.")
            
        log.info("Computing global SHAP values for Random Forest...")
        shap_values_raw = self.rf_explainer.shap_values(X)
        
        if isinstance(shap_values_raw, list):
            shap_values = shap_values_raw
        else:
            shap_values = [shap_values_raw[:, :, c] for c in range(3)]
            
        features = list(X.columns)
        global_importance = {}
        
        for c in range(3):
            # Calculate mean absolute SHAP value
            mean_abs_shap = np.mean(np.abs(shap_values[c]), axis=0)
            global_importance[c] = {
                features[i]: float(mean_abs_shap[i])
                for i in range(len(features))
            }
            
        return global_importance

    def explain_patient_tabnet(self, tabnet_model: TabNetModel, patient_df: pd.DataFrame) -> Dict[str, float]:
        """
        Extracts the native local attention mask importances from TabNet for a patient.
        """
        log.info("Extracting local attention from TabNet...")
        tabnet_model.model.eval()
        X_tensor = torch.tensor(patient_df.values, dtype=torch.float32).to(tabnet_model.device)
        
        with torch.no_grad():
            _, masks, _ = tabnet_model.model(X_tensor)
            
        # Aggregate across steps
        stacked_masks = torch.stack(masks, dim=0) # [n_steps, 1, num_features]
        # Average across steps
        avg_mask = stacked_masks.mean(dim=0).squeeze(0).cpu().numpy() # [num_features]
        
        # Normalize
        if avg_mask.sum() > 0:
            avg_mask = avg_mask / avg_mask.sum()
            
        features = list(patient_df.columns)
        return {features[i]: float(avg_mask[i]) for i in range(len(features))}
