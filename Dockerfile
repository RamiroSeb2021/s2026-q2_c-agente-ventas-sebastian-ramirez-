FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md .python-version ./
RUN uv sync --frozen --no-dev

COPY app.py ./
COPY src ./src
COPY scripts ./scripts

EXPOSE 8501

CMD ["uv", "run", "--frozen", "--no-dev", "streamlit", "run", "app.py", "--server.address=0.0.0.0"]
