###############################################################
# LINEAR MIXED EFFECTS MODELS - PEMS FDI / FDS / RT ANALYSIS
###############################################################


###############################################################
# 1. PACKAGES
###############################################################

# Auto-install missing packages
if (!require(tidyverse))   install.packages("tidyverse")
if (!require(lme4))        install.packages("lme4")
if (!require(lmerTest))    install.packages("lmerTest")
if (!require(performance)) install.packages("performance")
if (!require(see))         install.packages("see")
if (!require(emmeans))     install.packages("emmeans")
if (!require(effectsize))  install.packages("effectsize")   # NEW: effect sizes
if (!require(ggplot2))     install.packages("ggplot2")

# Load required libraries
library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)
library(emmeans)
library(effectsize)
library(ggplot2)


###############################################################
# 2. DATA IMPORT
###############################################################

df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms_2.csv")


###############################################################
#                                                             #
#                        FDI ANALYSIS                         #
#                                                             #
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
    log_MEP_FDI    = log(MEPpp_FDI_µV),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev     = factor(last_random_was_error,
                            levels = c(0, 1),
                            labels = c("Success", "Failure")),
    
    Block_Factor   = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer      = factor(volunteer)
  )

table(df_FDI$Predictability, df_FDI$Error_Prev)


###############################################################
# 4. FDI - MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL FDI: Predictability × Error × Block ===\n")

modelo_2_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDI,
  REML = TRUE
)

print(summary(modelo_2_FDI))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDI, type = 3))

# Diagnostics
check_model(modelo_2_FDI)


###############################################################
# 5. FDI - EFFECT SIZES
###############################################################

# R² marginal = variance explained by fixed effects only
# R² conditional = variance explained by fixed + random effects
cat("\n=== R² (marginal & conditional) - FDI ===\n")
print(performance::r2(modelo_2_FDI))

# Partial eta² for each fixed-effect term in the Type III ANOVA table
cat("\n=== PARTIAL ETA² - FDI ===\n")
print(effectsize::eta_squared(anova(modelo_2_FDI, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 6. FDI - POST-HOC (EMMEANS)
###############################################################

# Estimated marginal means for the full 3-way structure
emm_FDI <- emmeans(modelo_2_FDI,
                   ~ Predictability * Error_Prev | Block_Factor)

cat("\n=== EMMs - FDI (per Block) ===\n")
print(emm_FDI)

# Pairwise comparisons within each Block (Benjamini-Hochberg-adjusted)
cat("\n=== PAIRWISE CONTRASTS - FDI ===\n")
print(pairs(emm_FDI, adjust = "BH"))

# Simple effect: Predictability within each Error_Prev × Block combination
cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - FDI ===\n")
print(emmeans(modelo_2_FDI,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              adjust = "bonferroni"))


###############################################################
# 7. FDI - TRIPLE INTERACTION VISUALIZATION
###############################################################

# Custom plot — Predictability × Error | Block
p_FDI <- emmip(modelo_2_FDI, Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, plotit = TRUE)

p_FDI <- p_FDI +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log MEP Amplitude in FDI") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.11, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_FDI)
# ggsave("modelo_2_FDI.png", plot = p_FDI, width = 10, height = 6, dpi = 600)


###############################################################
#                                                             #
#                        FDS ANALYSIS                         #
#                                                             #
###############################################################

###############################################################
# 8. FDS - PREPROCESSING
###############################################################

df_FDS <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, MEPpp_FDS_µV,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    log_MEP_FDS    = log(MEPpp_FDS_µV),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev     = factor(last_random_was_error,
                            levels = c(0, 1),
                            labels = c("Success", "Failure")),
    
    Block_Factor   = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer      = factor(volunteer)
  )

table(df_FDS$Predictability, df_FDS$Error_Prev)


###############################################################
# 9. FDS - MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL FDS: Predictability × Error × Block ===\n")

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
# 10. FDS - EFFECT SIZES
###############################################################

# R² marginal (fixed only) and conditional (fixed + random)
cat("\n=== R² (marginal & conditional) - FDS ===\n")
print(performance::r2(modelo_2_FDS))

# Partial eta² for each fixed-effect term
cat("\n=== PARTIAL ETA² - FDS ===\n")
print(effectsize::eta_squared(anova(modelo_2_FDS, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 11. FDS - POST-HOC (EMMEANS)
###############################################################

# Estimated marginal means for the full 3-way structure
emm_FDS <- emmeans(modelo_2_FDS,
                   ~ Predictability * Error_Prev | Block_Factor)

cat("\n=== EMMs - FDS (per Block) ===\n")
print(emm_FDS)

# Pairwise comparisons within each Block (Benjamini-Hochberg-adjusted)
cat("\n=== PAIRWISE CONTRASTS - FDS ===\n")
print(pairs(emm_FDS, adjust = "BH"))

# Simple effect: Predictability within each Error_Prev × Block combination
cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - FDS ===\n")
print(emmeans(modelo_2_FDS,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              adjust = "bonferroni"))


###############################################################
# 12. FDS - TRIPLE INTERACTION VISUALIZATION
###############################################################

# Custom plot — Predictability × Error | Block
p_FDS <- emmip(modelo_2_FDS, Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, plotit = TRUE)

p_FDS <- p_FDS +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log MEP Amplitude in FDS") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.11, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_FDS)
# ggsave("modelo_2_FDS.png", plot = p_FDS, width = 10, height = 6, dpi = 300)


###############################################################
#                                                             #
#                         RT ANALYSIS                         #
#                                                             #
###############################################################

###############################################################
# 13. RT - PREPROCESSING
###############################################################

df_RT <- df %>%
  filter(type_block == "Pulse") %>%
  select(volunteer, trial, block_info, response_time,
         context, last_random_was_error) %>%
  drop_na() %>%
  mutate(
    response_time  = response_time * 1000,
    log_RT         = log(response_time),
    
    Predictability = ifelse(context %in% c(1, 10),
                            "Unpredictable", "Predictable"),
    Predictability = factor(Predictability,
                            levels = c("Predictable", "Unpredictable")),
    
    Error_Prev     = factor(last_random_was_error,
                            levels = c(0, 1),
                            labels = c("Success", "Failure")),
    
    Block_Factor   = factor(block_info, levels = c(2, 4, 6)),
    
    volunteer      = factor(volunteer)
  )

table(df_RT$Predictability, df_RT$Error_Prev)


###############################################################
# 14. RT - MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING MODEL RT: Predictability × Error × Block ===\n")

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
# 15. RT - EFFECT SIZES
###############################################################

# R² marginal (fixed only) and conditional (fixed + random)
cat("\n=== R² (marginal & conditional) - RT ===\n")
print(performance::r2(modelo_2_RT))

# Partial eta² for each fixed-effect term
cat("\n=== PARTIAL ETA² - RT ===\n")
print(effectsize::eta_squared(anova(modelo_2_RT, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 16. RT - POST-HOC (EMMEANS)
###############################################################

# Estimated marginal means for the full 3-way structure
emm_RT <- emmeans(modelo_2_RT,
                  ~ Predictability * Error_Prev | Block_Factor)

cat("\n=== EMMs - RT (per Block) ===\n")
print(emm_RT)

# Pairwise comparisons within each Block (Benjamini-Hochberg-adjusted)
cat("\n=== PAIRWISE CONTRASTS - RT ===\n")
print(pairs(emm_RT, adjust = "BH"))

# Simple effect: Predictability within each Error_Prev × Block combination
cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - RT ===\n")
print(emmeans(modelo_2_RT,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              adjust = "bonferroni"))


###############################################################
# 17. RT - TRIPLE INTERACTION VISUALIZATION
###############################################################

# Custom plot — Predictability × Error | Block
p_RT <- emmip(modelo_2_RT, Predictability ~ Error_Prev | Block_Factor,
              CIs = FALSE, plotit = TRUE)

p_RT <- p_RT +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Log Response Time") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.11, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_RT)
# ggsave("modelo_2_RT.png", plot = p_RT, width = 10, height = 6, dpi = 300)
