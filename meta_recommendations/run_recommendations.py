"""End-to-end pipeline for generating data, training and scoring Meta Reels recommendations."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from synthetic_data import (
    SyntheticDataConfig,
    estimate_engagement_probability,
    generate_interactions,
    generate_reels,
    generate_users,
    save_datasets,
)
from train_recommender import LogisticModel, train


FEATURE_COLUMNS = [
    "age",
    "region",
    "device",
    "primary_interest",
    "secondary_interest_1",
    "secondary_interest_2",
    "creator_affinity",
    "avg_session_minutes",
    "category",
    "creator_popularity",
    "audio_trendiness",
    "avg_watch_length",
    "production_quality",
    "engagement_probability",
]


def ensure_datasets(data_dir: Path, regenerate: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    users_path = data_dir / "users.csv"
    reels_path = data_dir / "reels.csv"
    interactions_path = data_dir / "interactions.csv"

    if regenerate or not (users_path.exists() and reels_path.exists() and interactions_path.exists()):
        print("Generating fresh synthetic datasets...")
        config = SyntheticDataConfig(output_dir=data_dir)
        users = generate_users(config)
        reels = generate_reels(config)
        interactions = generate_interactions(users, reels, config)
        save_datasets(users, reels, interactions, data_dir)
    else:
        print("Using cached synthetic datasets.")

    users = pd.read_csv(users_path)
    reels = pd.read_csv(reels_path)
    interactions = pd.read_csv(interactions_path)
    return users, reels, interactions


def train_model(data_dir: Path, reports_dir: Path) -> LogisticModel:
    model, metrics = train(data_dir, reports_dir)
    print("Model metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    return model


def _prepare_candidate_features(user: pd.Series, reels: pd.DataFrame) -> pd.DataFrame:
    candidate = reels.copy()
    candidate["user_id"] = user.user_id
    candidate["age"] = user.age
    candidate["region"] = user.region
    candidate["device"] = user.device
    candidate["primary_interest"] = user.primary_interest
    candidate["secondary_interest_1"] = user.secondary_interest_1
    candidate["secondary_interest_2"] = user.secondary_interest_2
    candidate["creator_affinity"] = user.creator_affinity
    candidate["avg_session_minutes"] = user.avg_session_minutes
    candidate["engagement_probability"] = candidate.apply(
        lambda reel: estimate_engagement_probability(user, reel), axis=1
    )
    return candidate


def recommend_reels(
    model, users: pd.DataFrame, reels: pd.DataFrame, user_id: int, top_k: int = 5
) -> pd.DataFrame:
    user_row = users.loc[users["user_id"] == user_id]
    if user_row.empty:
        raise ValueError(f"Unknown user_id={user_id}")
    user = user_row.iloc[0]

    candidate = _prepare_candidate_features(user, reels)
    candidate["score"] = model.predict_proba(candidate[FEATURE_COLUMNS])
    recommendations = candidate.sort_values("score", ascending=False).head(top_k)
    return recommendations[[
        "reel_id",
        "category",
        "score",
        "engagement_probability",
        "creator_popularity",
        "audio_trendiness",
        "production_quality",
    ]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Meta Reels recommendation pipeline")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--regenerate", action="store_true", help="Force regeneration of synthetic data")
    parser.add_argument("--user-id", type=int, default=0, help="User id to generate recommendations for")
    parser.add_argument("--top-k", type=int, default=5, help="Number of reels to recommend")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    users, reels, _ = ensure_datasets(args.data_dir, args.regenerate)

    print("Training recommendation model on full dataset...")
    model = train_model(args.data_dir, args.reports_dir)

    print(f"Generating top {args.top_k} recommendations for user {args.user_id}...")
    recommendations = recommend_reels(model, users, reels, args.user_id, args.top_k)
    print(recommendations.to_string(index=False))


if __name__ == "__main__":
    main()
