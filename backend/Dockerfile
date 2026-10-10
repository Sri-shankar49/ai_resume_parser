
# FROM python:3.11-slim

# WORKDIR /app

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]



# FROM python:3.11-slim

# WORKDIR /app

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# COPY requirements.txt .

# RUN python -m ensurepip --upgrade \
#     && python -m pip install --no-cache-dir --upgrade pip \
#     && python -m pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]







FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN echo "AI_RESUME_PARSER_BACKEND_DOCKERFILE" 

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# Copy uv dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv, not pip
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# Start FastAPI
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
