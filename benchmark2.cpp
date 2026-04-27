#include <iostream>
#include <chrono>
#include <string>
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, int> g_compartmentDimensions;

void setup() {
    g_compartmentDimensions["PM"] = 2;
    g_compartmentDimensions["NM"] = 2;
}

struct Pattern {
    std::string comp;
    std::string getCompartment() const { return comp; }
};

int main() {
    setup();

    std::vector<Pattern> reactantPatterns_(100);
    std::vector<Pattern> productPatterns_(100);

    for (int i = 0; i < 100; ++i) {
        reactantPatterns_[i].comp = "PM";
        productPatterns_[i].comp = "NM";
    }

    auto start = std::chrono::high_resolution_clock::now();

    long long dummy = 0;

    for (int iter = 0; iter < 1000000; ++iter) {
        for (std::size_t pi = 0; pi < reactantPatterns_.size() && pi < productPatterns_.size(); ++pi) {
            const auto& compR = reactantPatterns_[pi].getCompartment();
            const auto& compP = (pi < productPatterns_.size()) ? productPatterns_[pi].getCompartment() : std::string();
            if (compR.empty() || compP.empty() || compR == compP) continue;

            auto dimRIt = g_compartmentDimensions.find(compR);
            auto dimPIt = g_compartmentDimensions.find(compP);
            if (dimRIt == g_compartmentDimensions.end() || dimPIt == g_compartmentDimensions.end()) continue;
            if (dimRIt->second != dimPIt->second) continue; // must be same dimension

            dummy++;
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Baseline: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << " ms" << std::endl;
    std::cout << "Dummy: " << dummy << std::endl;

    start = std::chrono::high_resolution_clock::now();
    dummy = 0;

    for (int iter = 0; iter < 1000000; ++iter) {
        // OPTIMIZED VERSION
        auto endIt = g_compartmentDimensions.end();
        const std::string* lastCompR = nullptr;
        const std::string* lastCompP = nullptr;
        std::unordered_map<std::string, int>::iterator lastDimRIt = endIt;
        std::unordered_map<std::string, int>::iterator lastDimPIt = endIt;

        for (std::size_t pi = 0; pi < reactantPatterns_.size() && pi < productPatterns_.size(); ++pi) {
            const auto& compR = reactantPatterns_[pi].getCompartment();
            const auto& compP = (pi < productPatterns_.size()) ? productPatterns_[pi].getCompartment() : std::string();
            if (compR.empty() || compP.empty() || compR == compP) continue;

            auto dimRIt = endIt;
            if (lastCompR && *lastCompR == compR) {
                dimRIt = lastDimRIt;
            } else {
                dimRIt = g_compartmentDimensions.find(compR);
                lastCompR = &compR;
                lastDimRIt = dimRIt;
            }

            auto dimPIt = endIt;
            if (lastCompP && *lastCompP == compP) {
                dimPIt = lastDimPIt;
            } else {
                dimPIt = g_compartmentDimensions.find(compP);
                lastCompP = &compP;
                lastDimPIt = dimPIt;
            }

            if (dimRIt == endIt || dimPIt == endIt) continue;
            if (dimRIt->second != dimPIt->second) continue; // must be same dimension

            dummy++;
        }
    }

    end = std::chrono::high_resolution_clock::now();
    std::cout << "Optimized (cache string ptrs): " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << " ms" << std::endl;
    std::cout << "Dummy: " << dummy << std::endl;

    return 0;
}
