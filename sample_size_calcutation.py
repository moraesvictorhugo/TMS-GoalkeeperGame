# import pingouin as pg
# import numpy as np

# # Parameters from your ANOVA results
# eta_squared = 0.14      # Large effect size from Cohen’s Guidelines: effect of the IV on the DV
# alpha = 0.05            # Significance level (default is 0.05)
# power = 0.8             # Desired power (default is 0.8): probability of observe an effect, if it exists
# k = 5                   # Number of groups (from DF of context, which is 4 + 1)
# n = 15                   # Number of observations per group


# # Convert partial eta-squared to Cohen's f
# effect_size = np.sqrt(eta_squared / (1 - eta_squared))

# # Calculate sample size
# sample_size = pg.power_anova(n=n, alpha=alpha, power=power, k=k)

# print(f"Cohen's f (effect size): {effect_size:.3f}")
# print(f"Required Sample Size per Group: {round(sample_size)}")
# print(f"Total Required Sample Size: {round(sample_size) * k}")

# ---------------------------------------------------------------
# Sample size calculation for ANOVA with multiple comparisons
# ---------------------------------------------------------------
import pingouin as pg
import math

# Parâmetros
effect_size = 0.4  # Cohen's f
alpha = 0.05       # Nível de significância original
power = 0.8        # Poder estatístico desejado
num_groups = 5     # Número de grupos ou contextos
num_comparisons = 10  # Número de comparações (por exemplo, combinações de grupos)

# Ajustar o nível de significância para comparações múltiplas (Bonferroni)
alpha_ajustado = alpha / num_comparisons

# Calcular o tamanho da amostra usando pingouin
sample_size = pg.power_anova(eta_squared=effect_size**2,  # Pingouin usa eta_squared (n²)
                             k=num_groups,
                             alpha=alpha_ajustado,
                             power=power)

# Arredondar para o próximo número inteiro
sample_size_corrected = math.ceil(sample_size)

print(f"Tamanho da amostra necessário (corrigido para comparações múltiplas): {sample_size_corrected}")