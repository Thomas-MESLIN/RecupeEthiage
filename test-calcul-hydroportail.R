install.packages('HydroPortailStats')  # Install the package from CRAN
#devtools::install_github('benRenard/HydroPortailStats') # Install the development version from GitHub
library(HydroPortailStats) # Load the package

names(distInfo)
distInfo[['GEV']]

n=30 # sample size / taille de l'échantillon
dist='GEV' # chosen distribution / distribution
param=c(100,50,-0.2) # parameter vector / paramètres de la distribution
y<-Generate(dist=dist,par=param,n=n) # generate data / simulation des données
plot(y,type='b') 

h3=Hydro3_Estimation(y=y,dist=dist)

Hydro3_Plot(h3)


# Test distribution basse eaux
dist="GEV_min"
y<-Generate(dist=dist,par=c(1,0.5,0.5),n=n)
plot(y,type='b')
options=options_def 
options$invertT=TRUE
h3=Hydro3_Estimation(y=y,dist=dist,options=options)
Hydro3_Plot(h3)

# Note that only 'ML' estimation is available for distribution 'GEV_min_pos' / Notez que seule la méthode 'ML' est disponible pour la distribution 'GEV_min_pos'
h3=Hydro3_Estimation(y=y,dist="GEV_min_pos",Emeth="ML",Umeth="ML",options=options)
Hydro3_Plot(h3)

