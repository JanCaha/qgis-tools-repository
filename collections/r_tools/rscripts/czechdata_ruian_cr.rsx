##Czech Data=group
##RUIAN Data=name
##layer=enum literal stat;kraje;okresy;orp;obce;katastralni uzemi;volebni okrsky
##result=output vector 
library(CzechData)
result<-load_RUIAN_state(layer=layer)
