library(lme4)
library(dplyr)
library(emmeans)
emm_options(pbkrtest.limit = Inf)
emm_options(lmerTest.limit = Inf)
library(sjPlot)
library(ggplot2)

# Import data
file_path <- '~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18'
file_name <- "df_gklab_analysis_20251118_2exclusions.csv"
full_path <- file.path(file_path, file_name)

# Creating DF
df <- read.csv(full_path, header = TRUE, stringsAsFactors = FALSE)

# Droping rows with NaN
df <- subset(df, !is.na(relMean_MEPpp_FDI) & !is.na(context))

# Removing invalid MEPs rows
df <- df %>% filter(!block_info %in% c(1, 3, 5))

# Converting to categorical factors
df$context <- as.factor(df$context)

# Check normality
hist(df$relMean_MEPpp_FDI, breaks=30, main="FDI MEP Distribution")

# Check Q-Q plot
qqnorm(df$relMean_MEPpp_FDI, main = "Q-Q Plot of relMean_MEPpp_FDI")
qqline(df$relMean_MEPpp_FDI, col = "red")

# Log transformation of FDI MEPs
df$relMean_MEPpp_FDI_log <- log(df$relMean_MEPpp_FDI)

# Check normality
hist(df$relMean_MEPpp_FDI_log, breaks=30, main="Log FDI MEP Distribution")

# Check Q-Q plot
qqnorm(df$relMean_MEPpp_FDI_log, main = "Q-Q Plot of Log relMean_MEPpp_FDI")
qqline(df$relMean_MEPpp_FDI_log, col = "red")

# Model
df.model = lmer(relMean_MEPpp_FDI_log ~ context + (1|ID_info), data=df, REML = FALSE)

# Print
summary(df.model)

### Check residual normality

# Extract residuals
res <- residuals(df.model)

# Histogram
hist(res, breaks = 30, main = "Residuals Histogram", xlab = "Residuals")

# Q-Q plot (normality check)
qqnorm(res)
qqline(res)

### Check linearity
plot(df$context, res, main="Residuals by Context")

### Check Homoscedasticity (Variance Equality)
plot(fitted(df.model), res, main = "Residuals vs Fitted", xlab = "Fitted values", ylab = "Residuals")
abline(h = 0, lty = 2)

### Check Normality and variance for random effects
ranef_df <- ranef(df.model)$ID_info
hist(ranef_df[,1], breaks=20, main="Random Intercepts Distribution", xlab="Intercepts")
qqnorm(ranef_df[,1])
qqline(ranef_df[,1])

# Comparing models
# Full model
model_full <- lmer(relMean_MEPpp_FDI_log ~ context + (1 | ID_info),
                   data = df, REML = FALSE)

# Reduced model (without last_was_error)
model_reduced <- lmer(relMean_MEPpp_FDI_log ~ 1 + (1 | ID_info),
                      data = df, REML = FALSE)

anova(model_reduced, model_full)