import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import recall_score, precision_score
import logging
import pickle

from model_pytorch import F1StrategyModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

FEATURE_COLS = [
    "current_lap", "total_laps", "stint_length", "compound",
    "pace_delta_3lap", "pace_delta_5lap", "Position",
    "gap_ahead", "gap_behind", "pit_stop_count",
    "safety_car_active", "track_temp", "rain"
]

TRAIN_YEARS = [2019, 2020, 2021, 2022, 2023]
TEST_YEAR = 2024


class F1Dataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def load_data():
    train_dfs, test_dfs = [], []

    for year in TRAIN_YEARS:
        df = pd.read_csv(PROCESSED_DIR / f"features_{year}.csv")
        train_dfs.append(df)

    test_df = pd.read_csv(PROCESSED_DIR / f"features_{TEST_YEAR}.csv")

    train_df = pd.concat(train_dfs, ignore_index=True)

    # filling missing gap_behind with median
    median_gap = train_df["gap_behind"].median()
    train_df["gap_behind"] = train_df["gap_behind"].fillna(median_gap)
    test_df["gap_behind"] = test_df["gap_behind"].fillna(median_gap)

    # converting booleans to int
    train_df["safety_car_active"] = train_df["safety_car_active"].astype(int)
    train_df["rain"] = train_df["rain"].astype(int)
    test_df["safety_car_active"] = test_df["safety_car_active"].astype(int)
    test_df["rain"] = test_df["rain"].astype(int)

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["label"].values

    X_test = test_df[FEATURE_COLS].values
    y_test = test_df["label"].values

    # train/val split (85/15)
    val_size = int(len(X_train) * 0.15)
    indices = np.random.permutation(len(X_train))
    val_idx, train_idx = indices[:val_size], indices[val_size:]

    X_val, y_val = X_train[val_idx], y_train[val_idx]
    X_train, y_train = X_train[train_idx], y_train[train_idx]

    # normalize
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # saving scaler for inference
    with open(MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    logger.info(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    logger.info(f"Train label ratio: {y_train.mean():.3f}")

    return X_train, y_train, X_val, y_val, X_test, y_test


def train():
    X_train, y_train, X_val, y_val, X_test, y_test = load_data()

    train_loader = DataLoader(F1Dataset(X_train, y_train), batch_size=256, shuffle=True)
    val_loader = DataLoader(F1Dataset(X_val, y_val), batch_size=256, shuffle=False)

    model = F1StrategyModel(input_dim=13)

    # handling class imbalance
    pos_weight = torch.tensor([5.0])
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    best_val_loss = float("inf")
    patience_counter = 0
    early_stop_patience = 10

    for epoch in range(200):
        # training
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            pit_prob, _, _ = model(X_batch)
            loss = criterion(pit_prob.squeeze(), y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        train_loss /= len(train_loader)

        # validation
        model.eval()
        val_loss = 0
        all_preds, all_labels = [], []

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                pit_prob, _, _ = model(X_batch)
                loss = criterion(pit_prob.squeeze(), y_batch)
                val_loss += loss.item()
                preds = (torch.sigmoid(pit_prob.squeeze()) > 0.30).int().numpy()
                all_preds.extend(preds)
                all_labels.extend(y_batch.int().numpy())

        val_loss /= len(val_loader)
        recall = recall_score(all_labels, all_preds, zero_division=0)
        precision = precision_score(all_labels, all_preds, zero_division=0)

        scheduler.step(val_loss)

        if (epoch + 1) % 10 == 0:
            logger.info(
                f"Epoch {epoch+1:3d} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Recall: {recall:.3f} | "
                f"Precision: {precision:.3f}"
            )

        # early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), MODELS_DIR / "best_model.pt")
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break

    # final evaluation on test set
    logger.info("--- Test Set Evaluation ---")
    model.load_state_dict(torch.load(MODELS_DIR / "best_model.pt"))
    model.eval()

    test_loader = DataLoader(F1Dataset(X_test, y_test), batch_size=256, shuffle=False)
    all_preds, all_labels = [], []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            pit_prob, _, _ = model(X_batch)
            preds = (torch.sigmoid(pit_prob.squeeze()) > 0.30).int().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.int().numpy())

    recall = recall_score(all_labels, all_preds, zero_division=0)
    precision = precision_score(all_labels, all_preds, zero_division=0)
    logger.info(f"Test Recall: {recall:.3f} | Test Precision: {precision:.3f}")


if __name__ == "__main__":
    train()