import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Generate synthetic dataset
np.random.seed(42)
data_size = 1000

# Features: [color (0=green, 1=yellow, 2=red), size (0=small, 1=medium, 2=large), weight (in grams)]
colors = np.random.choice([0, 1, 2], size=data_size)
sizes = np.random.choice([0, 1, 2], size=data_size)
weights = np.random.randint(50, 300, size=data_size)

# Labels: 0=Not Fresh, 1=Fresh
labels = (colors == 2) & (sizes == 2) & (weights > 150)  # Example condition for freshness
labels = labels.astype(int)

# Create DataFrame
df = pd.DataFrame({
    'color': colors,
    'size': sizes,
    'weight': weights,
    'freshness': labels
})

# Split the dataset
X = df[['color', 'size', 'weight']]
y = df['freshness']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'myapp/models/model.pkl')

print("Model trained and saved as 'model.pkl'")