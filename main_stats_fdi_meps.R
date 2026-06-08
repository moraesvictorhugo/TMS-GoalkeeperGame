###############################################################
# LINEAR MIXED EFFECTS MODELS - MEPs FDI ANALYSIS
# Order: Robust model > Simplest model > Aggregated RM-ANOVA
###############################################################


###############################################################
# 1. PACKAGES
###############################################################

if (!require(tidyverse))   install.packages("tidyverse")
if (!require(lme4))        install.packages("lme4")
if (!require(lmerTest))    install.packages("lmerTest")
if (!require(performance)) install.packages("performance")
if (!require(see))         install.packages("see")
if (!require(emmeans))     install.packages("emmeans")
if (!require(effectsize))  install.packages("effectsize")
if (!require(rstatix))     install.packages("rstatix")
if (!require(ggplot2))     install.packages("ggplot2")

library(tidyverse)
library(lme4)
library(lmerTest)
library(performance)
library(see)
library(emmeans)
library(effectsize)
library(rstatix)
library(ggplot2)


###############################################################
# 2. DATA IMPORT
###############################################################

df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms_2.csv")

###############################################################
# 3. FDI - PREPROCESSING
###############################################################

df_FDI <- df %>%
  filter(type_block == "Pulse") %>%
  group_by(volunteer, block_info) %>%
  mutate(trial_in_block = trial - min(trial) + 1) %>%
  ungroup() %>%
  select(volunteer, trial, block_info, MEPpp_FDI_µV,
         context, last_random_was_error, trial_in_block) %>%
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
    volunteer      = factor(volunteer),

    # Numeric dummies for uncorrelated random slopes (|| syntax)
    P_unpred = as.numeric(Predictability == "Unpredictable"),
    E_error  = as.numeric(Error_Prev == "Failure"),
    B4       = as.numeric(block_info == 4),
    B6       = as.numeric(block_info == 6),

    trial_in_block_z = as.numeric(scale(trial_in_block))
  ) %>%
  filter(block_info %in% c(2, 4, 6))

table(df_FDI$Predictability, df_FDI$Error_Prev)


###############################################################
#                                                             #
#                      ROBUST MODEL                           #
#                                                             #
###############################################################

###############################################################
# 4. FDI - ROBUST MODEL (random intercept + uncorrelated slopes)
###############################################################

cat("\n=== FITTING ROBUST MODEL FDI (random slopes) ===\n")

ctrl <- lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))

# Model
fdi_model <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = df_FDI, REML = TRUE, control = ctrl
)

print(summary(fdi_model))

cat("\n=== TYPE III ANOVA - FDI ROBUST MODEL ===\n")
print(anova(fdi_model, type = 3))

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - FDI MODEL ===\n")
print(isSingular(fdi_model))

# Convergence (was missing!)
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(fdi_model@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(fdi_model))

# --- 3. Assumptions (plot) ---
print(check_model(fdi_model))

###############################################################
# 5. FDI - EFFECT SIZES (ROBUST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - FDI ROBUST MODEL ===\n")
print(performance::r2(fdi_model))

cat("\n=== PARTIAL ETA² - FDI ROBUST MODEL ===\n")
print(effectsize::eta_squared(anova(fdi_model, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 6. FDI - POST-HOC (EMMEANS) - ROBUST MODEL
###############################################################

emm_FDI_rob <- emmeans(fdi_model,
                       ~ Predictability * Error_Prev | Block_Factor,
                       tran = "log", type = "response")

cat("\n=== EMMs - FDI ROBUST MODEL (per Block) ===\n")
print(emm_FDI_rob)

cat("\n=== PAIRWISE CONTRASTS - FDI ROBUST MODEL ===\n")
print(pairs(emm_FDI_rob, adjust = "BH"))

cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - FDI ROBUST MODEL ===\n")
print(emmeans(fdi_model,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              tran = "log", type = "response", adjust = "BH"))

cat("\n=== SIMPLE EFFECT OF PREVIOUS-ERROR - FDI ROBUST MODEL ===\n")
print(emmeans(fdi_model,
              pairwise ~ Error_Prev | Predictability * Block_Factor,
              tran = "log", type = "response", adjust = "BH"))


###############################################################
#                                                             #
#                       Simplest MODEL                        #
#                                                             #
###############################################################

###############################################################
# 7. FDI - SIMPLEST MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING SIMPLEST MODEL FDI: Predictability × Error × Block ===\n")

modelo_2_FDI <- lmer(
  log_MEP_FDI ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDI, REML = TRUE
)

print(summary(modelo_2_FDI))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDI, type = 3))

check_model(modelo_2_FDI)

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - FDI MODEL ===\n")
print(isSingular(modelo_2_FDI))

# Convergence (was missing!)
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(modelo_2_FDI@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(modelo_2_FDI))

# --- 3. Assumptions (plot) ---
print(check_model(modelo_2_FDI))

###############################################################
# 8. FDI - EFFECT SIZES (SIMPLEST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - FDI SIMPLEST MODEL ===\n")
print(performance::r2(modelo_2_FDI))

cat("\n=== PARTIAL ETA² - FDI SIMPLEST MODEL ===\n")
print(effectsize::eta_squared(anova(modelo_2_FDI, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 9. FDI - POST-HOC (EMMEANS) - SIMPLEST MODEL
###############################################################

emm_FDI <- emmeans(modelo_2_FDI,
                   ~ Predictability * Error_Prev | Block_Factor,
                   tran = "log", type = "response")

cat("\n=== EMMs - FDI (per Block) ===\n")
print(emm_FDI)

cat("\n=== PAIRWISE CONTRASTS - FDI ===\n")
print(pairs(emm_FDI, adjust = "BH"))

cat("\n=== SIMPLE EFFECT OF PREDICTABILITY - FDI ===\n")
print(emmeans(modelo_2_FDI,
              pairwise ~ Predictability | Error_Prev * Block_Factor,
              tran = "log", type = "response", adjust = "BH"))

cat("\n=== SIMPLE EFFECT OF PREVIOUS-ERROR - FDI ===\n")
print(emmeans(modelo_2_FDI,
              pairwise ~ Error_Prev | Predictability * Block_Factor,
              tran = "log", type = "response", adjust = "BH"))


###############################################################
# 10. FDI - TRIPLE INTERACTION VISUALIZATION (SIMPLEST MODEL)
###############################################################

p_FDI <- emmip(modelo_2_FDI,
               Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, tran = "log", type = "response", plotit = TRUE)

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
# ggsave("/analysis_outputs/modelo_2_FDI.png", plot = p_FDI,
#        width = 14, height = 8, dpi = 900)


###############################################################
#                                                             #
#                  AGGREGATED RM-ANOVA                        #
#                                                             #
###############################################################

###############################################################
# 11. FDI - AGGREGATED ANALYSIS BY PARTICIPANT × CONDITION
###############################################################

# Per-participant cell means + repeated-measures ANOVA
# (Greenhouse-Geisser correction; partial eta squared as effect size).

cat("\n=== AGGREGATED RM-ANOVA - FDI MEP ===\n")

cell_dat_FDI <- df_FDI %>%
  group_by(volunteer, Predictability, Error_Prev, Block_Factor) %>%
  summarise(mean_log_y = mean(log_MEP_FDI), n = n(), .groups = "drop")

cat("Cells:", nrow(cell_dat_FDI),
    "| Participants:", n_distinct(cell_dat_FDI$volunteer), "\n")

fdi_rm <- anova_test(
  data        = cell_dat_FDI,
  dv          = mean_log_y,
  wid         = volunteer,
  within      = c(Predictability, Error_Prev, Block_Factor),
  effect.size = "pes"
)

cat("\n=== RM-ANOVA TABLE (Greenhouse-Geisser) - FDI ===\n")
print(get_anova_table(fdi_rm, correction = "GG"))

###############################################################
# 12. FDI - COMPARATIVE RESULTS TABLE
###############################################################

normalize_term <- function(x) {
  vapply(strsplit(x, ":"), function(p) paste(sort(trimws(p)), collapse = ":"),
         character(1))
}

extract_lmer <- function(model, label) {
  aov_tab <- as.data.frame(anova(model, type = 3))
  eta     <- as.data.frame(effectsize::eta_squared(anova(model, type = 3),
                                                   partial = TRUE, ci = NULL))
  tibble(
    Term  = normalize_term(rownames(aov_tab)),
    F     = round(aov_tab$`F value`, 3),
    df1   = round(aov_tab$NumDF, 1),
    df2   = round(aov_tab$DenDF, 1),
    p     = round(aov_tab$`Pr(>F)`, 4),
    pEta2 = round(eta$Eta2_partial[match(rownames(aov_tab), eta$Parameter)], 3)
  ) %>% rename_with(~ paste0(.x, "_", label), -Term)
}

extract_rm <- function(rm_obj, label) {
  tab <- as.data.frame(get_anova_table(rm_obj, correction = "GG"))
  tibble(
    Term  = normalize_term(tab$Effect),
    F     = round(tab$F, 3),
    p     = round(tab$p, 4),
    pEta2 = round(tab$pes, 3)
  ) %>% rename_with(~ paste0(.x, "_", label), -Term)
}

tab_robust <- extract_lmer(fdi_model,     "Robust")
tab_simplest   <- extract_lmer(modelo_2_FDI, "SIMPLEST")
tab_rm     <- extract_rm(fdi_rm,          "RM")

comparison_FDI <- tab_robust %>%
  full_join(tab_simplest, by = "Term") %>%
  full_join(tab_rm,   by = "Term")

cat("\n=== COMPARATIVE RESULTS TABLE - FDI ===\n")
print(as.data.frame(comparison_FDI), row.names = FALSE)

# write.csv(comparison_FDI, "comparison_FDI.csv", row.names = FALSE)