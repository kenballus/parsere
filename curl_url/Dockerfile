FROM debian:12

WORKDIR /app

RUN apt -y update && apt -y upgrade && apt -y install git autoconf libtool make

RUN git clone https://github.com/curl/curl

WORKDIR /app/curl

RUN git pull origin master \
 && git checkout 1cdac95e2e1022c298c1e4e551c7e8b5bd8fd5df \
 && autoreconf -fi \
 && ./configure --without-ssl --without-zlib --without-brotli --without-zstd --without-default-ssl-backend --without-ca-bundle --without-ca-path --without-ca-fallback --without-ca-embed --without-libpsl --without-libgsasl --without-librtmp --without-winidn --without-apple-idn --without-libidn2 --without-nghttp2 --without-ngtcp2 --without-openssl-quic --without-nghttp3 --without-quiche --without-msh3 --without-libuv --without-zsh-functions-dir --without-fish-functions-dir --without-shared --disable-alt-svc --disable-headers-api --disable-docs CFLAGS="-g -O0" \
 && make "-j$(nproc)"

WORKDIR /app

COPY harness.c .

RUN gcc -g -O0 -static -I/app/curl/include harness.c /app/curl/lib/.libs/libcurl.a -o harness

ENTRYPOINT ["/app/harness"]

CMD ["/app/harness"]
