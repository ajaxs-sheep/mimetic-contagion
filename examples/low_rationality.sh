#!/bin/bash
# Low rationality scenario (chaotic/random behavior)
# Actors make random decisions without considering global impact
# May result in longer cascades or stuck states

python run.py --nodes Alice Betty Charlie David \
              --initial all-positive \
              --perturb Alice:Betty \
              --seed 42 \
              --rationality 0.0
