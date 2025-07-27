FROM python:3.12-alpine

WORKDIR /frontend

# Copy frontend files
COPY . .

EXPOSE 3000

# Serve static files with Python's built-in server
CMD ["python", "-m", "http.server", "3000"]
