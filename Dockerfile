# Use a specific version of Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the app files
COPY app .

# Copy entrypoint.sh script
COPY entrypoint.sh .

# Make sure entrypoint.sh is executable
RUN chmod +x entrypoint.sh

# Use entrypoint.sh as the entry point
ENTRYPOINT ["./entrypoint.sh"]