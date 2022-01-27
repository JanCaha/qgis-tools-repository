##Raster comparison=group
##calculatemapcurvesvemeasure=name
##Calculate mapcurves and vmeasure=display_name
##in_raster_1=raster
##in_raster_2=raster
##mc_value=output number
##vm_value=output number
##vm_homogeneity=output number
##vm_completeness=output number
##pass_filenames
library(sabre)
library(terra)

raster1 <- rast(in_raster_1)
raster2 <- rast(in_raster_2)

mc <- mapcurves_calc(x = raster1, y = raster2)
>mc
mc_value <- mc$gof

vm <- vmeasure_calc(x = raster1, y = raster2)
>vm

vm_value <- vm_value$v_measure
vm_homogeneity <- vm_value$homogeneity
vm_completeness <- vm_value$completeness
