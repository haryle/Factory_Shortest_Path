FROM python:3.10-slim as requirements-stage

# 
WORKDIR /tmp

RUN pip install poetry
COPY src/server/pyproject.toml src/server/poetry.lock* /tmp/

# 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# 
FROM python:3.10-slim

# 
WORKDIR /app

# 
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY src/server/server /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging_conf.yaml"]
