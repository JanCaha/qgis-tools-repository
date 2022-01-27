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

raster_predicted <- raster_to_factor(raster_predicted)
raster_true_reference <- raster_to_factor(raster_true_reference)

>confusionMatrix(raster_predicted, raster_true_reference)