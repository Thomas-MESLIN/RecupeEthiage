library("ggplot2")
library("dlstats")

x <- cran_stats(c("HydroPortailStats"))

if (!is.null(x)) {
  print(head(x))
  ggplot(x, aes(end, downloads, group=package, color=package)) +
    geom_line() + 
    geom_point() +
    scale_y_log10()
}

