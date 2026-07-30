import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from models.base_model import BaseModel
from config import system_config
from utils import logger

log = logger.get_logger("tabnet")

# --- Custom PyTorch TabNet Architecture ---

class GhostBatchNorm(nn.Module):
    """
    Ghost Batch Normalization (splits input batch into virtual mini-batches to improve generalization).
    """
    def __init__(self, input_dim: int, virtual_batch_size: int = 16, momentum: float = 0.02):
        super().__init__()
        self.virtual_batch_size = virtual_batch_size
        self.bn = nn.BatchNorm1d(input_dim, momentum=momentum)

    def forward(self, x):
        if self.training and x.shape[0] > self.virtual_batch_size:
            splits = x.chunk(int(np.ceil(x.shape[0] / self.virtual_batch_size)), dim=0)
            x_conv = torch.cat([self.bn(s) for s in splits], dim=0)
            return x_conv
        return self.bn(x)


class GLU_Block(nn.Module):
    """
    Gated Linear Unit block.
    """
    def __init__(self, input_dim: int, output_dim: int, virtual_batch_size: int = 16):
        super().__init__()
        self.linear = nn.Linear(input_dim, output_dim * 2, bias=False)
        self.gbn = GhostBatchNorm(output_dim * 2, virtual_batch_size=virtual_batch_size)

    def forward(self, x):
        x = self.linear(x)
        x = self.gbn(x)
        out, gate = x.chunk(2, dim=-1)
        return out * torch.sigmoid(gate)


class FeatureTransformer(nn.Module):
    """
    Feature Transformer consisting of shared and independent GLU blocks.
    """
    def __init__(self, input_dim: int, output_dim: int, shared_layers: int = 2, independent_layers: int = 2, virtual_batch_size: int = 16):
        super().__init__()
        
        # Shared blocks
        self.shared = nn.ModuleList()
        in_d = input_dim
        for _ in range(shared_layers):
            self.shared.append(GLU_Block(in_d, output_dim, virtual_batch_size))
            in_d = output_dim
            
        # Independent blocks
        self.independent = nn.ModuleList()
        for _ in range(independent_layers):
            self.independent.append(GLU_Block(output_dim, output_dim, virtual_batch_size))

    def forward(self, x):
        # Pass through shared blocks
        for block in self.shared:
            x = block(x)
        # Pass through independent blocks with residual connections
        for block in self.independent:
            x = (x + block(x)) * np.sqrt(0.5)
        return x


class AttentionTransformer(nn.Module):
    """
    Attention Transformer for generating sparse selection masks.
    """
    def __init__(self, input_dim: int, output_dim: int, virtual_batch_size: int = 16):
        super().__init__()
        self.linear = nn.Linear(input_dim, output_dim, bias=False)
        self.gbn = GhostBatchNorm(output_dim, virtual_batch_size=virtual_batch_size)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x, prior):
        x = self.linear(x)
        x = self.gbn(x)
        # Apply prior scale to attention to avoid selecting same feature repeatedly
        x = x * prior
        # Use Softmax (standard alternative to Sparsemax for attention mapping)
        return self.softmax(x)


class TabNetCore(nn.Module):
    """
    Core TabNet PyTorch Model.
    """
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        n_d: int = 16,
        n_a: int = 16,
        n_steps: int = 3,
        gamma: float = 1.3,
        n_shared: int = 2,
        n_independent: int = 2,
        virtual_batch_size: int = 16
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.n_d = n_d
        self.n_a = n_a
        self.n_steps = n_steps
        self.gamma = gamma
        
        # Initial Ghost BN for input
        self.initial_bn = GhostBatchNorm(input_dim, virtual_batch_size=virtual_batch_size)
        
        # Feature Transformer (maps inputs to n_d + n_a)
        self.feature_transformer = FeatureTransformer(
            input_dim=input_dim,
            output_dim=n_d + n_a,
            shared_layers=n_shared,
            independent_layers=n_independent,
            virtual_batch_size=virtual_batch_size
        )
        
        # Attention Transformers
        self.attention_transformers = nn.ModuleList([
            AttentionTransformer(n_a, input_dim, virtual_batch_size=virtual_batch_size)
            for _ in range(n_steps)
        ])
        
        # Final classification linear layer
        self.final_linear = nn.Linear(n_d, output_dim)

    def forward(self, x):
        # Initial BN
        x = self.initial_bn(x)
        
        # Initialize prior
        prior = torch.ones_like(x)
        
        # Initialize outputs
        steps_output = []
        masks = []
        
        # Initialize decision/attention state (step 0 starts with all zeros as state)
        # We pass it through a feature transformer to generate initial n_a state
        initial_features = self.feature_transformer(x)
        state = initial_features[:, self.n_d:]  # n_a part
        
        # Sparsity loss accumulator
        sparsity_loss = 0.0
        
        for step in range(self.n_steps):
            # 1. Get attention mask
            mask = self.attention_transformers[step](state, prior)
            masks.append(mask)
            
            # Update sparsity regularization
            # Entropy calculation for mask to encourage sparsity
            step_entropy = -torch.sum(mask * torch.log(mask + 1e-10), dim=-1)
            sparsity_loss += torch.mean(step_entropy)
            
            # Update prior (penalize features already selected)
            prior = prior * (self.gamma - mask)
            
            # 2. Apply attention mask to input features
            masked_x = x * mask
            
            # 3. Process masked features
            step_features = self.feature_transformer(masked_x)
            
            # Separate decision part (n_d) and attention state part (n_a)
            d_part = step_features[:, :self.n_d]
            state = step_features[:, self.n_d:]
            
            # Add to decision representation
            # Apply ReLU to keep outputs positive/stable
            steps_output.append(torch.relu(d_part))
            
        # Combine decisions from all steps
        combined_decision = sum(steps_output)
        
        # Classify
        logits = self.final_linear(combined_decision)
        
        return logits, masks, sparsity_loss

# --- BaseModel Wrapper Class ---

class TabNetModel(BaseModel):
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def fit(self, X: pd.DataFrame, y: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        """
        Fits TabNet classifier using PyTorch training loop.
        """
        self.feature_names = list(X.columns)
        input_dim = len(self.feature_names)
        
        params = system_config.TABNET_PARAMS.copy()
        log.info(f"Instantiating TabNet core model on device: {self.device}")
        
        # Instantiate TabNet Core PyTorch model
        self.model = TabNetCore(
            input_dim=input_dim,
            output_dim=params["output_dim"],
            n_d=params["n_d"],
            n_a=params["n_a"],
            n_steps=params["n_steps"],
            gamma=params["gamma"],
            n_shared=params["n_shared"],
            n_independent=params["n_independent"]
        ).to(self.device)
        
        # Convert pandas datasets to Tensors
        X_train_tensor = torch.tensor(X.values, dtype=torch.float32).to(self.device)
        y_train_tensor = torch.tensor(y.values, dtype=torch.long).to(self.device)
        
        if X_val is not None and y_val is not None:
            X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32).to(self.device)
            y_val_tensor = torch.tensor(y_val.values, dtype=torch.long).to(self.device)
        else:
            X_val_tensor, y_val_tensor = None, None
            
        # Optimizer and loss function
        optimizer = optim.Adam(self.model.parameters(), lr=params["learning_rate"], weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        batch_size = params["batch_size"]
        epochs = params["epochs"]
        lambda_sparse = params["lambda_sparse"]
        
        log.info("Starting TabNet training epochs...")
        self.model.train()
        
        for epoch in range(epochs):
            # Mini-batch loop
            permutation = torch.randperm(X_train_tensor.size()[0])
            epoch_loss = 0.0
            
            for i in range(0, X_train_tensor.size()[0], batch_size):
                optimizer.zero_grad()
                indices = permutation[i:i+batch_size]
                batch_x, batch_y = X_train_tensor[indices], y_train_tensor[indices]
                
                logits, _, sparsity_loss = self.model(batch_x)
                
                # Cross-entropy loss + sparsity loss
                loss = criterion(logits, batch_y) + lambda_sparse * sparsity_loss
                
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * len(batch_y)
                
            epoch_loss /= len(X_train_tensor)
            
            # Validation evaluation
            if (epoch + 1) % 25 == 0 or epoch == epochs - 1:
                val_str = ""
                if X_val_tensor is not None:
                    self.model.eval()
                    with torch.no_grad():
                        val_logits, _, _ = self.model(X_val_tensor)
                        val_loss = criterion(val_logits, y_val_tensor).item()
                        val_preds = val_logits.argmax(dim=-1)
                        val_acc = (val_preds == y_val_tensor).float().mean().item()
                        val_str = f" | Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.4f}"
                    self.model.train()
                log.info(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.4f}{val_str}")
                
        log.info("TabNet training completed.")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not fitted yet.")
        self.model.eval()
        X_tensor = torch.tensor(X.values, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            logits, _, _ = self.model(X_tensor)
            preds = logits.argmax(dim=-1).cpu().numpy()
        return preds

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not fitted yet.")
        self.model.eval()
        X_tensor = torch.tensor(X.values, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            logits, _, _ = self.model(X_tensor)
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
        return probs

    def get_feature_importance_from_masks(self, X: pd.DataFrame) -> np.ndarray:
        """
        Extracts step-wise attention feature importance by aggregating the attention masks.
        """
        if self.model is None:
            raise ValueError("Model is not fitted yet.")
        self.model.eval()
        X_tensor = torch.tensor(X.values, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            _, masks, _ = self.model(X_tensor)
            
        # Aggregate masks across steps
        # masks is a list of Tensors of shape [batch_size, input_dim]
        # We can average them across patients and then sum/average across steps
        stacked_masks = torch.stack(masks, dim=0) # Shape: [n_steps, batch_size, input_dim]
        mean_masks = stacked_masks.mean(dim=1) # Shape: [n_steps, input_dim]
        total_importance = mean_masks.sum(dim=0).cpu().numpy() # Shape: [input_dim]
        
        # Normalize
        if total_importance.sum() > 0:
            total_importance = total_importance / total_importance.sum()
            
        return total_importance

    def save(self, filepath: str):
        """
        Saves PyTorch model weights and state dict.
        """
        log.info(f"Saving TabNet model weights to {filepath}...")
        state = {
            "model_state_dict": self.model.state_dict(),
            "feature_names": self.feature_names,
            "params": system_config.TABNET_PARAMS
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save(state, filepath)
        log.info("Model weights saved successfully.")

    def load(self, filepath: str):
        """
        Loads PyTorch model weights.
        """
        log.info(f"Loading TabNet model weights from {filepath}...")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at {filepath}")
        state = torch.load(filepath, map_location=self.device)
        self.feature_names = state["feature_names"]
        
        # Recreate core model
        params = state["params"]
        self.model = TabNetCore(
            input_dim=len(self.feature_names),
            output_dim=params["output_dim"],
            n_d=params["n_d"],
            n_a=params["n_a"],
            n_steps=params["n_steps"],
            gamma=params["gamma"],
            n_shared=params["n_shared"],
            n_independent=params["n_independent"]
        ).to(self.device)
        
        self.model.load_state_dict(state["model_state_dict"])
        self.model.eval()
        log.info("TabNet model weights loaded successfully.")
