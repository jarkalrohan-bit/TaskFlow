# Build stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
# FROM python:3.12-slim-bookworm

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1

# # Apply available Debian security updates
# RUN apt-get update && \
#     apt-get upgrade -y && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Install Python dependencies
# COPY requirements.txt .

# RUN python -m pip install --no-cache-dir -r requirements.txt && \
#     python -m pip install --no-cache-dir "setuptools>=78.1.1"

# # Copy backend application
# COPY . .

# # Run application as non-root
# RUN useradd --system --create-home --uid 10001 appuser && \
#     chown -R appuser:appuser /app

# USER 10001

# EXPOSE 5000

# CMD ["sh", "-c", "python wait_for_db.py && python init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - 'app:create_app()'"]





# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 5000

# CMD ["sh", "-c", "python init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - 'app:create_app()'"]



# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# # Patch Debian packages
# RUN apt-get update && \
#     apt-get upgrade -y --no-install-recommends && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 5000

# CMD ["sh", "-c", "python wait_for_db.py && python init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - 'app:create_app()'"]


# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1

# # Install security updates and remove package metadata
# RUN apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install -y --no-install-recommends ca-certificates && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Install application dependencies
# COPY requirements.txt .

# RUN python -m pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# # Copy application source
# COPY . .

# # Create non-root application user
# RUN useradd --system --create-home --uid 10001 appuser && \
#     chown -R appuser:appuser /app

# USER 10001

# EXPOSE 5000

# CMD ["sh", "-c", "python wait_for_db.py && python init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - 'app:create_app()'"]
