FROM node:20-alpine

WORKDIR /app

# Configure npm for better network resilience
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-timeout 600000

# Install dependencies
# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install dependencies with retry fallback
# Use --legacy-peer-deps to avoid peer dependency conflicts
# --no-audit speeds up installation
RUN npm install --legacy-peer-deps --no-audit || \
    (npm cache clean --force && npm install --legacy-peer-deps --no-audit)

# Copy source
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
