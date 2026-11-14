FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

FROM nginx:alpine

# 🔒 Add these two lines here to upgrade Alpine base packages
RUN apk upgrade --no-cache

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80


# FROM node:22-alpine AS build

# WORKDIR /app

# COPY package*.json ./
# RUN npm ci

# COPY . .

# ARG VITE_API_URL=""
# ENV VITE_API_URL=${VITE_API_URL}

# RUN npm run build

# FROM nginx:alpine

# COPY nginx.conf /etc/nginx/conf.d/default.conf
# COPY --from=build /app/dist /usr/share/nginx/html

# EXPOSE 80
