###############################################################
# LINEAR MIXED EFFECTS MODELS - PEMS FDI / FDS / RT ANALYSIS
###############################################################

###############################
# 1. PACKAGES
###############################

# Auto-install missing packages
if (!require(tidyverse))   install.packages("tidyverse")
if (!require(lme4))        install.packages("lme4")
if (!require(lmerTest))    install.packages("lmerTest")
if (!require(performance)) install.packages("performance")
if (!require(see))         install.packages("see")
if (!require(emmeans))     install.packages("emmeans")
if (!require(ggplot2))     install.packages("ggplot2")

# Load required libraries
library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)
library(emmeans)
library(ggplot2)

###############################################################
# 2. DATA IMPORT
###############################################################

df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms_2.csv")

###############################################################
#
#                         FDI ANALYSIS
#
###############################################################

###############################################################
# 3. FDI - PREPROCESSING
###############################################################

df_FDI <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, MEPpp_FDI_µV,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_MEP_FDI = log(MEPpp_FDI_µV),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),
    
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer = factor(volunteer)
  )

table(df_FDI$Predictability, df_FDI$Error_Prev)

###############################################################
# 4. FDI - MODEL 1: Predictability × Previous Error
###############################################################

cat("\n=== FITTING MODEL 1 FDI: Predictability × Previous Error ===\n")

modelo_1_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev + (1 | volunteer),
  data = df_FDI,
  REML = TRUE
)

summary(modelo_1_FDI)
anova(modelo_1_FDI, type = 3)

# Diagnostics
check_model(modelo_1_FDI)

# Interaction plots
emmip(modelo_1_FDI, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_FDI, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 5. FDI - MODEL 2: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL 2 FDI: Predictability × Error × Block ===\n")

modelo_2_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDI,
  REML = TRUE
)

print(summary(modelo_2_FDI))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDI, type = 3))

# Estimated means at Block 6
emmeans(modelo_2_FDI,
        ~ Predictability * Error_Prev,
        at = list(Block_Factor = "6")) |>
  summary() |>
  transform(MEP_uV = exp(emmean))

# Diagnostics
check_model(modelo_2_FDI)

###############################################################
# 6. FDI - TRIPLE INTERACTION VISUALIZATION
###############################################################

emmip(modelo_2_FDI, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

# Custom plot — Predictability × Error | Block
p_FDI <- emmip(modelo_2_FDI, Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, plotit = TRUE)

p_FDI <- p_FDI +
  scale_color_manual(values = c("Predictable" = "grey60", "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor, labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log MEP Amplitude in FDI") +
  theme(axis.title = element_text(size = 12))

print(p_FDI)
ggsave("modelo_2_FDI.png", plot = p_FDI, width = 10, height = 6, dpi = 300)

emmip(modelo_2_FDI, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

###############################################################
#
#                         FDS ANALYSIS
#
###############################################################

###############################################################
# 7. FDS - PREPROCESSING
###############################################################

df_FDS <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, MEPpp_FDS_µV,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_MEP_FDS = log(MEPpp_FDS_µV),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),
    
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer = factor(volunteer)
  )

table(df_FDS$Predictability, df_FDS$Error_Prev)

###############################################################
# 8. FDS - MODEL 1: Predictability × Previous Error
###############################################################

cat("\n=== FITTING MODEL 1 FDS: Predictability × Previous Error ===\n")

modelo_1_FDS <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev + (1 | volunteer),
  data = df_FDS,
  REML = TRUE
)

summary(modelo_1_FDS)
anova(modelo_1_FDS, type = 3)

# Diagnostics
check_model(modelo_1_FDS)

# Interaction plots
emmip(modelo_1_FDS, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_FDS, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 9. FDS - MODEL 2: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL 2 FDS: Predictability × Error × Block ===\n")

modelo_2_FDS <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDS,
  REML = TRUE
)

print(summary(modelo_2_FDS))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDS, type = 3))

# Diagnostics
check_model(modelo_2_FDS)

###############################################################
# 10. FDS - TRIPLE INTERACTION VISUALIZATION
###############################################################

emmip(modelo_2_FDS, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

# Custom plot — Predictability × Error | Block
p_FDS <- emmip(modelo_2_FDS, Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, plotit = TRUE)

p_FDS <- p_FDS +
  scale_color_manual(values = c("Predictable" = "grey60", "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor, labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log MEP Amplitude in FDS") +
  theme(axis.title = element_text(size = 12))

print(p_FDS)
ggsave("modelo_2_FDS.png", plot = p_FDS, width = 10, height = 6, dpi = 300)

emmip(modelo_2_FDS, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

###############################################################
#
#                         RT ANALYSIS
#
###############################################################

###############################################################
# 11. RT - PREPROCESSING
###############################################################

df_RT <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, response_time,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    response_time = response_time * 1000,
    log_RT = log(response_time),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),
    
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer = factor(volunteer)
  )

table(df_RT$Predictability, df_RT$Error_Prev)

###############################################################
# 12. RT - MODEL 1: Predictability × Previous Error
###############################################################

cat("\n=== FITTING MODEL 1 RT: Predictability × Previous Error ===\n")

modelo_1_RT <- lmer(
  log_RT ~ Predictability * Error_Prev + (1 | volunteer),
  data = df_RT,
  REML = TRUE
)

summary(modelo_1_RT)
anova(modelo_1_RT, type = 3)

# Diagnostics
check_model(modelo_1_RT)

# Interaction plots
emmip(modelo_1_RT, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_RT, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 13. RT - MODEL 2: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL 2 RT: Predictability × Error × Block ===\n")

modelo_2_RT <- lmer(
  log_RT ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_RT,
  REML = TRUE
)

print(summary(modelo_2_RT))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_RT, type = 3))

# Diagnostics
check_model(modelo_2_RT)

###############################################################
# 14. RT - TRIPLE INTERACTION VISUALIZATION
###############################################################

emmip(modelo_2_RT, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

# Custom plot — Predictability × Error | Block
p_RT <- emmip(modelo_2_RT, Predictability ~ Error_Prev | Block_Factor,
              CIs = FALSE, plotit = TRUE)

p_RT <- p_RT +
  scale_color_manual(values = c("Predictable" = "grey60", "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor, labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log Response Time") +
  theme(axis.title = element_text(size = 12))

print(p_RT)
ggsave("modelo_2_RT.png", plot = p_RT, width = 10, height = 6, dpi = 300)

emmip(modelo_2_RT, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))