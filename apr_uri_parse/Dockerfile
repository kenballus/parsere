FROM debian:12

WORKDIR /app

RUN apt -y update && apt -y upgrade && apt -y install git autoconf make libtool libtool-bin libexpat1-dev python3

RUN git clone https://github.com/apache/apr/

WORKDIR /app/apr

RUN git pull origin trunk \
 && git checkout 5a6d5173c8b88767616e80ab33a711c4e0543e04 \
 && ./buildconf \
 && ./configure \
 && make "-j$(nproc)"

WORKDIR /app

COPY harness.c .

RUN gcc -g -O0 -static -I/app/apr/include harness.c /app/apr/.libs/libapr-2.a -o harness

ENTRYPOINT ["/app/harness"]

CMD ["/app/harness"]
