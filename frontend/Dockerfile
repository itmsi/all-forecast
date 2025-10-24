# Frontend Dockerfile - Multi-stage build (Memory Optimized)
FROM node:18-alpine as build

# Accept build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Set working directory
WORKDIR /app

# Install dependencies untuk memory optimization
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies dengan memory optimization
RUN npm ci --only=production --no-audit --no-fund --maxsockets 1

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# Build production bundle dengan memory optimization
ENV NODE_OPTIONS="--max-old-space-size=2048"
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

