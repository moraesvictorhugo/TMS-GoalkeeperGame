# ======================================================================
#  TESTANDO MODELO MISTO - PEMS 
# ======================================================================

# Pacotes ---------------------------------------------------------------
if (!require(tidyverse))   install.packages("tidyverse")
if (!require(lme4))        install.packages("lme4")
if (!require(lmerTest))    install.packages("lmerTest")
if (!require(performance)) install.packages("performance")
if (!require(see))         install.packages("see")

library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)

# ======================================================================
#  Limpeza e reprocessamento
# ======================================================================

df <- read.csv(
  "~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms.csv"
)

# Filtrar e transformar dados ------------------------------------------

df_clean <- df %>%
  filter(type_block == "Pulse") %>%   # Apenas blocos com pulso de TMS
  select(volunteer, trial, relMean_MEPpp_FDI, context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),
    
    # Agrupamento de contextos (Previsível vs Imprevisível)
    Predictability = ifelse(context %in% c(1, 10), "Unpredictable", "Predictable"),
    
    # Fatores
    Predictability = factor(Predictability, levels = c("Predictable", "Unpredictable")),
    Error_Prev = factor(last_random_was_error, levels = c(0, 1), labels = c("Acerto", "Erro")),
    volunteer = factor(volunteer)
  )

# Visualização ----------------------------------------------------------
table(df_clean$Predictability, df_clean$Error_Prev)

# ======================================================================
#  Ajuste do modelo linear misto (LMM)
# ======================================================================

modelo_misto <- lmer(
  log_PEM ~ Predictability * Error_Prev + (1 | volunteer),
  data = df_clean,
  REML = TRUE
)

# Resultados do modelo --------------------------------------------------
summary(modelo_misto)

# ======================================================================
#  Diagnósticos
# ======================================================================

par(mfrow = c(2, 2))

# Normalidade dos resíduos
qqnorm(resid(modelo_misto), main = "Normalidade dos Resíduos")
qqline(resid(modelo_misto), col = "red")

# Homoscedasticidade
plot(
  fitted(modelo_misto), resid(modelo_misto),
  xlab = "Valores Ajustados", ylab = "Resíduos",
  main = "Homoscedasticidade",
  pch = 20, col = alpha("black", 0.2)
)
abline(h = 0, col = "red")

# Normalidade dos efeitos aleatórios
qqnorm(
  ranef(modelo_misto)$volunteer[[1]],
  main = "Normalidade dos Efeitos Aleatórios"
)
qqline(ranef(modelo_misto)$volunteer[[1]], col = "blue")

par(mfrow = c(1, 1))

# Diagnóstico automático
check_model(modelo_misto)

# ANOVA Tipo III --------------------------------------------------------
anova(modelo_misto, type = 3)

# ======================================================================
#  SEGUNDO MODELO — efeito do aprendizado
# ======================================================================

if (!require(emmeans)) install.packages("emmeans")
library(emmeans)

df <- read.csv(
  "~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms.csv"
)

# Filtrar e transformar (incluindo bloco)
df_clean <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, relMean_MEPpp_FDI, context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),
    
    Predictability = ifelse(context %in% c(1, 10), "Unpredictable", "Predictable"),
    Predictability = factor(Predictability, levels = c("Predictable", "Unpredictable")),
    Error_Prev = factor(last_random_was_error, levels = c(0, 1), labels = c("Acerto", "Erro")),
    
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    volunteer = factor(volunteer)
  )

# ======================================================================
#  Modelo de aprendizado
# ======================================================================

print("=== AJUSTANDO MODELO DE APRENDIZADO (COM BLOCO) ===")

modelo_aprendizado <- lmer(
  log_PEM ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_clean,
  REML = TRUE
)

# Resultados ------------------------------------------------------------
print(summary(modelo_aprendizado))

print("=== ANOVA TIPO III (Efeitos Fixos) ===")
print(anova(modelo_aprendizado, type = 3))

# Diagnósticos ----------------------------------------------------------
par(mfrow = c(2, 2))

qqnorm(resid(modelo_aprendizado), main = "Normalidade dos Resíduos (Modelo Bloco)")
qqline(resid(modelo_aprendizado), col = "red")

plot(
  fitted(modelo_aprendizado), resid(modelo_aprendizado),
  xlab = "Valores Ajustados", ylab = "Resíduos",
  main = "Homoscedasticidade",
  pch = 20, col = alpha("black", 0.2)
)
abline(h = 0, col = "red")

qqnorm(
  ranef(modelo_aprendizado)$volunteer[[1]],
  main = "Efeitos Aleatórios (Voluntários)"
)
qqline(ranef(modelo_aprendizado)$volunteer[[1]], col = "blue")

par(mfrow = c(1, 1))

check_model(modelo_aprendizado)

# Interações (plot estimado pelo emmeans) -------------------------------
emmip(
  modelo_aprendizado,
  Block_Factor ~ Error_Prev | Predictability,
  CIs = TRUE,
  labs = list(
    y = "Log(PEM)",
    x = "Erro Anterior",
    title = "Interação: Previsibilidade x Erro x Bloco"
  )
)
