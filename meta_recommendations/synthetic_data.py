"""Generate synthetic datasets for a Meta Reels style recommendation system."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


CATEGORIES = [
    "Music",
    "Comedy",
    "Dance",
    "Travel",
    "Food",
    "Fashion",
    "Sports",
    "DIY",
    "Education",
]
REGIONS = ["NA", "LATAM", "EMEA", "APAC"]
DEVICE_TYPES = ["iOS", "Android", "Web"]


@dataclass
class SyntheticDataConfig:
    output_dir: Path
    n_users: int = 1500
    n_reels: int = 500
    interactions_per_user: int = 40
    random_seed: int = 42


def generate_users(config: SyntheticDataConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed)
    ages = rng.normal(loc=28, scale=8, size=config.n_users).clip(13, 60).astype(int)
    regions = rng.choice(REGIONS, size=config.n_users, p=[0.35, 0.2, 0.25, 0.2])
    devices = rng.choice(DEVICE_TYPES, size=config.n_users, p=[0.45, 0.45, 0.1])
    primary_interest = rng.choice(CATEGORIES, size=config.n_users)
    secondary_interest = [
        rng.choice([c for c in CATEGORIES if c != primary_interest[i]], size=2, replace=False)
        for i in range(config.n_users)
    ]
    creator_affinity = rng.uniform(0.2, 1.0, size=config.n_users)
    session_length = rng.gamma(shape=2.2, scale=5, size=config.n_users)

    users = pd.DataFrame(
        {
            "user_id": np.arange(config.n_users),
            "age": ages,
            "region": regions,
            "device": devices,
            "primary_interest": primary_interest,
            "secondary_interest_1": [sec[0] for sec in secondary_interest],
            "secondary_interest_2": [sec[1] for sec in secondary_interest],
            "creator_affinity": creator_affinity,
            "avg_session_minutes": session_length,
        }
    )
    return users


def generate_reels(config: SyntheticDataConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed + 1)
    categories = rng.choice(CATEGORIES, size=config.n_reels)
    creator_popularity = rng.beta(a=2.5, b=1.5, size=config.n_reels)
    audio_trendiness = rng.beta(a=2.0, b=2.2, size=config.n_reels)
    watch_length = rng.normal(loc=32, scale=8, size=config.n_reels).clip(10, 90)
    production_quality = rng.uniform(0.3, 1.0, size=config.n_reels)

    reels = pd.DataFrame(
        {
            "reel_id": np.arange(config.n_reels),
            "category": categories,
            "creator_popularity": creator_popularity,
            "audio_trendiness": audio_trendiness,
            "avg_watch_length": watch_length,
            "production_quality": production_quality,
        }
    )
    return reels


def _engagement_probability(
    row: pd.Series, rng: np.random.Generator | None, *, noise: bool = True
) -> float:
    interest_match = float(row.primary_interest == row.category)
    secondary_match = float(
        row.category in {row.secondary_interest_1, row.secondary_interest_2}
    )
    creator_alignment = 0.4 * row.creator_affinity * row.creator_popularity
    trend_alignment = 0.2 * row.audio_trendiness
    session_factor = 0.1 * (row.avg_session_minutes / (row.avg_session_minutes + 20))

    watch_length_diff = abs(row.avg_watch_length - 25)
    watch_alignment = 0.15 * (1 - watch_length_diff / 80)

    base_score = (
        -1.2
        + 1.5 * interest_match
        + 0.9 * secondary_match
        + creator_alignment
        + trend_alignment
        + session_factor
        + watch_alignment
    )
    noise_term = rng.normal(0, 0.25) if (noise and rng is not None) else 0.0
    probability = 1 / (1 + np.exp(-(base_score + noise_term)))
    return float(np.clip(probability, 0.01, 0.99))


def generate_interactions(
    users: pd.DataFrame, reels: pd.DataFrame, config: SyntheticDataConfig
) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed + 2)
    interactions: List[pd.DataFrame] = []

    for user in users.itertuples(index=False):
        sampled_reels = rng.choice(
            reels.reel_id.values,
            size=config.interactions_per_user,
            replace=False,
        )
        user_rows = pd.DataFrame({"user_id": user.user_id, "reel_id": sampled_reels})
        user_rows = user_rows.merge(users, on="user_id").merge(reels, on="reel_id")

        probs = user_rows.apply(lambda r: _engagement_probability(r, rng, noise=True), axis=1).to_numpy()
        engaged = rng.binomial(1, probs)
        watch_time = probs * user_rows["avg_watch_length"].values * rng.uniform(0.8, 1.1, size=probs.size)

        user_rows = user_rows.assign(
            engagement_probability=probs,
            engaged=engaged,
            watch_time_seconds=watch_time,
        )
        interactions.append(user_rows)

    interactions_df = pd.concat(interactions, ignore_index=True)
    interactions_df = interactions_df.sort_values(["user_id", "engagement_probability"], ascending=[True, False])
    return interactions_df


def save_datasets(
    users: pd.DataFrame, reels: pd.DataFrame, interactions: pd.DataFrame, output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    users.to_csv(output_dir / "users.csv", index=False)
    reels.to_csv(output_dir / "reels.csv", index=False)
    interactions.to_csv(output_dir / "interactions.csv", index=False)


def estimate_engagement_probability(user: pd.Series, reel: pd.Series) -> float:
    """Estimate engagement probability without stochastic noise for inference."""
    combined = pd.Series({
        "primary_interest": user.primary_interest,
        "secondary_interest_1": user.secondary_interest_1,
        "secondary_interest_2": user.secondary_interest_2,
        "creator_affinity": user.creator_affinity,
        "avg_session_minutes": user.avg_session_minutes,
        "category": reel.category,
        "creator_popularity": reel.creator_popularity,
        "audio_trendiness": reel.audio_trendiness,
        "avg_watch_length": reel.avg_watch_length,
        "production_quality": reel.production_quality,
    })
    # Add user age for compatibility
    combined["age"] = user.age
    return _engagement_probability(combined, rng=None, noise=False)


def parse_args() -> SyntheticDataConfig:
    parser = argparse.ArgumentParser(description="Generate synthetic data for Meta Reels recommendations")
    parser.add_argument("--output", type=Path, default=Path("data"), help="Directory to save datasets")
    parser.add_argument("--users", type=int, default=1500, help="Number of users to simulate")
    parser.add_argument("--reels", type=int, default=500, help="Number of reels to simulate")
    parser.add_argument(
        "--interactions-per-user", type=int, default=40, help="Number of interactions per user"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    return SyntheticDataConfig(
        output_dir=args.output,
        n_users=args.users,
        n_reels=args.reels,
        interactions_per_user=args.interactions_per_user,
        random_seed=args.seed,
    )


def main() -> None:
    config = parse_args()
    users = generate_users(config)
    reels = generate_reels(config)
    interactions = generate_interactions(users, reels, config)
    save_datasets(users, reels, interactions, config.output_dir)
    print(f"Generated {len(users)} users, {len(reels)} reels and {len(interactions)} interactions")
    print(f"Data saved to {config.output_dir.resolve()}")


if __name__ == "__main__":
    main()
