import numpy as np
# Create a synthetic dataset
np.random.seed(42)  # For reproducibility
data = np.random.normal(loc=50, scale=10, size=100)  # Mean = 50, Std Dev = 10, Sample Size = 100
print("Original Data:", data)

def bootstrap(data, num_samples=1000, confidence_level=0.95):
    bootstrap_means = np.zeros(num_samples)
    
    # Perform bootstrap sampling
    for i in range(num_samples):
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means[i] = np.mean(bootstrap_sample)
    
    # Calculate confidence intervals
    lower_bound = np.percentile(bootstrap_means, (1 - confidence_level) / 2 * 100)
    upper_bound = np.percentile(bootstrap_means, (confidence_level + (1 - confidence_level) / 2) * 100)
    
    return np.mean(bootstrap_means), lower_bound, upper_bound, bootstrap_means

mean_estimate, lower_ci, upper_ci, bootstrap_means = bootstrap(data)

print(f"Bootstrap Mean Estimate: {mean_estimate:.2f}")
print(f"{95}% Confidence Interval: [{lower_ci:.2f}, {upper_ci:.2f}]")


import matplotlib.pyplot as plt

# Assuming bootstrap_means is an array containing means from bootstrap samples
plt.hist(bootstrap_means, bins=30, alpha=0.7, color='blue')
plt.axvline(mean_estimate, color='red', linestyle='dashed', linewidth=2, label='Bootstrap Mean')
plt.axvline(lower_ci, color='green', linestyle='dashed', linewidth=2, label='Lower CI')
plt.axvline(upper_ci, color='green', linestyle='dashed', linewidth=2, label='Upper CI')
plt.title('Distribution of Bootstrap Means')
plt.xlabel('Mean Values')
plt.ylabel('Frequency')
plt.legend()
plt.show()

