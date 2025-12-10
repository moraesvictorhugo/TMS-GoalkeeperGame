###############################################################
#   ANÁLISE DE MODELOS MISTOS - PEMS FDI
###############################################################

###############################
# 1. Pacotes
###############################

# Instalação automática se ausentes
if (!require(tidyverse))  install.packages("tidyverse")
if (!require(lme4))       install.packages("lme4")
if (!require(lmerTest))   install.packages("lmerTest")
if (!require(performance)) install.packages("performance")
if (!require(see))         install.packages("see")
if (!require(emmeans))     install.packages("emmeans") # post-hoc

# Carrega bibliotecas
library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)
library(emmeans)


###############################################################
# 2. Importação e pré-processamento dos dados
###############################################################

df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms.csv")

# Filtrar e preparar dados (versão sem bloco)
df_clean <- df %>%
  filter(type_block == "Pulse") %>%                       # Apenas trials com pulso TMS
  select(volunteer, trial, relMean_MEPpp_FDI, context,
         last_random_was_error) %>%                       # Seleção de colunas
  drop_na() %>%                                           # Remover missings
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),                     # Transformação log
    
    # Agrupamento dos contextos: previsível vs imprevisível
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    
    # Conversão para fatores com níveis controlados
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    Error_Prev     = factor(last_random_was_error,
                            levels = c(0, 1),
                            labels = c("Acerto", "Erro")),
    volunteer      = factor(volunteer)
  )

# Checar distribuição das condições
table(df_clean$Predictability, df_clean$Error_Prev)


###############################################################
# 3. MODELO 1
###############################################################

# Modelo com intercepto aleatório por voluntário
modelo_1 <- lmer(
  log_PEM ~ Predictability * Error_Prev + (1 | volunteer),
  data = df_clean,
  REML = TRUE
)

# Resumo do modelo
summary(modelo_1)


###############################################################
# 4. Diagnósticos do modelo
###############################################################

par(mfrow = c(2, 2))

# Normalidade dos resíduos
qqnorm(resid(modelo_1), main = "Normalidade dos Resíduos")
qqline(resid(modelo_1), col = "red")

# Homoscedasticidade (resíduos vs ajustados)
plot(
  fitted(modelo_1), resid(modelo_1),
  xlab = "Valores Ajustados",
  ylab = "Resíduos",
  main = "Homoscedasticidade",
  pch = 20, col = alpha("black", 0.2)
)
abline(h = 0, col = "red")

# Normalidade dos efeitos aleatórios (interceptos dos voluntários)
qqnorm(ranef(modelo_1)$volunteer[[1]],
       main = "Normalidade dos Efeitos Aleatórios")
qqline(ranef(modelo_1)$volunteer[[1]], col = "blue")

par(mfrow = c(1, 1))

# Checagem automática de diagnóstico
check_model(modelo_1)

# ANOVA tipo III para testar significância dos efeitos fixos
anova(modelo_1, type = 3)

###############################################################
# 5. Visualização das interações estimadas (EMMs)
###############################################################

emmip(
  modelo_1,
  Error_Prev ~ Predictability,
  CIs = TRUE,
  labs = list(
    y = "Log(PEM)",
    x = "predictability",
    title = "Interação: Previsibilidade × Erro"
  )
)

###############################################################
# 1. MODELO 2: adicionando BLOCO
###############################################################

# Reimporta dados (agora com variável block_info)
df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms.csv")

# Pré-processamento para modelo com bloco
df_clean <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, relMean_MEPpp_FDI,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),
    
    # Previsibilidade
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    # Erro anterior
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Acerto", "Erro")),
    
    # Bloco como fator (2–4–6)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer = factor(volunteer)
  )


###############################################################
# 2. Modelo com interação tripla (aprendizado ao longo dos blocos)
###############################################################

cat("\n=== AJUSTANDO MODELO DE APRENDIZADO (COM BLOCO) ===\n")

modelo_2 <- lmer(
  log_PEM ~ Predictability * Error_Prev * Block_Factor +
    (1 | volunteer),
  data = df_clean,
  REML = TRUE
)

# Resultados
print(summary(modelo_2))

cat("\n=== ANOVA TIPO III (Efeitos Fixos) ===\n")
print(anova(modelo_2, type = 3))


###############################################################
# 3. Diagnósticos do modelo com bloco
###############################################################

par(mfrow = c(2, 2))

qqnorm(resid(modelo_2),
       main = "Normalidade dos Resíduos (Modelo Bloco)")
qqline(resid(modelo_2), col = "red")

plot(
  fitted(modelo_2), resid(modelo_2),
  xlab = "Valores Ajustados",
  ylab = "Resíduos",
  main = "Homoscedasticidade",
  pch = 20, col = alpha("black", 0.2)
)
abline(h = 0, col = "red")

qqnorm(ranef(modelo_2)$volunteer[[1]],
       main = "Efeitos Aleatórios (Voluntários)")
qqline(ranef(modelo_2)$volunteer[[1]], col = "blue")

par(mfrow = c(1, 1))

check_model(modelo_2)


###############################################################
# 4. Visualização das interações estimadas (EMMs)
###############################################################

emmip(
  modelo_2,
  Block_Factor ~ Error_Prev | Predictability,
  CIs = TRUE,
  labs = list(
    y = "Log(PEM)",
    x = "Erro Anterior",
    title = "Interação: Previsibilidade × Erro × Bloco"
  )
)