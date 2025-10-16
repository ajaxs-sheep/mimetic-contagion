#!/bin/bash
# High rationality scenario (optimal scapegoating)
# Actors always choose moves that balance the most triangles
# Results in fastest convergence to scapegoat state

python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 1.0
