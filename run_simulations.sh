#!/bin/bash

# Array of controller types
controller_types=("fixed" "marl")

# Number of iterations for each controller type
iterations=20

# Loop through each controller type
for controller in "${controller_types[@]}"; do
    echo "Running simulations with controllerType: $controller"
    for ((i=1; i<=iterations; i++)); do
        echo "Execution #$i for controllerType: $controller"
        python3 -m src.main --controllerType "$controller"
        echo "Completed Execution #$i for controllerType: $controller"
        echo "---------------------------------------------"
    done
done
