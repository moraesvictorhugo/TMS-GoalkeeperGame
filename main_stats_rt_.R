###############################################################
# LINEAR MIXED EFFECTS MODELS - RTs ANALYSIS
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
# 3. RT - PREPROCESSING
###############################################################

df_RT <- df %>%
  filter(type_block == "Pulse") %>%
  group_by(volunteer, block_info) %>%
  mutate(trial_in_block = trial - min(trial) + 1) %>%
  ungroup() %>%
  select(volunteer, trial, block_info, response_time,
         context, last_random_was_error, trial_in_block) %>%
  drop_na() %>%
  filter(response_time > 0) %>%
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
    volunteer      = factor(volunteer),

    # Numeric dummies for uncorrelated random slopes (|| syntax)
    P_unpred = as.numeric(Predictability == "Unpredictable"),
    E_error  = as.numeric(Error_Prev == "Failure"),
    B4       = as.numeric(block_info == 4),
    B6       = as.numeric(block_info == 6),

    trial_in_block_z = as.numeric(scale(trial_in_block))
  ) %>%
  filter(block_info %in% c(2, 4, 6))

table(df_RT$Predictability, df_RT$Error_Prev)


###############################################################
#                                                             #
#                      ROBUST MODEL                           #
#                                                             #
###############################################################

###############################################################
# 4. RT - ROBUST MODEL (random intercept + uncorrelated slopes)
###############################################################

cat("\n=== FITTING ROBUST MODEL RT (random slopes) ===\n")

ctrl <- lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))

# Model
rt_model <- lmer(
  log_RT ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = df_RT, REML = TRUE, control = ctrl
)

print(summary(rt_model))

cat("\n=== TYPE III ANOVA - RT ROBUST MODEL ===\n")
print(anova(rt_model, type = 3))

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - RT MODEL ===\n")
print(isSingular(rt_model))

# Convergence
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(rt_model@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(rt_model))

# --- 3. Assumptions (plot) ---
print(check_model(rt_model))


###############################################################
# 5. RT - EFFECT SIZES (ROBUST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - RT ROBUST MODEL ===\n")
print(performance::r2(rt_model))

cat("\n=== PARTIAL ETA² - RT ROBUST MODEL ===\n")
print(effectsize::eta_squared(anova(rt_model, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 6. RT - POST-HOC (EMMEANS) - ROBUST MODEL
###############################################################

# Block main effect
cat("\n=== MAIN EFFECT - BLOCK (RT ROBUST) ===\n")
emm_block_RT_rob <- emmeans(rt_model, ~ Block_Factor,
                            tran = "log", type = "response")
print(emm_block_RT_rob)
print(pairs(emm_block_RT_rob, adjust = "BH"))

# Predictability × Previous-Error interaction
cat("\n=== INTERACTION: PREDICTABILITY × PREVIOUS-ERROR (RT ROBUST) ===\n")
emm_PxE_RT_rob <- emmeans(rt_model, ~ Predictability * Error_Prev,
                          tran = "log", type = "response")
print(emm_PxE_RT_rob)
cat("\n--- Predictability | Error_Prev ---\n")
print(pairs(emmeans(rt_model, ~ Predictability | Error_Prev,
                    tran = "log", type = "response"), adjust = "BH"))
cat("\n--- Error_Prev | Predictability ---\n")
print(pairs(emmeans(rt_model, ~ Error_Prev | Predictability,
                    tran = "log", type = "response"), adjust = "BH"))

# Predictability × Block interaction
cat("\n=== INTERACTION: PREDICTABILITY × BLOCK (RT ROBUST) ===\n")
emm_PxB_RT_rob <- emmeans(rt_model, ~ Predictability * Block_Factor,
                          tran = "log", type = "response")
print(emm_PxB_RT_rob)
cat("\n--- Predictability | Block ---\n")
print(pairs(emmeans(rt_model, ~ Predictability | Block_Factor,
                    tran = "log", type = "response"), adjust = "BH"))
cat("\n--- Block | Predictability ---\n")
print(pairs(emmeans(rt_model, ~ Block_Factor | Predictability,
                    tran = "log", type = "response"), adjust = "BH"))


###############################################################
#                                                             #
#                       Simplest MODEL                        #
#                                                             #
###############################################################

###############################################################
# 7. RT - SIMPLEST MODEL: Predictability × Error × Block
###############################################################

cat("\n=== FITTING SIMPLEST MODEL RT: Predictability × Error × Block ===\n")

modelo_2_RT <- lmer(
  log_RT ~ Predictability * Error_Prev * Block_Factor + (1 | volunteer),
  data = df_RT, REML = TRUE
)

print(summary(modelo_2_RT))

cat("\n=== TYPE III ANOVA (Fixed Effects) ===\n")
print(anova(modelo_2_RT, type = 3))

check_model(modelo_2_RT)

# ========================================
# DIAGNOSTICS
# ========================================

# --- 1. Computational fit ---
cat("\n=== SINGULAR FIT CHECK - RT MODEL ===\n")
print(isSingular(modelo_2_RT))

# Convergence
cat("\n=== CONVERGENCE MESSAGES ===\n")
print(modelo_2_RT@optinfo$conv$lme4$messages)

# --- 2. Variance structure ---
cat("\n=== VARIANCE COMPONENTS ===\n")
print(VarCorr(modelo_2_RT))

# --- 3. Assumptions (plot) ---
print(check_model(modelo_2_RT))


###############################################################
# 8. RT - EFFECT SIZES (SIMPLEST MODEL)
###############################################################

cat("\n=== R² (marginal & conditional) - RT SIMPLEST MODEL ===\n")
print(performance::r2(modelo_2_RT))

cat("\n=== PARTIAL ETA² - RT SIMPLEST MODEL ===\n")
print(effectsize::eta_squared(anova(modelo_2_RT, type = 3),
                              partial = TRUE, ci = 0.95))


###############################################################
# 9. RT - POST-HOC (EMMEANS) - SIMPLEST MODEL
###############################################################
# Three-way interaction non-significant (p = 0.792);
# two significant two-way interactions decomposed below.

# Block main effect
cat("\n=== MAIN EFFECT - BLOCK (RT) ===\n")
emm_block_RT <- emmeans(modelo_2_RT, ~ Block_Factor,
                        tran = "log", type = "response")
print(emm_block_RT)
print(pairs(emm_block_RT, adjust = "BH"))

# Predictability main effect
cat("\n=== MAIN EFFECT - PREDICTABILITY (RT) ===\n")
emm_predictability_RT <- emmeans(modelo_2_RT, ~ Predictability,
                        tran = "log", type = "response")
print(emm_predictability_RT)
print(pairs(emm_predictability_RT, adjust = "BH"))

# Predictability × Previous-Error interaction (p = 0.012)
cat("\n=== INTERACTION: PREDICTABILITY × PREVIOUS-ERROR (RT) ===\n")
emm_PxE_RT <- emmeans(modelo_2_RT, ~ Predictability * Error_Prev,
                      tran = "log", type = "response")
print(emm_PxE_RT)
cat("\n--- Predictability | Error_Prev ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Predictability | Error_Prev,
                    tran = "log", type = "response"), adjust = "BH"))
cat("\n--- Error_Prev | Predictability ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Error_Prev | Predictability,
                    tran = "log", type = "response"), adjust = "BH"))

# Predictability × Block interaction (p = 0.043)
cat("\n=== INTERACTION: PREDICTABILITY × BLOCK (RT) ===\n")
emm_PxB_RT <- emmeans(modelo_2_RT, ~ Predictability * Block_Factor,
                      tran = "log", type = "response")
print(emm_PxB_RT)
cat("\n--- Predictability | Block ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Predictability | Block_Factor,
                    tran = "log", type = "response"), adjust = "BH"))
cat("\n--- Block | Predictability ---\n")
print(pairs(emmeans(modelo_2_RT, ~ Block_Factor | Predictability,
                    tran = "log", type = "response"), adjust = "BH"))


###############################################################
# 10. RT - VISUALIZATION (SIMPLEST MODEL)
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
  labs(x = "Previous random transition result",
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

# Save fig
# Salva em PNG 900 dpi
ggsave("plot_RT_PxE.png", plot = p_RT_PxE,
       width = 7, height = 5, units = "in", dpi = 600)

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

# --- Plot 3: Triple interaction (exploratory) ---
p_RT <- emmip(modelo_2_RT,
              Predictability ~ Error_Prev | Block_Factor,
              CIs = FALSE, tran = "log", type = "response", plotit = TRUE)

p_RT <- p_RT +
  scale_color_manual(values = c("Predictable"   = "grey60",
                                "Unpredictable" = "black")) +
  facet_wrap(~ Block_Factor,
             labeller = labeller(Block_Factor = function(x) paste("Block:", x))) +
  labs(x = "Random transition result",
       y = "EMM of Response Time (ms)") +
  theme(
    axis.title        = element_text(size = 14),
    axis.text         = element_text(size = 8),
    strip.text        = element_text(size = 12),
    legend.title      = element_text(size = 10),
    legend.text       = element_text(size = 8),
    legend.position   = c(0.90, 0.98),
    legend.background = element_rect(fill = "white", color = "black"),
    legend.key        = element_rect(fill = "white")
  )

print(p_RT)

ggsave(
  filename = "RT_simple.pdf",
  plot = p_RT,
  width = 180,
  height = 100,
  units = "mm",
  device = cairo_pdf
)

###############################################################
#                                                             #
#                  AGGREGATED RM-ANOVA                        #
#                                                             #
###############################################################

###############################################################
# 11. RT - AGGREGATED ANALYSIS BY PARTICIPANT × CONDITION
###############################################################

# Per-participant cell means + repeated-measures ANOVA
# (Greenhouse-Geisser correction; partial eta squared as effect size).

cat("\n=== AGGREGATED RM-ANOVA - RT ===\n")

cell_dat_RT <- df_RT %>%
  group_by(volunteer, Predictability, Error_Prev, Block_Factor) %>%
  summarise(mean_log_y = mean(log_RT), n = n(), .groups = "drop")

cat("Cells:", nrow(cell_dat_RT),
    "| Participants:", n_distinct(cell_dat_RT$volunteer), "\n")

rt_rm <- anova_test(
  data        = cell_dat_RT,
  dv          = mean_log_y,
  wid         = volunteer,
  within      = c(Predictability, Error_Prev, Block_Factor),
  effect.size = "pes"
)

cat("\n=== RM-ANOVA TABLE (Greenhouse-Geisser) - RT ===\n")
print(get_anova_table(rt_rm, correction = "GG"))


###############################################################
# 12. RT - COMPARATIVE RESULTS TABLE
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

tab_robust   <- extract_lmer(rt_model,     "Robust")
tab_simplest <- extract_lmer(modelo_2_RT,  "SIMPLEST")
tab_rm       <- extract_rm(rt_rm,          "RM")

comparison_RT <- tab_robust %>%
  full_join(tab_simplest, by = "Term") %>%
  full_join(tab_rm,       by = "Term")

cat("\n=== COMPARATIVE RESULTS TABLE - RT ===\n")
print(as.data.frame(comparison_RT), row.names = FALSE)

# write.csv(comparison_RT, "comparison_RT.csv", row.names = FALSE)
