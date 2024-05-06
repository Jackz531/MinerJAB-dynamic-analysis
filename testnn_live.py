import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model

# Load the test dataset
test_df = pd.read_csv('int.csv')
original_df = test_df.copy()
# Specify the columns to be used as features
features = ['median_cpu_percent', 'quadratic_deviation', 'ram_usage', 'median_network_rate', 'Number of crypto API calls']
test_df = test_df[features]

# Scale the features
scaler = StandardScaler()
X_test = scaler.fit_transform(test_df)

# Load the trained model
model = load_model('cryptojacker_detection_model.h5')

# Predict the labels for the test dataset
predictions = model.predict(X_test)
predicted_labels = (predictions > 0.5).astype(int).flatten()
edicted_labels = ['yes' if label == 1 else 'no' for label in predicted_labels]
original_df['Cryptojacker or not'] = predicted_labels

# Remove rows where 'Cryptojacker or not' is 0
filtered_df = original_df[original_df['Cryptojacker or not'] != 0]

# Save the filtered dataframe back to 'int.csv'
filtered_df.to_csv('int.csv', index=False)
