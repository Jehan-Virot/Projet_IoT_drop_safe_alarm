
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} jehan \
    && useradd --uid ${USER_UID} \
               --gid ${USER_GID} \
               --create-home \
               --shell /bin/bash jehan

COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN chown jehan:jehan /workspace

USER jehan

EXPOSE 8000 8002

CMD ["python", "-m", "src.app"]
