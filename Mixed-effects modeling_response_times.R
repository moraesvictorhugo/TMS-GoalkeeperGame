library(lme4)

file_path <- '/home/victormoraes/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-08-27'
file_name <- "df_gklab_analysis_20250828.csv"
full_path <- file.path(file_path, file_name)

# Creating DF
df <- read.csv(full_path, header = TRUE, stringsAsFactors = FALSE)

# Droping rows with NaN
df <- subset(df, !is.na(response_time_info) & !is.na(context))

# Converting to categorical factors
df$context <- as.factor(df$context)
df$last_was_error <- as.factor(df$last_was_error)

# Check response time normality
hist(df$response_time_info, breaks=30, main="Response Time Distribution")

# Log transformation of response time
df$response_time_info_log <- log(df$response_time_info)

# Check log response time normality
hist(df$response_time_info_log, breaks=30, main="Log Response Time Distribution")

# Model
df.model = lmer(response_time_info_log ~ context + last_was_error + (1|ID_info), data=df, REML = FALSE)

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
plot(df$last_was_error, res, main="Residuals by Last Was Error")

### Check Homoscedasticity (Variance Equality)
plot(fitted(df.model), res, main = "Residuals vs Fitted", xlab = "Fitted values", ylab = "Residuals")
abline(h = 0, lty = 2)

### Check Normality and variance for random effects
ranef_df <- ranef(df.model)$ID_info
hist(ranef_df[,1], breaks=20, main="Random Intercepts Distribution", xlab="Intercepts")
qqnorm(ranef_df[,1])
qqline(ranef_df[,1])

# Ploting results -> developing!!
library(sjPlot)
library(emmeans)
library(ggplot2)

# To view the fixed effects
plot_model(df.model, type = "est", show.values = TRUE, value.offset = 0.3,
           title = "Fixed Effects Estimates (log response time)",
           axis.labels = rev(c("last_was_error", "context20", "context10", "context2", "context1")))

# Plot estimated marginal means (predicted averages)
emm_context <- emmeans(df.model, ~ context)
summary(emm_context)
plot(emm_context, comparisons = TRUE)

ggplot(df, aes(x = context, y = response_time_info_log, color = ID_info, group = ID_info)) +
  geom_line(alpha = 0.4) +
  stat_summary(fun = mean, geom = "point", size = 4, color = "black") +
  labs(title = "Observed log(RT) by Context and Participant",
       y = "log(Response Time)", x = "Context") +
  theme_minimal(base_size = 14)

# Testinf model without last_was_error effect
# Full model
model_full <- lmer(response_time_info_log ~ context + last_was_error + (1 | ID_info),
                   data = df, REML = FALSE)

# Reduced model (without last_was_error)
model_reduced <- lmer(response_time_info_log ~ context + (1 | ID_info),
                      data = df, REML = FALSE)

anova(model_reduced, model_full)








