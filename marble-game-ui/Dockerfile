# syntax=docker/dockerfile:1
FROM node:18-alpine

ARG STATIC_CONTENT_DIR=/static
ARG APP_DIR=/code
WORKDIR $APP_DIR

# install yarn v3
COPY .yarn $APP_DIR/.yarn
COPY .yarnrc.yml package.json yarn.lock $APP_DIR
RUN yarn set version stable

# install dependencies
RUN yarn install

# build
ARG BUILD_PATH=$STATIC_CONTENT_DIR
COPY . $APP_DIR
RUN yarn run build
