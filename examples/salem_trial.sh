#!/bin/bash
# Classic 4-node "Salem witch trial" scenario
# Demonstrates basic scapegoating behavior with balanced rationality

python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 0.5
