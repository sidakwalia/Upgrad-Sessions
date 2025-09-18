"""Train a logistic regression recommendation model without external ML frameworks."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class FeatureTransformer:
    categorical_features: List[str]
    numeric_features: List[str]
    category_columns: List[str] | None = None
    numeric_stats: Dict[str, Tuple[float, float]] | None = None

    def fit(self, df: pd.DataFrame) -> None:
        cat_df = pd.get_dummies(df[self.categorical_features], prefix=self.categorical_features)
        self.category_columns = cat_df.columns.tolist()

        stats: Dict[str, Tuple[float, float]] = {}
        for col in self.numeric_features:
            mean = float(df[col].mean())
            std = float(df[col].std())
            if std == 0:
                std = 1.0
            stats[col] = (mean, std)
        self.numeric_stats = stats

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if self.category_columns is None or self.numeric_stats is None:
            raise RuntimeError("Transformer must be fitted before calling transform().")

        cat_df = pd.get_dummies(df[self.categorical_features], prefix=self.categorical_features)
        cat_df = cat_df.reindex(columns=self.category_columns, fill_value=0)

        num_df = df[self.numeric_features].copy()
        for col, (mean, std) in self.numeric_stats.items():
            num_df[col] = (num_df[col] - mean) / std

        features = np.hstack([cat_df.values.astype(float), num_df.values.astype(float)])
        return features

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        self.fit(df)
        return self.transform(df)


@dataclass
class LogisticModel:
    weights: np.ndarray
    transformer: FeatureTransformer

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        X = self.transformer.transform(df)
        z = X @ self.weights[1:] + self.weights[0]
        return 1 / (1 + np.exp(-z))


def load_interactions(data_dir: Path) -> pd.DataFrame:
    interactions_path = data_dir / "interactions.csv"
    if not interactions_path.exists():
        raise FileNotFoundError(
            f"Could not find {interactions_path}. Run synthetic_data.py to generate the dataset first."
        )
    return pd.read_csv(interactions_path)


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-z))


def train_logistic_regression(X: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 800) -> np.ndarray:
    n_samples, n_features = X.shape
    weights = np.zeros(n_features + 1)

    for epoch in range(epochs):
        z = X @ weights[1:] + weights[0]
        predictions = sigmoid(z)
        error = predictions - y

        grad_w = (X.T @ error) / n_samples
        grad_b = error.mean()

        weights[1:] -= lr * grad_w
        weights[0] -= lr * grad_b

        if epoch % 200 == 0 and epoch > 0:
            lr *= 0.8

    return weights


def roc_auc_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    if y_true.max() == y_true.min():
        return 0.5
    order = np.argsort(-y_score)
    y_true_sorted = y_true[order]
    cum_pos = np.cumsum(y_true_sorted)
    cum_neg = np.cumsum(1 - y_true_sorted)
    tpr = cum_pos / cum_pos[-1]
    fpr = cum_neg / cum_neg[-1]
    auc = np.trapezoid(tpr, fpr)
    return float(auc)


def average_precision_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    total_positive = y_true.sum()
    if total_positive == 0:
        return 0.0
    order = np.argsort(-y_score)
    y_true_sorted = y_true[order]
    cum_pos = np.cumsum(y_true_sorted)
    precision_at_k = cum_pos / (np.arange(len(y_true_sorted)) + 1)
    relevant_precisions = precision_at_k[y_true_sorted == 1]
    ap = relevant_precisions.sum() / total_positive
    return float(ap)


def train(data_dir: Path, reports_dir: Path) -> tuple[LogisticModel, dict[str, float]]:
    interactions = load_interactions(data_dir)

    categorical_features = [
        "region",
        "device",
        "primary_interest",
        "secondary_interest_1",
        "secondary_interest_2",
        "category",
    ]
    numeric_features = [
        "age",
        "creator_affinity",
        "avg_session_minutes",
        "creator_popularity",
        "audio_trendiness",
        "avg_watch_length",
        "production_quality",
        "engagement_probability",
    ]

    feature_columns = categorical_features + numeric_features

    transformer = FeatureTransformer(categorical_features, numeric_features)
    X = transformer.fit_transform(interactions[feature_columns])
    y = interactions["engaged"].values.astype(float)

    weights = train_logistic_regression(X, y)
    model = LogisticModel(weights=weights, transformer=transformer)

    proba = model.predict_proba(interactions[feature_columns])
    metrics = {
        "roc_auc": roc_auc_score(y, proba),
        "average_precision": average_precision_score(y, proba),
    }

    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    return model, metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Meta Reels recommender model")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Directory with synthetic datasets")
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"), help="Directory to store evaluation outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _, metrics = train(args.data_dir, args.reports_dir)
    print("Training complete. Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")


if __name__ == "__main__":
    main()
