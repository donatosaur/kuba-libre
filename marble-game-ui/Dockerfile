# syntax=docker/dockerfile:1
FROM node:18-alpine

ARG STATIC_CONTENT_DIR=/static
ARG APP_DIR=/code

WORKDIR $APP_DIR

# install dependencies
COPY package.json $APP_DIR
COPY yarn.lock $APP_DIR
RUN yarn install

# build
COPY . $APP_DIR
RUN yarn build
RUN mv $APP_DIR/build $STATIC_CONTENT_DIR
