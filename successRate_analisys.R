if (!require(tidyverse)) install.packages("tidyverse")
if (!require(rstatix))   install.packages("rstatix")
if (!require(ggplot2))   install.packages("ggplot2")
if (!require(ggpubr))    install.packages("ggpubr")

library(tidyverse)
library(rstatix)
library(ggplot2)
library(ggpubr)

# =======================
# Data import and reshape
# =======================

data <- read_csv("~/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2026-01-12/success_rate_blocks.csv")

# Create a volunteer ID (one per row) BEFORE pivoting
data_long <- data %>%
  mutate(Volunteer = factor(row_number())) %>%
  pivot_longer(
    cols = -Volunteer,
    names_to  = "Block",
    values_to = "SuccessRate"
  ) %>%
  mutate(Block = factor(as.integer(as.numeric(Block))))

# =======================
# Statistical tests
# =======================

kruskal_test(SuccessRate ~ Block, data = data_long)
kruskal_effsize(data_long, SuccessRate ~ Block)

dunn_results <- data_long %>%
  dunn_test(SuccessRate ~ Block, p.adjust.method = "BH") %>%
  add_y_position(fun = "max")

# =======================
# Reusable theme with bigger fonts
# =======================

big_theme <- theme_pubr() +
  theme(
    axis.title = element_text(size = 20),
    axis.text  = element_text(size = 16),
    legend.title = element_text(size = 16),
    legend.text  = element_text(size = 14)
  )

# =======================
# Plot without significance
# =======================

p <- ggplot(data_long, aes(Block, SuccessRate)) +
  geom_boxplot(outlier.shape = NA) +
  # Lines connecting the same volunteer across blocks
  geom_line(aes(group = Volunteer),
            alpha = 0.3, color = "grey40") +
  geom_jitter(width = 0, size = 2, alpha = 0.7) +   # width = 0 to stay aligned with lines
  coord_cartesian(ylim = c(0.3, 1)) +
  big_theme +
  labs(y = "Success Rate", x = "Block")

print(p)

ggsave(
  "sucessRate_plot.png",
  plot = p,
  width = 10,
  height = 6,
  dpi = 300
)

# =======================
# Plot with significance
# =======================

dunn_sig <- dunn_results %>%
  filter(p.adj <= 0.05) %>%
  add_y_position(fun = "max", step.increase = 0.3)

p_sig <- ggplot(data_long, aes(Block, SuccessRate)) +
  geom_boxplot(outlier.shape = NA) +
  geom_line(aes(group = Volunteer),
            alpha = 0.3, color = "grey40") +
  geom_point(size = 2, alpha = 0.7) +                # aligned with the lines
  stat_pvalue_manual(
    dunn_sig,
    label      = "p.adj.signif",
    tip.length = 0.01,
    size       = 6                                   # bigger significance labels
  ) +
  coord_cartesian(ylim = c(0.3, 1.02)) +
  big_theme +
  labs(y = "Success Rate", x = "Block")

print(p_sig)

# ggsave(
#   "sucessRate_plot_significance.png",
#   plot = p_sig,
#   width = 10,
#   height = 6,
#   dpi = 300
# )
