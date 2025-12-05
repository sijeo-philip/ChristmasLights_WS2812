#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p lib
gcc -fPIC -shared -O3 -o lib/libeffects.so -I csrc csrc/effects.c
