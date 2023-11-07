# Use an official Python 3.11 image as the base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy your application code into the container
COPY . /app
COPY .env /app/.env

RUN pip install --upgrade pip
# Install any dependencies (e.g., Django, if not already in your requirements.txt)
RUN pip install -r requirements.txt

# Navigate to the "bot" directory
WORKDIR /app/bot

# Specify the command to run your Python script (test.py)
CMD ["python", "test.py"]
