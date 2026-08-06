import os
import sys
import glob
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image, ImageDraw, ImageFont
from sklearn.model_selection import train_test_split

# Setup workspace directory configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import system_config
from utils import logger

log = logger.get_logger("train_ocr")

# Define paths
DATASET_DIR = os.path.join(system_config.RAW_DATA_DIR, "doctors-handwritten-prescription-bd-dataset")
MODEL_DIR = os.path.join(system_config.WORKSPACE_DIR, "models", "custom_ocr")
os.makedirs(MODEL_DIR, exist_ok=True)

# Charset for OCR mapping
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- "
CHAR_TO_IDX = {char: idx + 1 for idx, char in enumerate(CHARSET)}
IDX_TO_CHAR = {idx + 1: char for idx, char in enumerate(CHARSET)}
CHAR_TO_IDX["blank"] = 0
IDX_TO_CHAR[0] = ""

# Model Configuration
IMG_WIDTH = 128
IMG_HEIGHT = 32

class OCRDataset(Dataset):
    def __init__(self, data_list, transform=None):
        self.data_list = data_list
        self.transform = transform

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        img_path, label = self.data_list[idx]
        
        # Load image or generate synthetic if path is a placeholder
        if isinstance(img_path, str) and os.path.exists(img_path):
            img = Image.open(img_path).convert('L')
        else:
            # Synthetic generation (dynamic backup)
            img = Image.new('L', (IMG_WIDTH, IMG_HEIGHT), color=255)
            draw = ImageDraw.Draw(img)
            # Simple text rendering
            draw.text((10, 8), label, fill=0)
            
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        img_arr = np.array(img, dtype=np.float32) / 255.0
        img_arr = np.expand_dims(img_arr, axis=0) # (1, H, W)
        
        # Tokenize label
        tokens = [CHAR_TO_IDX.get(c, CHAR_TO_IDX[" "]) for c in label]
        
        return torch.tensor(img_arr), torch.tensor(tokens, dtype=torch.long), torch.tensor(len(tokens), dtype=torch.long)

def collate_fn(batch):
    images, targets, target_lengths = zip(*batch)
    images = torch.stack(images, 0)
    target_lengths = torch.stack(target_lengths, 0)
    
    # Pad targets
    flat_targets = []
    for t in targets:
        flat_targets.extend(t.tolist())
    flat_targets = torch.tensor(flat_targets, dtype=torch.long)
    
    return images, flat_targets, target_lengths

class CRNN(nn.Module):
    def __init__(self, num_classes=len(CHARSET) + 1):
        super(CRNN, self).__init__()
        # CNN Feature Extractor
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2), # 64x16
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2), # 32x8
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d((2, 1), (2, 1)), # 32x4
            
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.MaxPool2d((2, 1), (2, 1)), # 32x2
        )
        # Sequence modeling
        self.rnn = nn.Sequential(
            nn.LSTM(512, 128, bidirectional=True, num_layers=2, batch_first=True, dropout=0.2)
        )
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        # x: (B, 1, 32, 128)
        features = self.cnn(x) # (B, 512, H, W)
        features = features.mean(dim=2) # (B, 512, W)
        features = features.permute(0, 2, 1) # (B, W, 512)
        
        # We need a linear layer or reduce dimension before LSTM
        # LSTM input size: 512
        rnn_out, _ = self.rnn(features) # (B, 32, 256)
        out = self.fc(rnn_out) # (B, 32, num_classes)
        
        # CTC Loss expects: (T, B, num_classes)
        out = out.permute(1, 0, 2)
        return out

def get_dataset_splits():
    # Attempt to locate Kaggle dataset images and structure
    data_list = []
    
    # We check if folder exists
    if os.path.exists(DATASET_DIR):
        log.info(f"Auditing Kaggle dataset folder at {DATASET_DIR}...")
        # Assume images are organized into subfolders by word class
        subfolders = [f for f in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, f))]
        
        for folder in subfolders:
            folder_path = os.path.join(DATASET_DIR, folder)
            # The folder name is the target label
            images = glob.glob(os.path.join(folder_path, "*.png")) + glob.glob(os.path.join(folder_path, "*.jpg"))
            for img_p in images:
                data_list.append((img_p, folder))
                
    if not data_list:
        log.warning("Kaggle prescription dataset not found or empty. Generating synthetic fallback data for demonstration...")
        # Fallback dataset: list of medicine names and clinical terms
        sample_words = [
            "Napa", "Aceta", "Zithrin", "Seclo", "Omeprazole", "Paracetamol", 
            "Amoxicillin", "Atorvastatin", "Metformin", "Amlodipine", "Albuterol",
            "delayed", "speech", "hypotonia", "poor", "contact", "seizures", "microcephaly"
        ]
        for _ in range(500):
            w = random.choice(sample_words)
            data_list.append(("synthetic_placeholder", w))
            
    # Stratified or randomized split
    # Since some classes might be sparse, we do a random split with seed
    random.seed(42)
    random.shuffle(data_list)
    
    n = len(data_list)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    
    train_data = data_list[:n_train]
    val_data = data_list[n_train:n_train + n_val]
    test_data = data_list[n_train + n_val:]
    
    return train_data, val_data, test_data

def train():
    log.info("Loading OCR datasets...")
    train_data, val_data, test_data = get_dataset_splits()
    log.info(f"Splits summary - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
    
    # Save splits registry for evaluation pipeline to prevent data leakage
    splits_registry = {
        "train": train_data,
        "val": val_data,
        "test": test_data
    }
    registry_path = os.path.join(MODEL_DIR, "ocr_splits_registry.json")
    with open(registry_path, "w") as f:
        json.dump(splits_registry, f, indent=4)
    log.info(f"Saved OCR splits registry to {registry_path}")
    
    # Create DataLoaders
    train_dataset = OCRDataset(train_data)
    val_dataset = OCRDataset(val_data)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, collate_fn=collate_fn)
    
    # Initialize Model, Optimizer, Loss Function
    model = CRNN()
    criterion = nn.CTCLoss(blank=0, zero_infinity=True)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Fine-tuning simulation / training loop (small epochs for demo stability)
    epochs = 5
    log.info(f"Starting OCR model training/fine-tuning for {epochs} epochs...")
    
    best_val_loss = float('inf')
    
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for batch_idx, (images, targets, target_lengths) in enumerate(train_loader):
            optimizer.zero_grad()
            
            # Predict
            outputs = model(images) # (T, B, num_classes)
            input_lengths = torch.full(size=(outputs.size(1),), fill_value=outputs.size(0), dtype=torch.long)
            
            loss = criterion(outputs, targets, input_lengths, target_lengths)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        train_loss /= len(train_loader)
        
        # Validate
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, targets, target_lengths in val_loader:
                outputs = model(images)
                input_lengths = torch.full(size=(outputs.size(1),), fill_value=outputs.size(0), dtype=torch.long)
                loss = criterion(outputs, targets, input_lengths, target_lengths)
                val_loss += loss.item()
        val_loss /= len(val_loader)
        
        log.info(f"Epoch {epoch}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Save best checkpoint
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, "best_ocr_model.pt"))
            log.info("Saved best checkpoint to best_ocr_model.pt")
            
    # Save final model metadata
    metadata = {
        "charset": CHARSET,
        "image_dimensions": [IMG_WIDTH, IMG_HEIGHT],
        "training_epochs": epochs,
        "best_val_loss": best_val_loss
    }
    with open(os.path.join(MODEL_DIR, "ocr_model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    print("OCR training execution completed successfully.")

if __name__ == "__main__":
    train()
