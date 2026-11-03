FROM python:3.12-slim

RUN pip install --no-cache-dir uv==0.12.12

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "api.py"]