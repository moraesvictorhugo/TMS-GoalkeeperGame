###############################################################
# LINEAR MIXED EFFECTS MODELS - PEMS FDI ANALYSIS
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
if (!require(emmeans))     install.packages("emmeans")     # Post-hoc tests

# Load required libraries
library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)
library(emmeans)

###############################################################
# 2. DATA IMPORT AND PREPROCESSING
###############################################################

# Import dataset
df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms_2.csv")

# Create clean dataset for FDI analysis (Pulse trials only)
df_FDI <- df %>%
  filter(type_block == "Pulse") %>%                                    # Keep only Pulse TMS trials
  select(volunteer, trial, block_info, MEPpp_FDI_µV,                   # Select relevant columns
         context, last_random_was_error) %>%
  drop_na() %>%                                                       # Remove rows with missing values
  mutate(
    log_MEP_FDI = log(MEPpp_FDI_µV),                                  # Log-transform MEP amplitude (log-normal dist.)
    
    # Predictability factor (Unpredictable = context 1,10)
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,                            # Convert to ordered factor
                            levels = c("Predictable", "Unpredictable")), # Predictable as reference
    
    # Previous trial error (0=Correct, 1=Error)
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),              # Correct as reference
    
    # Block factor (learning progression: Block 2→4→6)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),           # Block 2 as reference
    
    # Ensure volunteer is factor for random effects
    volunteer = factor(volunteer)
  )

# Check condition distribution (balance check)
table(df_FDI$Predictability, df_FDI$Error_Prev)

###############################################################
# 3. MODEL 1 - Predictability × Previous Error (Main effects + interaction)
###############################################################

cat("\n=== FITTING MODEL 1: Predictability × Previous Error ===\n")

# Mixed model with random intercept per volunteer
modelo_1_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev + (1 | volunteer),       # Fixed: interaction + Random: volunteer intercept
  data = df_FDI,
  REML = TRUE                                                        # Restricted Maximum Likelihood
)

# Model summary (coefficients, p-values)
summary(modelo_1_FDI)

# Type III ANOVA (sequential F-tests for fixed effects)
anova(modelo_1_FDI, type = 3)

###############################################################
# 4. MODEL DIAGNOSTICS (Automated)
###############################################################
check_model(modelo_1_FDI)                                               # Residuals, QQ, homogeneity checks

###############################################################
# 5. INTERACTION PLOTS - Estimated Marginal Means
###############################################################

# Predictability × Error interaction
emmip(modelo_1_FDI, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_FDI, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 6. MODEL 2 - Triple Interaction (Predictability × Error × Block/Learning)
###############################################################

cat("\n=== FITTING MODEL 2: Predictability × Error × Block ===\n")

# Full model with triple interaction + learning effect across blocks
modelo_2_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDI,
  REML = TRUE
)

# Model results
print(summary(modelo_2_FDI))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDI, type = 3))

###############################################################
# 7. MODEL 2 DIAGNOSTICS
###############################################################
check_model(modelo_2_FDI)

###############################################################
# 8. TRIPLE INTERACTION VISUALIZATION
###############################################################

# Three-way interaction plots (condition by condition)
emmip(modelo_2_FDI, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_FDI, Predictability ~ Error_Prev | Block_Factor, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Previous Error",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_FDI, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDI)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

# ------------------------------------------------------------------------------
###############################################################
# 9. DATA IMPORT AND PREPROCESSING
###############################################################

# Create clean dataset for FDI analysis (Pulse trials only)
df_FDS <- df %>%
  filter(type_block == "Pulse") %>%                                    # Keep only Pulse TMS trials
  select(volunteer, trial, block_info, MEPpp_FDS_µV,                   # Select relevant columns
         context, last_random_was_error) %>%
  drop_na() %>%                                                       # Remove rows with missing values
  mutate(
    log_MEP_FDS = log(MEPpp_FDS_µV),                                  # Log-transform MEP amplitude (log-normal dist.)
    
    # Predictability factor (Unpredictable = context 1,10)
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,                            # Convert to ordered factor
                            levels = c("Predictable", "Unpredictable")), # Predictable as reference
    
    # Previous trial error (0=Correct, 1=Error)
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),              # Correct as reference
    
    # Block factor (learning progression: Block 2→4→6)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),           # Block 2 as reference
    
    # Ensure volunteer is factor for random effects
    volunteer = factor(volunteer)
  )

# Check condition distribution (balance check)
table(df_FDS$Predictability, df_FDS$Error_Prev)

###############################################################
# 10. MODEL 1 - Predictability × Previous Error (Main effects + interaction)
###############################################################

cat("\n=== FITTING MODEL 1: Predictability × Previous Error ===\n")

# Mixed model with random intercept per volunteer
modelo_1_FDS <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev + (1 | volunteer),       # Fixed: interaction + Random: volunteer intercept
  data = df_FDS,
  REML = TRUE                                                        # Restricted Maximum Likelihood
)

# Model summary (coefficients, p-values)
summary(modelo_1_FDS)

# Type III ANOVA (sequential F-tests for fixed effects)
anova(modelo_1_FDS, type = 3)

###############################################################
# 11. MODEL DIAGNOSTICS (Automated)
###############################################################
check_model(modelo_1_FDS)                                               # Residuals, QQ, homogeneity checks

###############################################################
# 12. INTERACTION PLOTS - Estimated Marginal Means
###############################################################

# Predictability × Error interaction
emmip(modelo_1_FDS, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_FDS, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 13. MODEL 2 - Triple Interaction (Predictability × Error × Block/Learning)
###############################################################

cat("\n=== FITTING MODEL 2: Predictability × Error × Block ===\n")

# Full model with triple interaction + learning effect across blocks
modelo_2_FDS <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDS,
  REML = TRUE
)

# Model results
print(summary(modelo_2_FDS))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDS, type = 3))

###############################################################
# 14. MODEL 2 DIAGNOSTICS
###############################################################
check_model(modelo_2_FDS)

###############################################################
# 15. TRIPLE INTERACTION VISUALIZATION
###############################################################

# Three-way interaction plots (condition by condition)
emmip(modelo_2_FDS, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_FDS, Predictability ~ Error_Prev | Block_Factor, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Previous Error",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_FDS, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(MEP FDS)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

# ------------------------------------------------------------------------------
###############################################################
# 16. DATA IMPORT AND PREPROCESSING
###############################################################

# Create clean dataset for RT analysis (Pulse trials only)
df_RT <- df %>%
  filter(type_block == "Pulse") %>%                                    # Keep only Pulse TMS trials
  select(volunteer, trial, block_info, response_time,                   # Select relevant columns
         context, last_random_was_error) %>%
  drop_na() %>%                                                       # Remove rows with missing values
  mutate(
    log_RT = log(response_time),                                      # Log-transform RT
    
    # Predictability factor (Unpredictable = context 1,10)
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,                            # Convert to ordered factor
                            levels = c("Predictable", "Unpredictable")), # Predictable as reference
    
    # Previous trial error (0=Correct, 1=Error)
    Error_Prev = factor(last_random_was_error,
                        levels = c(0, 1),
                        labels = c("Correct", "Error")),              # Correct as reference
    
    # Block factor (learning progression: Block 2→4→6)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),           # Block 2 as reference
    
    # Ensure volunteer is factor for random effects
    volunteer = factor(volunteer)
  )

# Check condition distribution (balance check)
table(df_RT$Predictability, df_RT$Error_Prev)

###############################################################
# 17. MODEL 1 - Predictability × Previous Error (Main effects + interaction)
###############################################################

cat("\n=== FITTING MODEL 1: Predictability × Previous Error ===\n")

# Mixed model with random intercept per volunteer
modelo_1_RT <- lmer(
  log_RT ~ Predictability * Error_Prev + (1 | volunteer),       # Fixed: interaction + Random: volunteer intercept
  data = df_RT,
  REML = TRUE                                                        # Restricted Maximum Likelihood
)

# Model summary (coefficients, p-values)
summary(modelo_1_RT)

# Type III ANOVA (sequential F-tests for fixed effects)
anova(modelo_1_RT, type = 3)

###############################################################
# 18. MODEL DIAGNOSTICS (Automated)
###############################################################
check_model(modelo_1_RT)                                               # Residuals, QQ, homogeneity checks

###############################################################
# 19. INTERACTION PLOTS - Estimated Marginal Means
###############################################################

# Predictability × Error interaction
emmip(modelo_1_RT, Error_Prev ~ Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Predictability",
                  title = "Interaction: Predictability × Error"))

emmip(modelo_1_RT, Predictability ~ Error_Prev, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Previous Error",
                  title = "Interaction: Predictability × Error"))

###############################################################
# 20. MODEL 2 - Triple Interaction (Predictability × Error × Block/Learning)
###############################################################

cat("\n=== FITTING MODEL 2: Predictability × Error × Block ===\n")

# Full model with triple interaction + learning effect across blocks
modelo_2_RT <- lmer(
  log_RT ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_RT,
  REML = TRUE
)

# Model results
print(summary(modelo_2_RT))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_RT, type = 3))

###############################################################
# 21. MODEL 2 DIAGNOSTICS
###############################################################
check_model(modelo_2_RT)

###############################################################
# 22. TRIPLE INTERACTION VISUALIZATION
###############################################################

# Three-way interaction plots (condition by condition)
emmip(modelo_2_RT, Block_Factor ~ Error_Prev | Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_RT, Predictability ~ Error_Prev | Block_Factor, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Previous Error",
                  title = "Triple Interaction: Predictability × Error × Block"))

emmip(modelo_2_RT, Error_Prev ~ Block_Factor | Predictability, CIs = FALSE,
      labs = list(y = "Log(RT)", x = "Block",
                  title = "Triple Interaction: Predictability × Error × Block"))
