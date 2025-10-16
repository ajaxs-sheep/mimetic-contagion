#!/bin/bash
# Larger 6-node graph scenario
# Demonstrates how complexity increases with more actors

python run.py --nodes Alice Betty Charlie David Eve Frank \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 123 \
              --rationality 0.5
