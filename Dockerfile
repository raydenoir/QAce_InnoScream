FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade pip && \
    pip install poetry==1.8.2

# Copy only requirements files first
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-dev

# Copy the rest of the application
COPY . .

WORKDIR /app/src/innoscream
CMD ["python", "bot.py"]