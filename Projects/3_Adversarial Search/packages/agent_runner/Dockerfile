FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/opt/arena/packages/isolation_engine:/opt/arena/packages/agent_runner
RUN useradd --create-home --uid 10001 arena
WORKDIR /opt/arena
COPY packages/isolation_engine packages/isolation_engine
COPY packages/agent_runner packages/agent_runner
USER arena
ENTRYPOINT []
