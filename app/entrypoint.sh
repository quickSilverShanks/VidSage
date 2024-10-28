#!/bin/bash

# Run the initialization script ; deprecated initialization
# python init-app.py

# Start Flask in the background on port 5000
# gunicorn --bind 0.0.0.0:5000 add_video_active:app_getvid &

# Run prefect server and deploy
prefect config set PREFECT_API_URL="http://localhost:4200/api"
prefect server start &
# python ./utils/ingest_data.py &

# Wait for the Prefect server to start
echo "Waiting for Prefect server to start on localhost:4200..."
while ! echo > /dev/tcp/localhost/4200; do
    echo "Prefect server is not available yet, retrying in 5 seconds..."
    sleep 5
done

# Run Streamlit and make it respond properly to shutdown signals
exec streamlit run vidsage_ui.py --server.port=8501
