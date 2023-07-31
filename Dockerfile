# Set the base image
FROM python:3.8-alpine

# Set the working directory
WORKDIR /.

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements.txt file to the working directory
COPY ./requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project to the working directory
COPY ./telegram .
COPY ./fastapi_app/vpnworks ./fastapi_app/vpnworks
