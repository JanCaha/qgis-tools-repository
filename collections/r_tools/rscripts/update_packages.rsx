##Update R packages=name
##R management=group
##dont_load_any_packages
##force_uninstall=boolean false

unloadNamespace("remotes")
install.packages("remotes")

library(remotes)

packages <- utils::installed.packages()
packages <- packages[-which(packages[,4] %in% c("base", "recommended")), ]
packages <- packages[-which(packages == "remotes"), ]

>packages

packages_to_update <- old.packages(instPkgs = packages)

if (!is.null(nrow(packages_to_update))) {
  packages_to_update <- packages_to_update[, "Package"]
  
  for (package in packages_to_update){
    unloadNamespace(package)
  }
  
  if (force_uninstall) {
    remove.packages(packages_to_update)
  }
  
  >remotes::update_packages(packages_to_update, upgrade = "always", force = TRUE)
}