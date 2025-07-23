FROM node:20-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy frontend files
COPY . .

# Install dependencies if package.json exists
RUN if [ -f package.json ]; then npm install; fi

# Expose port
EXPOSE 8080

# This replaces the startCommand from render.yaml
CMD ["npx", "serve", "-s", "/app", "-l", "8080"]

