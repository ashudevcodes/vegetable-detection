FROM docker.io/library/nginx:alpine

WORKDIR /usr/share/nginx/html

COPY index.html ./
COPY main.js ./
COPY styles.css ./

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
