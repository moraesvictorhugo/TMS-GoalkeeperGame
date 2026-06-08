###############################################################
# LINEAR MIXED EFFECTS MODELS - MEPs FDS ANALYSIS
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
# 3. FDS - PREPROCESSING
###############################################################

df_FDS <- df %>%
  filter(type_block == "Pulse") %>%
  group_by(volunteer, block_info) %>%
  mutate(trial_in_block = trial - min(trial) + 1) %>%
  ungroup() %>%
  select(volunteer, trial, block_info, MEPpp_FDS_µV,
         context, last_random_was_error, trial_in_block) %>%
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
    volunteer      = factor(volunteer),

    # Numeric dummies for uncorrelated random slopes (|| syntax)
    P_unpred = as.numeric(Predictability == "Unpredictable"),
    E_error  = as.numeric(Error_Prev == "Failure"),
    B4       = as.numeric(block_info == 4),
    B6       = as.numeric(block_info == 6),

    trial_in_block_z = as.numeric(scale(trial_in_block))
  ) %>%
  filter(block_info %in% c(2, 4, 6))

table(df_FDS$Predictability, df_FDS$Error_Prev)


###############################################################
#                                                             #
#                      ROBUST MODEL                           #
#                                                             #
###############################################################

###############################################################
# 4. FDS - ROBUST MODEL (random intercept + uncorrelated slopes)
###############################################################

cat("\n=== FITTING ROBUST MODEL FDS (random slopes) ===\n")

ctrl <- lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))

# Model
fds_model <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = df_FDS, REML = TRUE, control = ctrl
)

print(summary(fds_model))

cat("\n=== TYPE III ANOVA - FDS ROBUST MODEL ===\n")
print(anova(fds_model, type = 3))

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - FDS MODEL ===\n")
print(isSingular(fds_model))

# Convergence
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(fds_model@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(fds_model))

# --- 3. Assumptions (plot) ---
print(check_model(fds_model))


###############################################################
# 5. FDS - EFFECT SIZES (ROBUST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - FDS ROBUST MODEL ===\n")
print(performance::r2(fds_model))

cat("\n=== PARTIAL ETA² - FDS ROBUST MODEL ===\n")
print(effectsize::eta_squared(anova(fds_model, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 6. FDS - POST-HOC (EMMEANS) - ROBUST MODEL (main effects only)
###############################################################

cat("\n=== MARGINAL MEANS - PREDICTABILITY (FDS ROBUST) ===\n")
emm_pred_FDS_rob <- emmeans(fds_model, ~ Predictability,
                            tran = "log", type = "response")
print(emm_pred_FDS_rob)
print(pairs(emm_pred_FDS_rob, adjust = "BH"))

cat("\n=== MARGINAL MEANS - PREVIOUS-ERROR (FDS ROBUST) ===\n")
emm_err_FDS_rob <- emmeans(fds_model, ~ Error_Prev,
                           tran = "log", type = "response")
print(emm_err_FDS_rob)
print(pairs(emm_err_FDS_rob, adjust = "BH"))

cat("\n=== MARGINAL MEANS - BLOCK (FDS ROBUST) ===\n")
emm_block_FDS_rob <- emmeans(fds_model, ~ Block_Factor,
                             tran = "log", type = "response")
print(emm_block_FDS_rob)
print(pairs(emm_block_FDS_rob, adjust = "BH"))


###############################################################
#                                                             #
#                       Simplest MODEL                        #
#                                                             #
###############################################################

###############################################################
# 7. FDS - SIMPLEST MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING SIMPLEST MODEL FDS: Predictability × Error × Block ===\n")

modelo_2_FDS <- lmer(
  log_MEP_FDS ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_FDS, REML = TRUE
)

print(summary(modelo_2_FDS))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_FDS, type = 3))

check_model(modelo_2_FDS)

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - FDS MODEL ===\n")
print(isSingular(modelo_2_FDS))

# Convergence
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(modelo_2_FDS@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(modelo_2_FDS))

# --- 3. Assumptions (plot) ---
print(check_model(modelo_2_FDS))


###############################################################
# 8. FDS - EFFECT SIZES (SIMPLEST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - FDS SIMPLEST MODEL ===\n")
print(performance::r2(modelo_2_FDS))

cat("\n=== PARTIAL ETA² - FDS SIMPLEST MODEL ===\n")
print(effectsize::eta_squared(anova(modelo_2_FDS, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 9. FDS - POST-HOC (EMMEANS) - SIMPLEST MODEL (main effects only)
###############################################################

cat("\n=== MARGINAL MEANS - PREDICTABILITY (FDS) ===\n")
emm_pred_FDS <- emmeans(modelo_2_FDS, ~ Predictability,
                        tran = "log", type = "response")
print(emm_pred_FDS)
print(pairs(emm_pred_FDS, adjust = "BH"))

cat("\n=== MARGINAL MEANS - PREVIOUS-ERROR (FDS) ===\n")
emm_err_FDS <- emmeans(modelo_2_FDS, ~ Error_Prev,
                       tran = "log", type = "response")
print(emm_err_FDS)
print(pairs(emm_err_FDS, adjust = "BH"))

cat("\n=== MARGINAL MEANS - BLOCK (FDS) ===\n")
emm_block_FDS <- emmeans(modelo_2_FDS, ~ Block_Factor,
                         tran = "log", type = "response")
print(emm_block_FDS)
print(pairs(emm_block_FDS, adjust = "BH"))


###############################################################
# 10. FDS - TRIPLE INTERACTION VISUALIZATION (SIMPLEST MODEL)
###############################################################

p_FDS <- emmip(modelo_2_FDS,
               Predictability ~ Error_Prev | Block_Factor,
               CIs = FALSE, tran = "log", type = "response", plotit = TRUE)

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
# ggsave("/analysis_outputs/modelo_2_FDS.png", plot = p_FDS,
#        width = 14, height = 8, dpi = 900)


###############################################################
#                                                             #
#                  AGGREGATED RM-ANOVA                        #
#                                                             #
###############################################################

###############################################################
# 11. FDS - AGGREGATED ANALYSIS BY PARTICIPANT × CONDITION
###############################################################

# Per-participant cell means + repeated-measures ANOVA
# (Greenhouse-Geisser correction; partial eta squared as effect size).

cat("\n=== AGGREGATED RM-ANOVA - FDS MEP ===\n")

cell_dat_FDS <- df_FDS %>%
  group_by(volunteer, Predictability, Error_Prev, Block_Factor) %>%
  summarise(mean_log_y = mean(log_MEP_FDS), n = n(), .groups = "drop")

cat("Cells:", nrow(cell_dat_FDS),
    "| Participants:", n_distinct(cell_dat_FDS$volunteer), "\n")

fds_rm <- anova_test(
  data        = cell_dat_FDS,
  dv          = mean_log_y,
  wid         = volunteer,
  within      = c(Predictability, Error_Prev, Block_Factor),
  effect.size = "pes"
)

cat("\n=== RM-ANOVA TABLE (Greenhouse-Geisser) - FDS ===\n")
print(get_anova_table(fds_rm, correction = "GG"))


###############################################################
# 12. FDS - COMPARATIVE RESULTS TABLE
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

tab_robust   <- extract_lmer(fds_model,     "Robust")
tab_simplest <- extract_lmer(modelo_2_FDS,  "SIMPLEST")
tab_rm       <- extract_rm(fds_rm,          "RM")

comparison_FDS <- tab_robust %>%
  full_join(tab_simplest, by = "Term") %>%
  full_join(tab_rm,       by = "Term")

cat("\n=== COMPARATIVE RESULTS TABLE - FDS ===\n")
print(as.data.frame(comparison_FDS), row.names = FALSE)

# write.csv(comparison_FDS, "comparison_FDS.csv", row.names = FALSE)