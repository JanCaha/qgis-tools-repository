##Raster comparison=group
##calculateconfusionmatrix=name
##Calculate confusion matrix=display_name
##raster_predicted=raster
##raster_true_reference=raster
##pass_filenames

library(terra)
library(forcats)
library(caret)

raster_to_factor <- function(filename){
  
  rast <- rast(filename)

  values <- values(rast)
  
  values <- as_factor(values)
}

list_of_factors <- list(raster_to_factor(raster_predicted), raster_to_factor(raster_true_reference))

list_of_factors <- fct_unify(list_of_factors, lvls_union(list_of_factors))

>confusionMatrix(list_of_factors[[1]], list_of_factors[[2]])
