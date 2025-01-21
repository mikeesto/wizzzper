# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install Python packages
RUN pip install --upgrade pip && \
  pip install Flask \
  fal_client \
  gunicorn \
  python-dotenv

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run Gunicorn when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:80", "--log-level=debug", "server:app"]