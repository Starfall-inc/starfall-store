FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends git

# Clone the repository
ARG REPO_URL=https://github.com/danish-mar/dreamkart.git
RUN git clone $REPO_URL .

# Set up the environment
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the .env file
COPY .env .

# Expose the port your Flask app will run on
EXPOSE 5909

# Command to run the Flask application with a script to check for updates
CMD ["/app/start.sh"]

# Create a script to run the Flask app and check for updates
RUN echo '#!/bin/bash' > start.sh && \
    echo 'while true; do' >> start.sh && \
    echo '  echo "Checking for updates..."' >> start.sh && \
    echo '  git pull origin' >> start.sh && \
    echo '  echo "Starting Flask server..."' >> start.sh && \
    echo '  flask run --host 0.0.0.0 --port=5909' >> start.sh && \
    echo '  echo "Flask server stopped. Waiting for restart..."' >> start.sh && \
    echo '  sleep 5 # Wait a bit before checking again on restart' >> start.sh && \
    echo 'done' >> start.sh && \
    chmod +x start.sh