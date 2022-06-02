# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG APP_DIR=/app
ARG STATIC_CONTENT_DIR=/static
ENV FASTAPI_STATIC_CONTENT_DIR=/static

# copy static content
COPY --from=frontend ${STATIC_CONTENT_DIR} ${STATIC_CONTENT_DIR}

# copy shared libraries
COPY --from=shared /shared/marble-game /marble-game

# install dependencies
WORKDIR $APP_DIR
COPY requirements.txt $APP_DIR
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt
RUN python -m pip install --no-cache-dir /marble-game/
COPY . $APP_DIR

# run as non-privileged user
RUN useradd -m app
USER app
EXPOSE 3000

CMD ["python", "main.py"]
