# Multi-stage Dockerfile for DhafnckMCP Server
# Target: Image size under 200MB with full functionality

# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Set build arguments
ARG PYTHONUNBUFFERED=1
ARG PYTHONDONTWRITEBYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv for faster dependency resolution
RUN pip install uv

# Copy dependency files and README (needed for package build)
COPY pyproject.toml uv.lock* README.md ./

# Copy source code
COPY src/ src/

# Copy agent library (needed for agent system)
COPY agent-library/ agent-library/

# Copy rule files (needed for runtime)
COPY 00_RULES/ ./00_RULES/

# Create virtual environment and install dependencies
RUN uv venv .venv
# Use uv sync which installs both dependencies AND the current package
RUN uv sync --frozen

# Stage 2: Runtime stage
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src:/app
ENV FASTMCP_LOG_LEVEL=INFO
ENV FASTMCP_ENABLE_RICH_TRACEBACKS=0
ENV DATA_STORAGE_MODE=internal

# Create non-root user for security
RUN groupadd -r dhafnck && useradd -r -g dhafnck -s /bin/false dhafnck

# Create directories
WORKDIR /app
RUN mkdir -p /data /data/rules /app/logs /app/rules && \
    chown -R dhafnck:dhafnck /app /data

# Copy Python environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/src /app/src
COPY --from=builder /app/README.md /app/
COPY --from=builder /app/pyproject.toml /app/

# Copy agent library from builder stage
COPY --from=builder /app/agent-library /app/agent-library

# Copy rule files to /app/rules (where rule management expects them)
COPY --from=builder /app/00_RULES /app/rules

# Create symbolic link from /data/rules to /app/rules for backward compatibility
RUN ln -sf /app/rules /data/rules

# Copy startup script from scripts directory
COPY scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set proper ownership for both app and data directories
RUN chown -R dhafnck:dhafnck /app /data

# Switch to non-root user
USER dhafnck

# Expose port
EXPOSE 8000

# Activate virtual environment by updating PATH (must be after USER directive)
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server; print('Health check passed')"

# Default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "fastmcp"] 