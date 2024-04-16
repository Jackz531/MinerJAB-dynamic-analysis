import pandas as pd
import numpy as np

# Set a random seed for reproducibility
np.random.seed(42)

# Generate synthetic data
data = {
    'PID': np.arange(17, 117),
    'CPU utilization': np.random.uniform(50, 100, 100),
    'CPU Quadtric deviation': np.random.uniform(0, 3000, 100),
    'Ram Usage': np.random.uniform(10, 4000, 100),
    'Network Upload Rate': np.random.uniform(0, 400, 100),
    'Number of crypto api calls': np.random.randint(0, 10, 100),
    'Crytpojacker or not': np.random.choice(['yes', 'no'], 100, p=[0.5, 0.5])
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('synthetic_data.csv', index=False)

# Print the first 5 rows of the DataFrame
print(df.head())
