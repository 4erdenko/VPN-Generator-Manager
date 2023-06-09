FROM python:3.8-alpine
# Set work directory
WORKDIR ./
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r ./requirements.txt
# Copy project to workdir
COPY . .

# Make start.sh executable
RUN chmod +x /start.sh

# Run start.sh when the container launches
CMD ["/start.sh"]
