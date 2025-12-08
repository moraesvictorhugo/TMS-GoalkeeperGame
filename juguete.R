#  TESTANDO MODELO MISTO - PEMS 

#  paquetes 
# ---------------------------------
if(!require(tidyverse))  install.packages("tidyverse") 
if(!require(lme4)) install.packages("lme4")           
if(!require(lmerTest)) install.packages("lmerTest")  
if(!require(performance))  install.packages("performance") 
if(!require(see)) install.packages("see")

library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)

# limpiando y re-procesandp
# ------------------------------------

df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms.csv")

# filtrado y transform
df_clean <- df %>%
  # Filtrar apenas blocos com pulso de EMT
  filter(type_block == "Pulse") %>%
  
  # selecionar colunmas y remover NAs
  select(volunteer, trial, relMean_MEPpp_FDI, context, last_random_was_error) %>%
  drop_na() %>%
  
  # criar variaveis
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),
    
    #  agrupamento de contextos (Previsivel vs. ImPrevisivel)
    # contextos 1 e 10 sao Imprevis; 0, 2, 20 sao Previs
    Predictability = ifelse(context %in% c(1, 10), "Unpredictable", "Predictable"),
    
    #   converter em fatores
    Predictability = factor(Predictability, levels = c("Predictable", "Unpredictable")),
    Error_Prev = factor(last_random_was_error, levels = c(0, 1), labels = c("Acerto", "Erro")),
    volunteer = factor(volunteer)
  )

# Visualizar

table(df_clean$Predictability, df_clean$Error_Prev)



# ajuste do modelo linear misto (LMM)
# ---------------------------------------

# Primeiro Modelo: intercepto aleatorio por voluntario
# formula: log_PEM ~ Previsibilidade * Erro_Anterior + (1 | Voluntario)

modelo_misto <- lmer(log_PEM ~ Predictability * Error_Prev + (1 | volunteer), 
                     data = df_clean,
                     REML = TRUE) # REML é preferivel para estimativas de variancia

# resultados do modelo
summary(modelo_misto)

# diagnósticos 
# --------------------------------------------------------
#  pressupostos sobre os resíduos.

par(mfrow = c(2, 2))

# normalidade (desvios nas pontas sao comuns em dados biologicos...)
qqnorm(resid(modelo_misto), main = " Normalidade dos Resíduos")
qqline(resid(modelo_misto), col = "red")

# homoscedasticidade (resíduos vs. ajustados)
#  não deve haver padrao de funil.
plot(fitted(modelo_misto), resid(modelo_misto), 
     xlab = "Valores Ajustados", ylab = "Resíduos", 
     main = "Homoscedasticidade",
     pch = 20, col = alpha("black", 0.2))
abline(h = 0, col = "red")

# normalidade dos efeitos aleatorios
# os interceptos dos volunarios seguem uma distribuicao normal?
qqnorm(ranef(modelo_misto)$volunteer[[1]], main = " Normalidade dos Efeitos Aleatórios")
qqline(ranef(modelo_misto)$volunteer[[1]], col = "blue")

par(mfrow = c(1, 1))

# diagnostico automatico con pacote performance
# entre os graficos aparece influential observations que son candidatos a outliers tem que pensar o que significam...
# ------------------------------------------
check_model(modelo_misto)

#  teste de significancia dos efeitos fixos (ANOVA Tipo III), util 
# para confirmar a significancia da interacao
anova(modelo_misto, type = 3)



#
#
#
# Modelo com Bloco para testar efeito do aprendizado na excitabilidade

if(!require(emmeans)) install.packages("emmeans") # Recomendado para post-hoc de interações


library(emmeans)

df <- read.csv("df_gkg-tms.csv")

# filtrado y transform adicionei block na seleção de colunas
df_clean <- df %>%
  # Filtrar apenas blocos com pulso de EMT
  filter(type_block == "Pulse") %>%
  
  # selecionar colunmas y remover NAs
  select(volunteer, trial, block_info, relMean_MEPpp_FDI, context, last_random_was_error) %>%
  drop_na() %>%
  
  # criar variaveis
  mutate(
    log_PEM = log(relMean_MEPpp_FDI),
    
    #  agrupamento de contextos (Previsivel vs. ImPrevisivel)
    # contextos 1 e 10 sao Imprevis; 0, 2, 20 sao Previs
    Predictability = ifelse(context %in% c(1, 10), "Unpredictable", "Predictable"),
    
    #   converter em fatores
    Predictability = factor(Predictability, levels = c("Predictable", "Unpredictable")),
    Error_Prev = factor(last_random_was_error, levels = c(0, 1), labels = c("Acerto", "Erro")),
    # loco como Fator (para testar diferenças nao-lineares entre 2, 4 e 6)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer = factor(volunteer)  )






# segundo modelo: efeito do aprendizado
# =====================================
# para verificar se a modulação pelo contexto/erro muda ao longo do tempo.
# hipótese: a diferença entre previsivel/imprevisivel deve aumentar nos blocos finais.

print("=== AJUSTANDO MODELO DE APRENDIZADO (COM BLOCO) ===")

modelo_aprendizado <- lmer(log_PEM ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
                           data = df_clean,
                           REML = TRUE)

# Exibir Resultados
print(summary(modelo_aprendizado))

# teste de Significância dos Efeitos (ANOVA Tipo III)
print("=== ANOVA TIPO III (Efeitos Fixos) ===")
print(anova(modelo_aprendizado, type = 3))

# diagnósticos 
par(mfrow = c(2, 2))

qqnorm(resid(modelo_aprendizado), main = "Normalidade dos Resíduos (Modelo Bloco)")
qqline(resid(modelo_aprendizado), col = "red")

plot(fitted(modelo_aprendizado), resid(modelo_aprendizado), 
     xlab = "Valores Ajustados", ylab = "Resíduos", 
     main = " Homoscedasticidade",
     pch = 20, col = alpha("black", 0.2))
abline(h = 0, col = "red")
qqnorm(ranef(modelo_aprendizado)$volunteer[[1]], main = " Efeitos Aleatórios (Voluntários)")
qqline(ranef(modelo_aprendizado)$volunteer[[1]], col = "blue")
par(mfrow = c(1, 1))

check_model(modelo_aprendizado)

# As iterações são complicadas de visualizar, esto gera um gráfico das médias estimadas para interpretar ainteração tripla
emmip(modelo_aprendizado, Block_Factor ~ Error_Prev | Predictability, 
      CIs = TRUE, 
      labs = list(y = "Log(PEM)", x = "Erro Anterior", title = "Interação: Previsibilidade x Erro x Bloco"))



