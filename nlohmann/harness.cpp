#include <iostream>
#include <nlohmann/json.hpp>

int main(void) {
    nlohmann::json data = nlohmann::json::parse(std::cin);
}
