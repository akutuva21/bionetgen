#include <chrono>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <random>

int main() {
    constexpr size_t N = 10000;

    std::unordered_map<size_t, size_t> lastProcessedMap;
    std::vector<size_t> lastProcessedVec(N, static_cast<size_t>(-1)); // -1 representing untouched

    // Fill half of them
    for (size_t i = 0; i < N / 2; ++i) {
        lastProcessedMap[i * 2] = 1;
        lastProcessedVec[i * 2] = 1;
    }

    auto t1 = std::chrono::high_resolution_clock::now();
    size_t count1 = 0;
    for (int iter = 0; iter < 10000; ++iter) {
        for (size_t i = 0; i < N; ++i) {
            auto iterMap = lastProcessedMap.find(i);
            if (iterMap == lastProcessedMap.end() || iterMap->second < 2) {
                count1++;
            }
        }
    }
    auto t2 = std::chrono::high_resolution_clock::now();

    auto t3 = std::chrono::high_resolution_clock::now();
    size_t count2 = 0;
    for (int iter = 0; iter < 10000; ++iter) {
        for (size_t i = 0; i < N; ++i) {
            auto val = lastProcessedVec[i];
            if (val == static_cast<size_t>(-1) || val < 2) {
                count2++;
            }
        }
    }
    auto t4 = std::chrono::high_resolution_clock::now();

    std::cout << "Map time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms (count: " << count1 << ")\n";
    std::cout << "Vec time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t4 - t3).count() << "ms (count: " << count2 << ")\n";

    return 0;
}
