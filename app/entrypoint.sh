#!/bin/bash

# Run the initialization script ; deprecated initialization
# python init-app.py

# Start Flask in the background on port 5000
# gunicorn --bind 0.0.0.0:5000 add_video_active:app_getvid &

# Run Streamlit and make it respond properly to shutdown signals
exec streamlit run vidsage_ui.py --server.port=8501 &

# Run prefect server and deploy
prefect config set PREFECT_API_URL="http://localhost:4200/api"
prefect server start &
python ./utils/ingest_data.py
