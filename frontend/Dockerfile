FROM node:20-alpine

WORKDIR /app

RUN npm install -g serve

COPY . .

EXPOSE 8080

CMD ["npx", "serve", "-s", "/app", "-l", "8080"]
