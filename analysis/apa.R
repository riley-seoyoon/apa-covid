library(ggplot2)
library(dplyr)
library(ggridges)
library(RColorBrewer)
library(plotly)
library(tidyverse)

# temp = list.files("E:/Documents/APA/res_HepG2", pattern="*ratios.csv", full.names = T)
temp = list.files("/Users/seoyoonpark/Documents/APA/A549_apa_csv", pattern="*.csv", full.names = T)
temp
apa_files = lapply(temp, read.csv)
apa_df <- do.call(rbind.data.frame, apa_files)


apa_df$alias <- gsub("^.*/(.*).csv", "\\1", temp)

apa_df$condition <- gsub("(\\w{1,2}).\\d*", "\\1", apa_df$alias)

View(apa_df)

ggplot(apa_df) + 
  geom_density_ridges(aes(x = apa_pos, y = transcript, fill = condition), alpha = 0.5) +
  xlab("APA Location density") +
  ylab("Samples") +
  theme(legend.position = "none")

# Load required libraries
library(ggplot2)
library(reshape2)

View(apa_df)

apa_summary <- apa_df %>%
  group_by(alias) %>%
  summarize(apa_events = sum(read_count),
            mean_ratio = mean(apa_ratio))

apa_summary$isoforms <- lapply(1:15, function(i) nrow(apa_files[[i]]))
apa_summary$condition <- gsub("(\\w{1,2}).\\d*", "\\1", apa_summary$alias)


# View summary dataframe
View(apa_summary)

library(ggplot2)

# Create bar plot

ggplot(apa_summary, aes(x = alias, y = apa_events)) +
  geom_col(aes(fill = condition), width = 0.7) +
  xlab("Sample") +
  ylab("Number of APA events") +
  ggtitle("APA Events per Sample") + coord_flip()

ggsave("apa_events_by_sample.png")


ggplot(apa_df) +
  geom_density_ridges(aes(x = apa_pos, y = alias, 
                           group = interaction(alias, strand), fill = strand), 
                      scale = 1.5, alpha = 0.5) +
  facet_grid(condition ~ ., scales = "free_y") +
  xlab("APA Genomic Location") +
  ylab("Samples")

ggsave("density_loc.png")