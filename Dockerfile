FROM python:3.11-alpine

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy project files
COPY . .

# Make start.sh executable and change ownership
RUN chmod +x ./start.sh && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Run start.sh when the container launches
CMD ["./start.sh"]
