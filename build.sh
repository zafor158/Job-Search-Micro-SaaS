# Vercel build configuration
# This file helps Vercel build the Python application correctly

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
