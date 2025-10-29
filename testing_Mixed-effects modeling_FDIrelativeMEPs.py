'''
Here is an example code to run a Mixed-Effects Model in Python using the statsmodels library. It assumes you have a CSV data file with columns:

response_time: your dependent variable (response time for each trial)

volunteer: volunteer ID

kicker_choice: categorical variable for the 5 past kicker choices

finger: categorical variable for the finger used (left, middle, ring)

previous_success: indicator of success or mistake in previous trial

trial: trial number (not used here directly but available)
'''

import pandas as pd
import statsmodels.formula.api as smf
from modules import import_signal

# Load your dataset from CSV
file_path = '/home/victormoraes/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-08-27'
file_name = "df_gklab_analysis_20250828.csv"
df = import_signal.import_csv_data(file_path, file_name)

# Custom function for conversion
def convert_value(val):
    if pd.isna(val):
        return val  # keep NaN as is
    if val == 0.0:
        return "00"
    else:
        return str(int(val))

df['context'] = df['context'].apply(convert_value)
df['response_info'] = df['response_info'].astype('Int64')
df['response_info'] = df['response_info'].astype('category')
df['last_was_error'] = df['last_was_error'].astype('Int64')
df['last_was_error'] = df['last_was_error'].astype('category')

# Drop rows with any NaN in columns of interest
df_clean = df.dropna(subset=['MEPpp_FDI_µV', 'context', 'response_info', 'last_was_error', 'ID_info'])

# Exclude trials noPulse
df_clean = df_clean[df_clean['tms_pulse'] != 'noPulse']

# Fit the mixed effects model
# Here 'volunteer' is the grouping variable for random effects (random intercept)
# Fixed effects: kicker_choice, finger, and previous_success
model = smf.mixedlm("MEPpp_FDI_µV ~ context * response_info * last_was_error", df_clean, groups=df_clean['ID_info'])

# Fit the model
result = model.fit()

# Print the summary of the model fit
print(result.summary())

'''
Coeficientes dos efeitos fixos (Coef.): 
    Mostram o efeito estimado do seu fator (exemplo, tipo de estímulo) sobre a variável de resposta (tempo de resposta cerebral).
    Um coeficiente positivo indica aumento esperado na resposta, negativo indica redução.

Erro padrão (Std.Err.): mede a incerteza da estimativa do coeficiente.

Valor z e P>|z|: indicam se o efeito é estatisticamente significativo.

Tipicamente, p-valor < 0.05 sugere efeito significativo.

Intervalo de confiança ([0.025 0.975]):
    Faixa provável do valor verdadeiro do coeficiente com 95% de confiança.

Variância dos efeitos aleatórios (Group Var):
    Indica a variabilidade entre os clusters/grupos (ex: participantes diferentes ter suas médias diferentes).

Uma variância alta indica grande variação entre indivíduos no efeito inato.

Log-Likelihood & Scale: 
    Métricas para avaliar ajuste do modelo, mas que geralmente são menos úteis para interpretação direta.
    Log-Likelihood: É uma medida da verossimilhança do modelo dados os dados observados.
        Quanto maior (menos negativo) o valor do Log-Likelihood, melhor o ajuste do modelo. É utilizado para comparação entre modelos.
    Scale: Reflete a estimativa da variância do erro residual.
        Valores menores indicam menor dispersão dos resíduos em torno da linha do modelo, o que sugere ajuste melhor.
    O ideal é construir diferentes modelos mistos (ex: com ou sem interação, com diferentes efeitos aleatórios) e comparar seus Log-Likelihoods
        e Scales para decidir qual é mais apropriado para seus dados e hipóteses.
'''

## -----> to do:

# deal with independent variables: this analysis excluded the context 00

# Plot fixed effects
import matplotlib.pyplot as plt
import numpy as np

coefs = result.params
errors = result.bse

fixed_effects = coefs.index
coef_values = coefs.values
errors_values = errors.values

plt.errorbar(coef_values, fixed_effects, xerr=errors_values, fmt='o')
plt.axvline(x=0, color='gray', linestyle='--')
plt.xlabel('Coefficient Estimate')
plt.title('Fixed Effects Coefficients with 95% CI')
plt.show()

###############

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

random_effects = result.random_effects

# Criar DataFrame direto, convertendo cada valor para escalar
re_list = []
for group, coef in random_effects.items():
    # coef é um ndarray com os valores dos efeitos aleatórios para o grupo
    re_list.append({"group": group, "random_intercept": coef[0]})

re_df = pd.DataFrame(re_list)

# Gráfico dos efeitos aleatórios por grupo
sns.pointplot(data=re_df, x="group", y="random_intercept")
plt.xticks(rotation=90)
plt.title("Random Intercepts by Group")
plt.xlabel("Group")
plt.ylabel("Random Intercept")
plt.show()

###############

import numpy as np

# Criar combinacoes unique de context e response_info
unique_combinations = df_clean[['context','response_info']].drop_duplicates()

# Criar data frame para previsoes
pred_df = unique_combinations.copy()
pred_df['last_was_error'] = df_clean['last_was_error'].cat.categories[0]  # escolher um nível de referência

# Obter predições do modelo para essas combinacoes
pred_df['predicted_response'] = result.predict(pred_df)

sns.lineplot(data=pred_df, x='context', y='predicted_response', hue='response_info', marker="o")
plt.title("Predicted FDI MEP amplitude by Context and Response Info")
plt.ylabel("Predicted FDI MEP amplitude")
plt.show()

###############

residuals = result.resid
fitted = result.fittedvalues

plt.scatter(fitted, residuals, alpha=0.3)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Fitted values")
plt.ylabel("Residuals")
plt.title("Residuals vs Fitted values")
plt.show()
