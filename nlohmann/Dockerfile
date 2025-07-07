FROM debian:12

WORKDIR /app

RUN apt -y update && apt -y upgrade && apt -y install git cmake g++

RUN git clone https://github.com/nlohmann/json

WORKDIR /app/json

RUN git pull origin develop \
 && git checkout d33ecd3f3bd11e30aa8bbabb00e0a9cd3f2456d8 \
 && mkdir build \
 && cd build \
 && cmake .. \
 && make "-j$(nproc)"

WORKDIR /app

COPY harness.cpp .

RUN g++ -g -O0 -static -I/app/json/build -I/app/json/include harness.cpp -o harness

ENTRYPOINT ["/app/harness"]

CMD ["/app/harness"]
