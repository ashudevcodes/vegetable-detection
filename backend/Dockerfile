FROM golang:1.22 as builder

WORKDIR /app
COPY . .

# Force static build (removes glibc dependency)
RUN go mod init backend && go mod tidy && CGO_ENABLED=0 go build -o server

FROM scratch
COPY --from=builder /app/server /server

EXPOSE 8080
ENTRYPOINT ["/server"]
