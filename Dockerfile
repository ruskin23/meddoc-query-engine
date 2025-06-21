# Start from the same Python version you're using locally
FROM python:3.12.3-slim

# Environment settings: avoid writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv package manager
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Create a virtual environment and install dependencies from pyproject.toml
RUN uv venv && uv pip install .

# Now copy the rest of your code
COPY . .

# Command to run the FastAPI app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
