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
df <- subset(df, !is.na(relMean_MEPpp_FDS) & !is.na(context))

# Removing invalid MEPs rows
df <- df %>% filter(!block_info %in% c(1, 3, 5))

# Converting to categorical factors
df$context <- as.factor(df$context)

# Check normality
hist(df$relMean_MEPpp_FDS, breaks=30, main="FDS MEP Distribution")

# Check Q-Q plot
qqnorm(df$relMean_MEPpp_FDS, main = "Q-Q Plot of relMean_MEPpp_FDS")
qqline(df$relMean_MEPpp_FDS, col = "red")

# Log transformation of FDS MEPs
df$relMean_MEPpp_FDS_log <- log(df$relMean_MEPpp_FDS)

# Check normality
hist(df$relMean_MEPpp_FDS_log, breaks=30, main="Log FDS MEP Distribution")

# Check Q-Q plot
qqnorm(df$relMean_MEPpp_FDS_log, main = "Q-Q Plot of Log relMean_MEPpp_FDS")
qqline(df$relMean_MEPpp_FDS_log, col = "red")

# Model
df.model = lmer(relMean_MEPpp_FDS_log ~ context + (1|ID_info), data=df, REML = FALSE)

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

# Ploting results -> developing!!

# To view the fixed effects
plot_model(df.model, type = "est", show.values = TRUE, value.offset = 0.3,
           title = "Fixed Effects Estimates (log FDS MEPs)",
           axis.labels = rev(c("context20", "context10", "context2", "context1")))

# Plot estimated marginal means (predicted averages)
emm_context <- emmeans(df.model, ~ context)
summary(emm_context)
plot(emm_context, comparisons = TRUE)

ggplot(df, aes(x = context, y = relMean_MEPpp_FDS_log, color = ID_info, group = ID_info)) +
  geom_line(alpha = 0.4) +
  stat_summary(fun = mean, geom = "point", size = 4, color = "black") +
  labs(title = "Observed log(RT) by Context and Participant",
       y = "log(Response Time)", x = "Context") +
  theme_minimal(base_size = 14)

# Testing model without last_was_error effect
# Full model
model_full <- lmer(relMean_MEPpp_FDS_log ~ context + (1 | ID_info),
                   data = df, REML = FALSE)

# Reduced model (without last_was_error)
model_reduced <- lmer(relMean_MEPpp_FDS_log ~ 1 + (1 | ID_info),
                      data = df, REML = FALSE)

anova(model_reduced, model_full)

