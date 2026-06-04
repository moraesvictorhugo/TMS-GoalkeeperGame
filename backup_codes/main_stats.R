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
                   ~ Predictability * Error_Prev | Block_Factor,
                   tran = "log",
                   type = "response")

cat("\n=== EMMs - FDI (per Block) ===\n")
print(emm_FDI)

# Pairwise comparisons within each Block (Benjamini-Hochberg-adjusted)
cat("\n=== PAIRWISE CONTRASTS - FDI ===\n")
print(pairs(emm_FDI, adjust = "BH"))

# --- SIMPLE EFFECTS ---

# Simple effect de Predictability (6 contrastes)
cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - FDI ===\n")
print(emmeans(modelo_2_FDI,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              tran = "log",
              type = "response",
              adjust = "BH"))

# Simple effect de Error_Prev (6 contrastes)
cat("\n=== SIMPLE EFFECT OF PREVIOUS-ERROR - FDI ===\n")
print(emmeans(modelo_2_FDI,
              pairwise ~ Error_Prev | Predictability * Block_Factor,
              tran = "log",
              type = "response",
              adjust = "BH"))

###############################################################
# 7. FDI - TRIPLE INTERACTION VISUALIZATION
###############################################################
p_FDI <- emmip(modelo_2_FDI,
               Predictability ~ Error_Prev | Block_Factor,
               CIs   = FALSE,
               tran  = "log",         
               type  = "response",
               plotit = TRUE)

p_FDI <- p_FDI +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of MEP amplitude in FDI (µV)") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.10, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_FDI)
# ggsave("modelo_2_FDI.png", plot = p_FDI, width = 14, height = 8, dpi = 600)


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

cat("\n=== R² (marginal & conditional) - FDS ===\n")
print(performance::r2(modelo_2_FDS))

cat("\n=== PARTIAL ETA² - FDS ===\n")
print(effectsize::eta_squared(anova(modelo_2_FDS, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 11. FDS - POST-HOC: MARGINAL MEANS (no interaction → main effects only)
###############################################################

# Marginal mean: PREDICTABILITY (averaged over Error_Prev and Block)
cat("\n=== MARGINAL MEANS - PREDICTABILITY (FDS) ===\n")
emm_pred_FDS <- emmeans(modelo_2_FDS, ~ Predictability,
                        tran = "log", type = "response")
print(emm_pred_FDS)
print(pairs(emm_pred_FDS, adjust = "BH"))

# Marginal mean: ERROR_PREV (averaged over Predictability and Block)
cat("\n=== MARGINAL MEANS - PREVIOUS-ERROR (FDS) ===\n")
emm_err_FDS <- emmeans(modelo_2_FDS, ~ Error_Prev,
                       tran = "log", type = "response")
print(emm_err_FDS)
print(pairs(emm_err_FDS, adjust = "BH"))

# Marginal mean: BLOCK (averaged over Predictability and Error_Prev)
cat("\n=== MARGINAL MEANS - BLOCK (FDS) ===\n")
emm_block_FDS <- emmeans(modelo_2_FDS, ~ Block_Factor,
                         tran = "log", type = "response")
print(emm_block_FDS)
print(pairs(emm_block_FDS, adjust = "BH")) # 3 contrastes


###############################################################
# 12. FDS - TRIPLE INTERACTION VISUALIZATION
###############################################################
p_FDS <- emmip(modelo_2_FDS,
               Predictability ~ Error_Prev | Block_Factor,
               CIs   = FALSE,
               tran  = "log",
               type  = "response",
               plotit = TRUE)

p_FDS <- p_FDS +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of MEP amplitude in FDS (µV)") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.10, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_FDS)
# ggsave("modelo_2_FDS.png", plot = p_FDS, width = 14, height = 8, dpi = 600)

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

cat("\n=== R² (marginal & conditional) - RT ===\n")
print(performance::r2(modelo_2_RT))

cat("\n=== PARTIAL ETA² - RT ===\n")
print(effectsize::eta_squared(anova(modelo_2_RT, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 16. RT - POST-HOC: 3-WAY STRUCTURE (kept for reference)
###############################################################
# NOTE: Three-way interaction was non-significant (p = 0.792).
# The blocks below are exploratory/illustrative only.

emm_RT <- emmeans(modelo_2_RT,
                  ~ Predictability * Error_Prev | Block_Factor,
                  tran = "log",
                  type = "response")

cat("\n=== EMMs - RT (per Block) ===\n")
print(emm_RT)

cat("\n=== PAIRWISE CONTRASTS - RT (per Block) ===\n")
print(pairs(emm_RT, adjust = "BH"))

# --- SIMPLE EFFECTS (3-way) ---

cat("\n=== SIMPLE EFFECT OF PREDICTABILITY (per Error × Block) - RT ===\n")
print(emmeans(modelo_2_RT,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              tran = "log",
              type = "response",
              adjust = "BH"))

cat("\n=== SIMPLE EFFECT OF PREVIOUS-ERROR (per Predictability × Block) - RT ===\n")
print(emmeans(modelo_2_RT,
              pairwise ~ Error_Prev | Predictability * Block_Factor,
              tran = "log",
              type = "response",
              adjust = "BH"))


###############################################################
# 17. RT - POST-HOC: PRIMARY ANALYSIS (additions)
###############################################################
# The three-way interaction is non-significant (p = 0.792), but two
# two-way interactions are significant. They are decomposed below,
# independently, collapsing over the remaining factor.

# -------------------------------------------------------------
# 17a. MAIN EFFECT OF BLOCK
# (Block does not interact significantly with Error_Prev, p = 0.113,
#  and its interaction with Predictability is addressed in 17c)
# -------------------------------------------------------------
cat("\n=== MAIN EFFECT - BLOCK (RT) ===\n")
emm_block_RT <- emmeans(modelo_2_RT, ~ Block_Factor,
                        tran = "log", type = "response")
print(emm_block_RT)
print(pairs(emm_block_RT, adjust = "BH"))


# -------------------------------------------------------------
# 17b. PREDICTABILITY × PREVIOUS-ERROR INTERACTION
# (p = 0.012; collapsed over Block)
# -------------------------------------------------------------
cat("\n=== INTERACTION: PREDICTABILITY × PREVIOUS-ERROR (RT) ===\n")
emm_PxE_RT <- emmeans(modelo_2_RT,
                      ~ Predictability * Error_Prev,
                      tran = "log", type = "response")
print(emm_PxE_RT)

# Simple effect of Predictability within each Error_Prev
cat("\n--- Predictability | Error_Prev ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Predictability | Error_Prev,
                    tran = "log", type = "response"),
            adjust = "BH"))

# Simple effect of Error_Prev within each Predictability
cat("\n--- Error_Prev | Predictability ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Error_Prev | Predictability,
                    tran = "log", type = "response"),
            adjust = "BH"))


# -------------------------------------------------------------
# 17c. PREDICTABILITY × BLOCK INTERACTION
# (p = 0.043; collapsed over Error_Prev)
# -------------------------------------------------------------
cat("\n=== INTERACTION: PREDICTABILITY × BLOCK (RT) ===\n")
emm_PxB_RT <- emmeans(modelo_2_RT,
                      ~ Predictability * Block_Factor,
                      tran = "log", type = "response")
print(emm_PxB_RT)

# Simple effect of Predictability within each Block
cat("\n--- Predictability | Block ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Predictability | Block_Factor,
                    tran = "log", type = "response"),
            adjust = "BH"))

# Simple effect of Block within each Predictability
cat("\n--- Block | Predictability ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Block_Factor | Predictability,
                    tran = "log", type = "response"),
            adjust = "BH"))

# Pairwise contrasts
pairs(emmeans(modelo_2_RT, ~ Predictability, tran = "log", type = "response"))
pairs(emmeans(modelo_2_RT, ~ Error_Prev,    tran = "log", type = "response"))


# -------------------------------------------------------------
# 17d. PREDICTABILITY and PREV_ERROR MAIN EFFECTS
# -------------------------------------------------------------

emmeans(modelo_2_RT, ~ Predictability, tran = "log", type = "response")
emmeans(modelo_2_RT, ~ Error_Prev,    tran = "log", type = "response")

###############################################################
# 18. RT - VISUALIZATION
###############################################################

# --- Plot 1: Predictability × Error_Prev (collapsed over Block) ---
df_plot_PxE <- as.data.frame(emm_PxE_RT)

p_RT_PxE <- ggplot(df_plot_PxE,
                   aes(x = Error_Prev, y = response,
                       color = Predictability, group = Predictability)) +
  geom_line(size = 1) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
                width = 0.1, size = 0.8) +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  labs(x = "Previous random outcome",
       y = "EMM of Response Time (ms)",
       title = "Predictability × Previous-Error") +
  theme_minimal() +
  theme(
    axis.title   = element_text(size = 16),
    axis.text    = element_text(size = 13),
    plot.title   = element_text(size = 15, face = "bold"),
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 11)
  )

print(p_RT_PxE)

# --- Plot 2: Predictability × Block (collapsed over Error_Prev) ---
df_plot_PxB <- as.data.frame(emm_PxB_RT)

p_RT_PxB <- ggplot(df_plot_PxB,
                   aes(x = Block_Factor, y = response,
                       color = Predictability, group = Predictability)) +
  geom_line(size = 1) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
                width = 0.1, size = 0.8) +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  labs(x = "Block",
       y = "EMM of Response Time (ms)",
       title = "Predictability × Block") +
  theme_minimal() +
  theme(
    axis.title   = element_text(size = 16),
    axis.text    = element_text(size = 13),
    plot.title   = element_text(size = 15, face = "bold"),
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 11)
  )

print(p_RT_PxB)

###############################################################
# 17. RT - TRIPLE INTERACTION VISUALIZATION
###############################################################
p_RT <- emmip(modelo_2_RT,
              Predictability ~ Error_Prev | Block_Factor,
              CIs   = FALSE,
              tran  = "log",
              type  = "response",
              plotit = TRUE)

p_RT <- p_RT +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Response Time (ms)") +
  theme(
    axis.title        = element_text(size = 18),
    axis.text         = element_text(size = 14),
    strip.text        = element_text(size = 16),
    legend.title      = element_text(size = 13),
    legend.text       = element_text(size = 12),
    legend.position   = c(0.92, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_RT)
ggsave("modelo_2_RT.png", plot = p_RT, width = 14, height = 8, dpi = 600)