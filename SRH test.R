library(rcompanion)
library(dplyr)
library(FSA)
# read data, risk&reward data for example
data_all <- read.csv("data/df_rr.csv",header = TRUE, row.names = 1)

# Ensure type as factor
data_all <- data_all %>%
  mutate(across(c(risk, reward, phase), as.factor))

# phases
for (stage in c(1,2)){
  cat("\n====================\n")
  cat("Stage:", stage, "\n")
  
  data_10t <- data_all[data_all$phase == stage, ]
  data_10t_esc <- data_10t[data_10t$decision_corrected %in% c(1,3), ]
  
  # ----------------- full trial -----------------
  dv_list <- c("distance_under_threat", "duration_reward", "max_instance_speed2safezone",
               "speed_explore_25.100_mean")
  
  for (dv in dv_list) {
    cat("\n--------------------\n")
    cat("Dependent variable:", dv, "\n")
    
    df <- data_10t %>%
      select(all_of(c(dv, "risk", "reward"))) %>%
      na.omit()
    
    if (nrow(df) == 0) {
      cat("No data, skipping.\n")
      next
    }
    
    # Scheirer–Ray–Hare test
    formula <- as.formula(paste(dv, "~ risk * reward"))
    srh <- scheirerRayHare(formula, data = df)
    print(srh)
    
    # Dunn post-hoc：reward within each risk
    cat("\n--- Post-hoc Dunn tests (reward within each risk) ---\n")
    for (r in levels(df$risk)) {
      sub_df <- df[df$risk == r, ]
      if (length(unique(sub_df$reward)) >= 2) {
        dunn <- FSA::dunnTest(sub_df[[dv]], g = sub_df$reward, method = "holm")
        cat("\nRisk =", r, "\n")
        print(dunn)
      }
    }
  }
  
  # ----------------- flee trial -----------------
  dv_list <- c("latency_to_first_escape")
  
  for (dv in dv_list) {
    cat("\n--------------------\n")
    cat("Dependent variable:", dv, "\n")
    
    df <- data_10t_esc %>%
      select(all_of(c(dv, "risk", "reward"))) %>%
      na.omit()
    
    if (nrow(df) == 0) {
      cat("No data, skipping.\n")
      next
    }
    
    # Scheirer–Ray–Hare test
    formula <- as.formula(paste(dv, "~ risk * reward"))
    srh <- scheirerRayHare(formula, data = df)
    print(srh)
    
    # Dunn post-hoc：reward within each risk
    cat("\n--- Post-hoc Dunn tests (reward within each risk) ---\n")
    for (r in levels(df$risk)) {
      sub_df <- df[df$risk == r, ]
      if (length(unique(sub_df$reward)) >= 2) {
        dunn <- FSA::dunnTest(sub_df[[dv]], g = sub_df$reward, method = "holm")
        cat("\nRisk =", r, "\n")
        print(dunn)
      }
    }
  }
}
