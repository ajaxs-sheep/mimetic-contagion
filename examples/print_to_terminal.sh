#!/bin/bash
# Print output to terminal instead of files
# Useful for quick testing and demonstrations

python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 0.5 \
              --format chain \
              --no-files
