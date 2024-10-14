#!/bin/bash

# Run the initialization script ; deprecated initialization
# python init-app.py

# Run Streamlit and make it respond properly to shutdown signals
exec streamlit run vidsage_ui.py --server.port=8501
