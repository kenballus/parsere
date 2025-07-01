FROM debian:12

WORKDIR /app

RUN apt -y update && apt -y upgrade && apt -y install git cmake

RUN git clone https://github.com/json-c/json-c

WORKDIR /app/json-c

RUN git pull origin master \
 && git checkout 7cee5237dc6c0831e3f9dc490394eaea44636861 \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make "-j$(nproc)"

WORKDIR /app

COPY harness.c .

RUN gcc -g -O0 -static -I/app/json-c/build -I/app/json-c harness.c /app/json-c/build/libjson-c.a -o harness

ENTRYPOINT ["/app/harness"]

CMD ["/app/harness"]
