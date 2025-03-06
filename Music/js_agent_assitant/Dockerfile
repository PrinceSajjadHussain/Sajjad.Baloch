# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Ensure output is logged immediately
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install the required Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of your application code to the container
COPY . /app

# Expose the port that the app runs on
EXPOSE 5002

# Run the application
CMD ["python", "app.py"]
