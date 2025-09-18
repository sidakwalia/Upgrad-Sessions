# Meta Reels Recommendation Project

This project demonstrates how to build a lightweight recommendation pipeline for Meta Reels using fully synthetic data.

## Project Structure

- `data/` – location where the generated synthetic datasets are stored.
- `synthetic_data.py` – script that creates synthetic user, reel and interaction datasets.
- `train_recommender.py` – trains a recommendation model using the generated data.
- `run_recommendations.py` – end-to-end script that generates data, trains the model and produces sample recommendations.
- `reports/` – evaluation results and exploratory analysis summaries.

## Quickstart

```bash
python synthetic_data.py               # generate synthetic data
python train_recommender.py            # train model and save metrics
python run_recommendations.py          # run full pipeline and print top recommendations
```

All scripts rely only on common Python libraries (`numpy`, `pandas`) and implement the
machine-learning components (feature encoding, logistic regression, evaluation metrics)
directly in code so that the full pipeline runs without external ML frameworks.

## Synthetic Data Overview

The synthetic dataset captures plausible relationships between users and reels by simulating:

- **User features**: age, region, preferred categories and creator affinity.
- **Reel features**: category, audio trendiness, creator popularity and average watch length.
- **Interaction labels**: whether a user would engage with a given reel (like, share, rewatch, etc.).

The data generator injects signal into the labels by correlating them with overlapping interests and popularity signals. This allows the recommendation model to learn meaningful patterns without requiring any real user data.

## Recommendation Approach

The baseline recommender trains a logistic regression model over feature crossed user-reel interactions. The pipeline performs categorical encoding and feature scaling using `ColumnTransformer`. Evaluation metrics include ROC AUC and average precision.

The `run_recommendations.py` script also demonstrates how to rank candidate reels for a given user by predicting engagement probabilities.

## Next Steps

Potential future improvements include:

1. Using sequence-aware models (transformers or RNNs) to capture temporal dynamics.
2. Introducing graph-based embeddings to represent creator-user relationships.
3. Exploring reinforcement learning for ranking policies that optimise long-term engagement.
4. Deploying the model via a lightweight API for serving recommendations in real time.

