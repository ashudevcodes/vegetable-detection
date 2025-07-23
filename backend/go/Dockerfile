FROM golang:1.22-alpine AS builder
WORKDIR /app

# RUN go mod download
COPY go.mod go.sum ./

COPY . .

RUN go build -o price-service cmd/main.go

FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/price-service .
EXPOSE 9000
CMD ["./price-service"]
