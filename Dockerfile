FROM python:3.13-slim

# Graphviz draws the diagrams; the fonts are for their labels
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# show the startup message and request log as they happen
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# compose files are read from, and diagrams written to, the folder mounted here
WORKDIR /work
EXPOSE 8000

ENTRYPOINT ["compose-diagrams"]
CMD ["--web", "--host", "0.0.0.0", "--no-browser"]
