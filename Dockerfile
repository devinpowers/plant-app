# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Run the application
CMD [ "python", "src/main.py" ]
