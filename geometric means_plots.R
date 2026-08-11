# =============================================================================
# MEP / RT plotting script
# Adapted from generic time-series teaching scripts (some variable names
# may look unusual because of that origin).
# Purpose: visualise per-participant cell means and group means (95% CI)
#          for FDI MEPs, FDS MEPs and response time.
# =============================================================================


# -----------------------------------------------------------------------------
# 1. Packages
# -----------------------------------------------------------------------------
library(dplyr)
library(ggplot2)
# library(patchwork)  # optional: only needed to combine the 3 figures in one panel


# -----------------------------------------------------------------------------
# 2. File paths
#    Output folder is kept here for reproducibility, but saving is disabled
#    further down (we only plot to screen for now).
# -----------------------------------------------------------------------------
out_dir   <- "analysis_outputs"
data_file <- "~/pCloudDrive/pCloud Sync/Projects/Manuscript_TMS-GKg/data/df_gkg-tms_2.csv"

# dir.create(out_dir, showWarnings = FALSE)  # uncomment only when saving figures


# -----------------------------------------------------------------------------
# 3. Plot style and theme
#    Generic visual settings (colours, sizes, alphas). Reusable across other
#    plots of the same type. Editing this block changes appearance only,
#    never the underlying statistics.
# -----------------------------------------------------------------------------
plot_style <- list(
  pred_cols = c(                       # colour mapping for predictability levels
    "Predictable"   = "#5558f6",
    "Unpredictable" = "#b68c62"
  ),
  country_line_alpha  = 0.18,          # transparency of per-participant lines
  country_line_width  = 0.45,          # width of per-participant lines
  country_point_alpha = 0.28,          # transparency of per-participant points
  country_point_size  = 1.3,           # size of per-participant points
  ci_ribbon_alpha     = 0.16,          # transparency of the 95% CI ribbon
  mean_line_width     = 1.2,           # width of the group-mean line
  mean_point_size     = 2.6,           # size of the group-mean points
  dpi                 = 300            # resolution used when saving
)

# Figure sizes (inches) used only when exporting to file
figure_size <- list(
  fdi = c(width = 9.0, height = 5.2),
  fds = c(width = 7.2, height = 5.0),
  rt  = c(width = 7.2, height = 5.0)
)

# Custom clean theme built on top of theme_classic()
theme_limpo <- function(base_size = 12) {
  theme_classic(base_size = base_size) +
    theme(
      plot.title       = element_text(face = "bold", size = base_size + 2),
      plot.subtitle    = element_text(size = base_size),
      axis.title       = element_text(face = "bold"),
      legend.position  = "top",
      legend.title     = element_blank(),
      strip.background = element_rect(fill = "grey95", color = "grey75"),
      strip.text       = element_text(face = "bold"),
      panel.grid.major.y = element_line(color = "grey90", linewidth = 0.25)
    )
}

# Helper that applies the shared colour/fill scales, x-axis breaks and theme
add_limpo_scales <- function(plot) {
  plot +
    scale_color_manual(values = plot_style$pred_cols) +
    scale_fill_manual(values  = plot_style$pred_cols) +
    scale_x_continuous(breaks = c(2, 4, 6)) +
    theme_limpo()
}

# -----------------------------------------------------------------------------
# 4. Saving helper (currently NOT called)
#    Exports a figure as both PNG and PDF into out_dir.
# -----------------------------------------------------------------------------
save_plot_pair <- function(plot, filename, size) {
  # High-resolution raster (PNG) for quick preview / submission
  ggsave(
    file.path(out_dir, paste0(filename, ".png")),
    plot,
    width  = size["width"],
    height = size["height"],
    units  = "in",
    dpi    = 900                       # 600 DPI: safer for line art + text
  )
  # Vector PDF with embedded fonts (best for final publication)
  ggsave(
    file.path(out_dir, paste0(filename, ".pdf")),
    plot,
    width  = size["width"],
    height = size["height"],
    units  = "in",
    device = cairo_pdf
  )
}

# -----------------------------------------------------------------------------
# 5. Aggregation functions
#    Collapse trial-by-trial data into per-participant / per-condition cells.
#    Geometric means are computed by averaging in log space and back-transforming
#    with exp(), which is appropriate for the right-skewed MEP / RT distributions.
# -----------------------------------------------------------------------------

# Per-participant geometric-mean cells for a given MEP column
make_mep_cells <- function(data, column) {
  data %>%
    filter(!is.na(.data[[column]]), .data[[column]] > 0) %>%
    group_by(volunteer, Block, Block_num, Predictability, Previous_outcome) %>%
    summarise(
      log_value = mean(log(.data[[column]]), na.rm = TRUE),
      value     = exp(log_value),
      trials    = n(),
      .groups   = "drop"
    )
}

# Per-participant geometric-mean cells for response time (ms)
make_rt_cells <- function(data) {
  data %>%
    filter(!is.na(RT_ms), RT_ms > 0) %>%
    group_by(volunteer, Block, Block_num, Predictability, Previous_outcome) %>%
    summarise(
      log_value = mean(log(RT_ms), na.rm = TRUE),
      value     = exp(log_value),
      trials    = n(),
      .groups   = "drop"
    )
}

# Group-level summary with a simple 95% CI (t-based) over participant cell means,
# keeping the Previous_outcome factor (used for the FDI figure).
ci_summary <- function(data, value_col) {
  data %>%
    group_by(Block, Block_num, Predictability, Previous_outcome) %>%
    summarise(
      mean    = mean(.data[[value_col]], na.rm = TRUE),
      se      = sd(.data[[value_col]], na.rm = TRUE) / sqrt(n()),
      ci      = qt(0.975, df = n() - 1) * se,
      lower   = mean - ci,
      upper   = mean + ci,
      n       = n(),
      .groups = "drop"
    )
}

# Collapse over Previous_outcome (compact figures for FDS and RT).
# Averaging is done in log space to stay consistent with the geometric mean.
average_over_previous_outcome <- function(cells) {
  cells %>%
    group_by(volunteer, Block, Block_num, Predictability) %>%
    summarise(value = exp(mean(log_value)), .groups = "drop")
}

# Group-level 95% CI summary without the Previous_outcome factor
ci_summary_no_previous_outcome <- function(cells) {
  cells %>%
    group_by(Block, Block_num, Predictability) %>%
    summarise(
      mean    = mean(value),
      se      = sd(value) / sqrt(n()),
      ci      = qt(0.975, df = n() - 1) * se,
      lower   = mean - ci,
      upper   = mean + ci,
      .groups = "drop"
    )
}

# -----------------------------------------------------------------------------
# 6. Study-specific data preparation
#    Read raw data and build the experimental factors:
#      - Predictability   (Predictable / Unpredictable) from 'context'
#      - Previous_outcome  (success / failure) from 'last_random_was_error'
#      - Block             (ordered TMS blocks 2, 4, 6)
#      - RT in milliseconds
# -----------------------------------------------------------------------------
df <- read.csv(data_file) %>%
  mutate(
    # Map context codes to predictability condition
    Predictability = case_when(
      context %in% c(1, 10)     ~ "Unpredictable",
      context %in% c(0, 2, 20)  ~ "Predictable",
      TRUE                      ~ NA_character_
    ),
    Predictability = factor(
      Predictability,
      levels = c("Predictable", "Unpredictable")
    ),

    # Outcome of the previous random trial
    Previous_outcome = ifelse(
      last_random_was_error == 1,
      "Previous failure",
      "Previous success"
    ),
    Previous_outcome = factor(
      Previous_outcome,
      levels = c("Previous success", "Previous failure")
    ),

    # Block as ordered factor + numeric version for the x-axis
    Block     = factor(block_info, levels = c(2, 4, 6)),
    Block_num = as.numeric(as.character(Block)),

    # Convert response time from seconds to milliseconds
    RT_ms = response_time * 1000
  ) %>%
  filter(block_info %in% c(2, 4, 6), !is.na(Predictability))


# -----------------------------------------------------------------------------
# 7. Build per-participant cells and group-level summaries
# -----------------------------------------------------------------------------

# Per-participant geometric-mean cells
fdi_cells <- make_mep_cells(df, "MEPpp_FDI_µV")
fds_cells <- make_mep_cells(df, "MEPpp_FDS_µV")
rt_cells  <- make_rt_cells(df)

# FDI: keep Previous_outcome (shown as facets)
fdi_sum <- ci_summary(fdi_cells, "value")

# FDS: collapse over Previous_outcome, then summarise
fds_cells_no_error_facet <- average_over_previous_outcome(fds_cells)
fds_sum <- ci_summary_no_previous_outcome(fds_cells_no_error_facet)

# RT: collapse over Previous_outcome, then summarise
rt_cells_no_error_facet <- average_over_previous_outcome(rt_cells)
rt_sum <- ci_summary_no_previous_outcome(rt_cells_no_error_facet)


# -----------------------------------------------------------------------------
# 8. Figures
#    Layered structure (generic, reusable):
#      (1) thin per-participant lines + points
#      (2) transparent 95% CI ribbon
#      (3) thick group-mean line + points
# -----------------------------------------------------------------------------

# --- Figure 1: FDI MEPs (faceted by Previous_outcome) ---
fig_fdi <- ggplot(fdi_cells, aes(Block_num, value, color = Predictability)) +
  # (1) per-participant trajectories
  geom_line(
    aes(group = interaction(volunteer, Predictability)),
    alpha     = plot_style$country_line_alpha,
    linewidth = plot_style$country_line_width
  ) +
  geom_point(
    alpha = plot_style$country_point_alpha,
    size  = plot_style$country_point_size
  ) +
  # (2) 95% CI ribbon
  geom_ribbon(
    data = fdi_sum,
    aes(x = Block_num, ymin = lower, ymax = upper,
        fill = Predictability, group = Predictability),
    inherit.aes = FALSE,
    alpha       = plot_style$ci_ribbon_alpha,
    color       = NA
  ) +
  # (3) group means
  geom_line(
    data = fdi_sum,
    aes(y = mean, group = Predictability),
    linewidth = plot_style$mean_line_width
  ) +
  geom_point(
    data = fdi_sum,
    aes(y = mean),
    size = plot_style$mean_point_size
  ) +
  facet_wrap(~ Previous_outcome, nrow = 1) +
  labs(
    title    = "FDI MEPs: predictability by previous outcome across ordered blocks",
    subtitle = "Thin lines are participant cell means; thick lines are group means with 95% CI",
    x        = "TMS block",
    y        = "FDI MEP amplitude (geometric mean, µV)"
  )
fig_fdi <- add_limpo_scales(fig_fdi)


# --- Figure 2: FDS MEPs (collapsed over Previous_outcome) ---
fig_fds <- ggplot(fds_cells_no_error_facet,
                  aes(Block_num, value, color = Predictability)) +
  # (1) per-participant trajectories
  geom_line(
    aes(group = interaction(volunteer, Predictability)),
    alpha     = plot_style$country_line_alpha,
    linewidth = plot_style$country_line_width
  ) +
  geom_point(
    alpha = plot_style$country_point_alpha,
    size  = plot_style$country_point_size
  ) +
  # (2) 95% CI ribbon
  geom_ribbon(
    data = fds_sum,
    aes(x = Block_num, ymin = lower, ymax = upper,
        fill = Predictability, group = Predictability),
    inherit.aes = FALSE,
    alpha       = plot_style$ci_ribbon_alpha,
    color       = NA
  ) +
  # (3) group means
  geom_line(
    data = fds_sum,
    aes(y = mean, group = Predictability),
    linewidth = plot_style$mean_line_width
  ) +
  geom_point(
    data = fds_sum,
    aes(y = mean),
    size = plot_style$mean_point_size
  ) +
  labs(
    title    = "FDS MEPs: monotonic increase and predictability effect",
    subtitle = "Averaged over previous outcome because the error effect was not robust",
    x        = "TMS block",
    y        = "FDS MEP amplitude (geometric mean, µV)"
  )
fig_fds <- add_limpo_scales(fig_fds)


# --- Figure 3: Response time (collapsed over Previous_outcome) ---
fig_rt <- ggplot(rt_cells_no_error_facet,
                 aes(Block_num, value, color = Predictability)) +
  # (1) per-participant trajectories
  geom_line(
    aes(group = interaction(volunteer, Predictability)),
    alpha     = plot_style$country_line_alpha,
    linewidth = plot_style$country_line_width
  ) +
  geom_point(
    alpha = plot_style$country_point_alpha,
    size  = plot_style$country_point_size
  ) +
  # (2) 95% CI ribbon
  geom_ribbon(
    data = rt_sum,
    aes(x = Block_num, ymin = lower, ymax = upper,
        fill = Predictability, group = Predictability),
    inherit.aes = FALSE,
    alpha       = plot_style$ci_ribbon_alpha,
    color       = NA
  ) +
  # (3) group means
  geom_line(
    data = rt_sum,
    aes(y = mean, group = Predictability),
    linewidth = plot_style$mean_line_width
  ) +
  geom_point(
    data = rt_sum,
    aes(y = mean),
    size = plot_style$mean_point_size
  ) +
  labs(
    title    = "Response time: ordered decrease across blocks",
    subtitle = "Averaged over previous outcome for a compact supplementary figure",
    x        = "TMS block",
    y        = "Response time (ms, geometric mean)"
  )
fig_rt <- add_limpo_scales(fig_rt)


# -----------------------------------------------------------------------------
# 9. Display figures on screen (no file saving)
#    Explicit print() is required when running the whole script via source(),
#    because ggplot objects are not auto-printed outside the interactive console.
# -----------------------------------------------------------------------------
print(fig_fdi)
print(fig_fds)
print(fig_rt)

# Optional: combine all three in a single panel (requires patchwork)
# print(fig_fdi / fig_fds / fig_rt)


# -----------------------------------------------------------------------------
# 10. Saving (disabled) — uncomment to export PNG + PDF into out_dir
# -----------------------------------------------------------------------------
save_plot_pair(fig_fdi, "figure_1_fdi_interaction",    figure_size$fdi)
save_plot_pair(fig_fds, "figure_2_fds_ordered_trend",  figure_size$fds)
save_plot_pair(fig_rt,  "figure_3_rt_ordered_trend",   figure_size$rt)
