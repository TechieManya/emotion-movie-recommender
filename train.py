import pandas as pd
import pickle
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

print("Loading dataset...")
ratings = pd.read_csv(
    'ml-100k/u.data',
    sep='\t',
    names=['user_id', 'movie_id', 'rating', 'timestamp']
)

print(f"Total ratings: {len(ratings)}")
print(f"Total users:   {ratings['user_id'].nunique()}")
print(f"Total movies:  {ratings['movie_id'].nunique()}")

print("\nPreparing data...")
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(
    ratings[['user_id', 'movie_id', 'rating']],
    reader
)

trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
print(f"Training samples: {trainset.n_ratings}")

print("\nTraining SVD model...")
print("Takes about 30-60 seconds...")
model = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02)
model.fit(trainset)
print("Training complete ✅")

print("\nEvaluating...")
predictions = model.test(testset)
rmse = accuracy.rmse(predictions)
mae  = accuracy.mae(predictions)
print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")

print("\nSaving model...")
with open('svd_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model saved as svd_model.pkl ✅")
print("\nDone! Ready for next step.")