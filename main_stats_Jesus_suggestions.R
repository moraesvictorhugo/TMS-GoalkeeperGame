###############################################################
# LINEAR MIXED EFFECTS MODELS - COMPLEMENTARY ANALYSIS
###############################################################

###############################################################
# 1. PACKAGES (add these to the top of the script)
###############################################################

if (!require(dplyr))    install.packages("dplyr")
if (!require(lme4))     install.packages("lme4")
if (!require(lmerTest)) install.packages("lmerTest")
if (!require(rstatix)) install.packages("rstatix")

library(dplyr)
library(lme4)
library(lmerTest)
library(rstatix)

###############################################################
# 2. DATA LOADING AND PREPROCESSING
###############################################################

# Read raw data and build analysis-ready data frame
df <- read.csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18/df_gkg-tms_2.csv") %>%
  
  # Compute trial position within each block (per volunteer)
  # Used later as a covariate to control for within-block learning/fatigue
  group_by(volunteer, block_info) %>%
  mutate(trial_in_block = trial - min(trial) + 1) %>%
  ungroup() %>%
  
  mutate(
    # Map context codes to predictability condition
    Predictability = case_when(
      context %in% c(1, 10)     ~ "Unpredictable",
      context %in% c(0, 2, 20)  ~ "Predictable",
      TRUE ~ NA_character_
    ),
    # Set "Predictable" as reference level
    Predictability = factor(Predictability, levels = c("Predictable", "Unpredictable")),
    
    # Previous-trial error indicator; "No Error" as reference level
    Error_Prev = factor(ifelse(last_random_was_error == 1, "Error", "No Error"),
                        levels = c("No Error", "Error")),
    
    # Block as categorical factor (main model)
    Block_Factor = factor(block_info, levels = c(2, 4, 6)),
    
    # Convert reaction time from seconds to milliseconds
    RT_ms = response_time * 1000,
    
    # Numeric dummies required for uncorrelated random slopes (|| syntax in lmer)
    P_unpred = as.numeric(Predictability == "Unpredictable"),
    E_error  = as.numeric(Error_Prev == "Error"),
    B4       = as.numeric(block_info == 4),
    B6       = as.numeric(block_info == 6),
    
    # Standardized within-block trial index (improves model convergence)
    trial_in_block_z = as.numeric(scale(trial_in_block))
  ) %>%
  
  # Keep only relevant blocks and trials with a valid predictability label
  filter(block_info %in% c(2, 4, 6), !is.na(Predictability))

###############################################################
# 3. OUTCOME-SPECIFIC DATASETS
###############################################################

# One dataset per outcome; outcomes are log-transformed to handle skewness
# and stored as 'log_y' to keep model formulas consistent across analyses

# Reaction time
dat_rt  <- df %>% 
  filter(!is.na(RT_ms), RT_ms > 0) %>% 
  mutate(log_y = log(RT_ms))

# FDS motor-evoked potential (peak-to-peak)
dat_fds <- df %>% 
  filter(!is.na(MEPpp_FDS_µV), MEPpp_FDS_µV > 0) %>% 
  mutate(log_y = log(MEPpp_FDS_µV))

# FDI motor-evoked potential (peak-to-peak)
dat_fdi <- df %>% 
  filter(!is.na(MEPpp_FDI_µV), MEPpp_FDI_µV > 0) %>% 
  mutate(log_y = log(MEPpp_FDI_µV))

###############################################################
# 4. SENSIBILITY ANALYSIS BY OUTCOME
###############################################################

# Shared model formula:
# - Fixed effects: full 3-way interaction + within-block trial covariate
# - Random effects: by-volunteer intercept and uncorrelated random slopes
#   for Predictability, previous Error, Block (dummies B4/B6), and trial position

# Optimizer settings to help convergence of complex random-effects structures
ctrl <- lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))

# ---- Reaction time ----
rt_model <- lmer(
  log_y ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = dat_rt, REML = TRUE, control = ctrl
)
print(summary(rt_model))
print(anova(rt_model, type = 3))

# ---- FDS motor-evoked potential ----
fds_model <- lmer(
  log_y ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = dat_fds, REML = TRUE, control = ctrl
)
print(summary(fds_model))
print(anova(fds_model, type = 3))

# ---- FDI motor-evoked potential ----
fdi_model <- lmer(
  log_y ~ Predictability * Error_Prev * Block_Factor + trial_in_block_z +
    (1 + P_unpred + E_error + B4 + B6 + trial_in_block_z || volunteer),
  data = dat_fdi, REML = TRUE, control = ctrl
)
print(summary(fdi_model))
print(anova(fdi_model, type = 3))

###############################################################
# 5. AGGREGATED ANALYSIS BY PARTICIPANT × CONDITION
###############################################################

# To show that results do not depend solely on the large number of trials,
# we compute each participant's mean per condition cell and run a 
# repeated-measures ANOVA. Greenhouse-Geisser correction is applied for
# sphericity; partial eta squared reported as effect size.

# ---- Helper function ----
rm_anova_by_outcome <- function(data, outcome_label) {
  
  # Mean of log-outcome per participant × condition cell
  cell_dat <- data %>%
    group_by(volunteer, Predictability, Error_Prev, Block_Factor) %>%
    summarise(mean_log_y = mean(log_y), n = n(), .groups = "drop")
  
  cat("\n=====================================================\n")
  cat("Repeated-measures ANOVA -", outcome_label, "\n")
  cat("Cells:", nrow(cell_dat),
      "| Participants:", n_distinct(cell_dat$volunteer), "\n")
  cat("=====================================================\n")
  
  res <- anova_test(
    data = cell_dat,
    dv = mean_log_y,
    wid = volunteer,
    within = c(Predictability, Error_Prev, Block_Factor),
    effect.size = "pes"
  )
  
  print(get_anova_table(res, correction = "GG"))
  
  invisible(list(data = cell_dat, anova = res))
}

# ---- Run for each outcome ----
rt_rm  <- rm_anova_by_outcome(dat_rt,  "Reaction Time")
fds_rm <- rm_anova_by_outcome(dat_fds, "FDS MEP")
fdi_rm <- rm_anova_by_outcome(dat_fdi, "FDI MEP")

###############################################################
# 6. SENSITIVITY: BLOCK AS ORDERED (LINEAR & QUADRATIC TRENDS)
###############################################################

# Blocks 2, 4, 6 are ordered in time. Testing linear and quadratic
# contrasts clarifies whether effects evolve progressively across
# task exposure.

# ---- Create orthogonal polynomial contrasts for Block ----
dat_rt <- dat_rt %>% mutate(
  Block_linear    = case_when(block_info == 2 ~ -1,
                              block_info == 4 ~  0,
                              block_info == 6 ~  1),
  Block_quadratic = case_when(block_info == 2 ~  1,
                              block_info == 4 ~ -2,
                              block_info == 6 ~  1)
)

dat_fds <- dat_fds %>% mutate(
  Block_linear    = case_when(block_info == 2 ~ -1,
                              block_info == 4 ~  0,
                              block_info == 6 ~  1),
  Block_quadratic = case_when(block_info == 2 ~  1,
                              block_info == 4 ~ -2,
                              block_info == 6 ~  1)
)

dat_fdi <- dat_fdi %>% mutate(
  Block_linear    = case_when(block_info == 2 ~ -1,
                              block_info == 4 ~  0,
                              block_info == 6 ~  1),
  Block_quadratic = case_when(block_info == 2 ~  1,
                              block_info == 4 ~ -2,
                              block_info == 6 ~  1)
)

# =============================================================
# 6.1 Main ordered model (linear trend with full random structure)
# =============================================================

fit_ordered_main <- function(data, outcome_label, ctrl) {
  
  cat("\n=====================================================\n")
  cat("Ordered model (linear) -", outcome_label, "\n")
  cat("=====================================================\n")
  
  m_ord <- lmer(
    log_y ~ Predictability * Error_Prev * Block_linear + trial_in_block_z +
      (1 + P_unpred + E_error + Block_linear + trial_in_block_z || volunteer),
    data = data, REML = TRUE, control = ctrl
  )
  
  print(summary(m_ord))
  print(anova(m_ord, type = 3))
  
  invisible(m_ord)
}

rt_ord  <- fit_ordered_main(dat_rt,  "Reaction Time", ctrl)
fds_ord <- fit_ordered_main(dat_fds, "FDS MEP",       ctrl)
fdi_ord <- fit_ordered_main(dat_fdi, "FDI MEP",       ctrl)


# =============================================================
# 6.2 Polynomial model (linear + quadratic, random intercept only)
# =============================================================

fit_ordered_poly <- function(data, outcome_label) {
  
  cat("\n=====================================================\n")
  cat("Polynomial model (linear + quadratic) -", outcome_label, "\n")
  cat("=====================================================\n")
  
  m_poly <- lmer(
    log_y ~ Predictability * Error_Prev * (Block_linear + Block_quadratic) +
      (1 | volunteer),
    data = data, REML = TRUE
  )
  
  print(summary(m_poly))
  print(anova(m_poly, type = 3))
  
  invisible(m_poly)
}

rt_poly  <- fit_ordered_poly(dat_rt,  "Reaction Time")
fds_poly <- fit_ordered_poly(dat_fds, "FDS MEP")
fdi_poly <- fit_ordered_poly(dat_fdi, "FDI MEP")

