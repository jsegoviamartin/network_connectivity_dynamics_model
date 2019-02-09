### CONVERGENCE ###
# 1. Code to calculate mean entropy, standard error and 95%CIs
# 2. Script to plot entropy by connectivity dynamic by content bias (Fig 2, 3)
#
#José Segovia Martín (Universidad Autónoma de Barcelona)

ps <- read.csv("C:\\...\\data.csv")
ps <- subset(l, select=c("Generation", "Connectivity", "Content.bias", "Entropy_population"))              

data <- data.frame(ps$Generation, ps$Connectivity,ps$Entropy_population, ps$Content.bias)
names(data)[names(data) == 'ps.Generation'] <- 'Round'
names(data)[names(data) == 'ps.Connectivity'] <- 'Connectivity'
names(data)[names(data) == 'ps.Entropy_population'] <- 'Entropy_population'
names(data)[names(data) == 'ps.Content.bias'] <- 'Content_bias'
data <- subset(data,Content_bias==0 | Content_bias==0.2 | Content_bias==0.4 | Content_bias==0.6 | Content_bias==0.8 | Content_bias==1)

mytitle1 <- "Entropy by connectivity by content bias (pop.size=8)"
y <- data$Entropy_population
z <- data$Connectivity
g <- data$Round
Content_bias <- data$Content_bias
z = factor(z, levels = c("Low isolation", "High isolation"))
data <- data.frame(y,z,g,Content_bias)
library(dplyr)
library(ggplot2)
#library(tidyverse)
library(scales) 
data %>%
  group_by(g, z, Content_bias) %>%
  summarise(media = mean(y), 
            desvio = sd(y),                             #Mean
            error_est = desvio / sqrt(n()),             #Standard error of the mean 
            intervalo_sup = media + (2*error_est),      #Upper interval limit. 
            intervalo_inf = media - (2*error_est)) %>%  #Lower limit 95%.
  ggplot(aes(x = g, y = media, color = z)) +
  labs(title=mytitle1) +
  #geom_point() +                                        #Only one datapoint
  geom_line(aes(group = z), size=0.5) +                  #Links 
  geom_errorbar(aes(ymax = intervalo_sup,                
                    ymin = intervalo_inf),
                width=0.3) + 
  #theme_minimal() +
  labs(x = "", y = "Entropy (bits)", color = "Connectivity") +
  scale_color_manual(labels = c("Early", "Mid", "Late"), values = c("blue","green", "red")) +
  scale_x_continuous(breaks = seq(0,15, by=5)) +
  theme(legend.position="bottom", legend.text=element_text(size=12)) +
  theme(axis.text=element_text(size=14),
        axis.title=element_text(size=14))+
  #facet_grid(Content_bias~., labeller = label_both)
  facet_wrap(~Content_bias)



