"""
=================================================
Importing modules and data
=================================================
"""
from modules import import_signal
import matplotlib.pyplot as plt
import numpy as np

## Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/"
file_name = "df_gklab_analysis.csv"
df = import_signal.import_csv_data(file_path, file_name)

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v01_ctx_2 = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 1)]

# Array for MEPs in ctx 2
array_01_ctx_2 = v01_ctx_2['MEPpp_FDI_µV'].to_numpy()

# Filter MEPs during pulses and split by context
v01_ctx_10 = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 1)]

# Array for MEPs in ctx 10
array_01_ctx_10 = v01_ctx_10['MEPpp_FDI_µV'].to_numpy()

"""
=================================================
Function definition
=================================================
"""

# Function to perform bootstrap resampling
def bootstrap_resample(data, n_samples):
    return np.random.choice(data, size=n_samples, replace=True)

# Function to compute ECDF
def ecdf(data):
    x = np.sort(data)
    y = np.arange(1, len(data) + 1) / len(data)
    return x, y

# Calculate ECDF for array_01_ctx_10
x_array_01_ctx_10, y_array_01_ctx_10 = ecdf(array_01_ctx_10)

# Generate bootstrap samples for array_01_ctx_2
num_bootstrap_samples = 1000
bootstrap_samples = [bootstrap_resample(array_01_ctx_2, len(array_01_ctx_2)) for _ in range(num_bootstrap_samples)]

# Plotting ECDFs
plt.figure(figsize=(10, 6))

# Plot ECDF for array_01_ctx_10
plt.plot(x_array_01_ctx_10, y_array_01_ctx_10, label='array_01_ctx_10 ECDF', color='blue')

# Plot ECDFs for multiple bootstrap samples of array_01_ctx_2
for i in range(100):  # Plot only 10 bootstrap samples for clarity
    x_bs, y_bs = ecdf(bootstrap_samples[i])
    plt.plot(x_bs, y_bs, color='green', alpha=0.3)

plt.title('ECDF of array_01_ctx_10 and Bootstrap Samples of array_01_ctx_2')
plt.xlabel('Value')
plt.ylabel('Cumulative Probability')
plt.legend(['array_01_ctx_10 ECDF', 'Bootstrap Sample ECDF (array_01_ctx_2)'])
plt.grid()
plt.show()


# --------------------------------------------------
# pip install pymc3 arviz
# --------------------------------------------------
import pymc3 as pm
import arviz as az


# Combine data into a single array with a group indicator
data = np.concatenate([array_01_ctx_10, array_01_ctx_2])
group_indicator = np.concatenate([np.zeros(len(array_01_ctx_10)), np.ones(len(array_01_ctx_2))])

# Bayesian model
with pm.Model() as model:
    # Priors for the means of the two groups
    mu_10 = pm.Normal('mu_10', mu=0, sigma=100)
    mu_2 = pm.Normal('mu_2', mu=0, sigma=100)
    
    # Priors for the standard deviations of the two groups
    sigma_10 = pm.HalfNormal('sigma_10', sigma=10)
    sigma_2 = pm.HalfNormal('sigma_2', sigma=10)
    
    # Priors for the degrees of freedom (nu) of the Student's t-distribution
    nu_10 = pm.Exponential('nu_10', lam=1/30)
    nu_2 = pm.Exponential('nu_2', lam=1/30)
    
    # Likelihood (Student's t-distribution)
    likelihood_10 = pm.StudentT('likelihood_10', nu=nu_10, mu=mu_10, sigma=sigma_10, observed=array_01_ctx_10)
    likelihood_2 = pm.StudentT('likelihood_2', nu=nu_2, mu=mu_2, sigma=sigma_2, observed=array_01_ctx_2)
    
    # Difference between the means
    delta_mu = pm.Deterministic('delta_mu', mu_10 - mu_2)
    
    # Sample from the posterior
    trace = pm.sample(2000, tune=1000, target_accept=0.95, return_inferencedata=True)

# Summary of the results
print(az.summary(trace, var_names=['mu_10', 'mu_2', 'delta_mu']))

# Plot the posterior distributions
az.plot_posterior(trace, var_names=['mu_10', 'mu_2', 'delta_mu'])
plt.show()

# Probability that mu_10 > mu_2
prob_mu_10_gt_mu_2 = np.mean(trace.posterior['delta_mu'] > 0)
print(f"Probability that mu_10 > mu_2: {prob_mu_10_gt_mu_2:.4f}")