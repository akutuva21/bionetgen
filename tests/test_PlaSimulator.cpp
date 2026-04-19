#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

// Include the source file directly to test the anonymous namespace function
#include "../src/engine/PlaSimulator.cpp"

namespace bng::engine {

TEST_CASE("evaluateRateString error path", "[PlaSimulator]") {
    auto resolve = [](const std::string& s) {
        if (s == "valid_var") return 42.0;
        return 0.0;
    };

    // Valid float
    REQUIRE_THAT(evaluateRateString("1.23", resolve), Catch::Matchers::WithinRel(1.23));

    // Invalid float - triggers std::stod exception, falls back to resolve
    REQUIRE_THAT(evaluateRateString("invalid_float", resolve), Catch::Matchers::WithinRel(0.0));

    // Variable resolution
    REQUIRE_THAT(evaluateRateString("valid_var", resolve), Catch::Matchers::WithinRel(42.0));

    // Partial float - should fail std::stod length check and fall back to resolve
    REQUIRE_THAT(evaluateRateString("1.23abc", resolve), Catch::Matchers::WithinRel(0.0));
}

} // namespace bng::engine
