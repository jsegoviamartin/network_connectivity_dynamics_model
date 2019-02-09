### ADAPTIVENESS ###
# 1. Script to get high quality variants and calculate variant frequency
# 2. Code to plot change in adaptiveness by round by content bias (Fig 4, 5)
#
#José Segovia Martín (Universidad Autónoma de Barcelona)

ps <- read.csv("C:\\...\\data.csv")
ps <- subset(ps, select=c("Generation", "Connectivity", "Content.bias", "Population.signals"))

data <- data.frame(ps$Generation, ps$Connectivity,ps$Population.signals, ps$Content.bias)
names(data)[names(data) == 'ps.Generation'] <- 'Round'
names(data)[names(data) == 'ps.Connectivity'] <- 'Connectivity'
names(data)[names(data) == 'ps.Population.signals'] <- 'Population_signals'
names(data)[names(data) == 'ps.Content.bias'] <- 'Content_bias'
data <- subset(data,Content_bias==0 | Content_bias==0.2 | Content_bias==0.4 | Content_bias==0.6 | Content_bias==0.8 | Content_bias==1)
write.csv(data,"data.csv")

data %>%
  mutate(Population_signals = gsub('\\[|\\]', '', Population_signals)) %>% 
  separate(Population_signals, into=paste0("V",1:8)) -> data           

mytitle1 <- "Change in adaptiveness by round"
y <- data$V1
z <- data$Connectivity
Round <- data$Round
x <- data$Content_bias
z = factor(z, levels = c("Early connectivity", "Mid connectivity", "Late connectivity"))
data <- data.frame(y,Round,z,x)
data %>%
  group_by(Round, z, x) %>%
  summarise(media = mean(y, na.rm = T)) %>%  
  arrange(Round, z, x) %>%
  mutate(Round_n = match(Round, unique({.}$Round)),
         Round_n_lag = Round_n - 1) %>%
  left_join(y={.}, c("Round_n_lag" = "Round_n", "z", "x")) %>%
  mutate(media_lag = ifelse(is.na(media.y),0,media.x-media.y)) %>%
  select(Round=Round.x, x, z, media=media.x, media_lag)->data


ggplot(data,aes(x = Round, y = media_lag/8, color = z)) +
  labs(title=mytitle1) +
  #geom_point() +                                        
  geom_line(aes(group = z), size=0.5) +                       
  #geom_errorbar(aes(ymax = intervalo_sup,               
  #ymin = intervalo_inf),
  #width=0.3) + 
  #theme_minimal() +
  labs(x = "Round", y = "???A", color = "Connectivity") +
  scale_color_manual(labels = c("Early", "Mid", "Late"), values = c("blue","green","red")) +
  scale_x_continuous(breaks = seq(1, 7, by = 1)) +
  theme(legend.position="bottom", legend.text=element_text(size=12)) +
  theme(axis.text=element_text(size=14),
        axis.title=element_text(size=14))+
  facet_wrap(~x)







