#include <catch2/catch_test_macros.hpp>
#include "../src/ast/Model.hpp"
#include "../src/engine/NetworkGenerator.hpp"
#include "../src/engine/HybridModelGenerator.hpp"

namespace bng::engine {
    class HybridModelGeneratorTest {
    public:
        static bool callIsIsomorphic(const HybridModelGenerator& generator, const std::string& pattern1, const std::string& pattern2) {
            return generator.isIsomorphic(pattern1, pattern2);
        }
    };
}

TEST_CASE("HybridModelGenerator isIsomorphic error handling", "[HybridModelGenerator]") {
    bng::ast::Model model;
    bng::engine::GeneratedNetwork network;
    bng::engine::HybridModelGenerator generator(model, network);

    // Test malformed strings that return false (due to parsing or catching exceptions)
    REQUIRE(bng::engine::HybridModelGeneratorTest::callIsIsomorphic(generator, "A(x~1, x~2)", "A()") == false);
    REQUIRE(bng::engine::HybridModelGeneratorTest::callIsIsomorphic(generator, "\x01", "A()") == false);
    REQUIRE(bng::engine::HybridModelGeneratorTest::callIsIsomorphic(generator, "!!InvalidBNGL!!", "A()") == false);
    REQUIRE(bng::engine::HybridModelGeneratorTest::callIsIsomorphic(generator, "A(x!1)) garbage", "A()") == false);
}
