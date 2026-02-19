#!/bin/bash
# Quick Miniconda installer for ApplyFlow

set -e

echo "🔧 Installing Miniconda..."

cd ~
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh

echo "✅ Miniconda installed"

# Initialize conda
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc

echo "🎉 Miniconda ready! Please close and reopen your terminal."
