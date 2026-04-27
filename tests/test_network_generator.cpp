#include <catch2/catch_all.hpp>
#include "../src/engine/NetworkGenerator.cpp"

using namespace bng::engine;

TEST_CASE("parseBooleanLike parses boolean-like strings correctly", "[NetworkGenerator]") {
    SECTION("True values") {
        REQUIRE(parseBooleanLike("1") == true);
        REQUIRE(parseBooleanLike("true") == true);
        REQUIRE(parseBooleanLike("yes") == true);
        REQUIRE(parseBooleanLike("on") == true);
    }
    SECTION("True values with different cases") {
        REQUIRE(parseBooleanLike("True") == true);
        REQUIRE(parseBooleanLike("TRUE") == true);
        REQUIRE(parseBooleanLike("Yes") == true);
        REQUIRE(parseBooleanLike("YES") == true);
        REQUIRE(parseBooleanLike("On") == true);
        REQUIRE(parseBooleanLike("ON") == true);
    }
    SECTION("True values with whitespace") {
        REQUIRE(parseBooleanLike(" 1 ") == true);
        REQUIRE(parseBooleanLike("  true  ") == true);
        REQUIRE(parseBooleanLike("\tyes\n") == true);
    }
    SECTION("True values with quotes") {
        REQUIRE(parseBooleanLike("\"1\"") == true);
        REQUIRE(parseBooleanLike("'true'") == true);
        REQUIRE(parseBooleanLike("\"yes\"") == true);
    }
    SECTION("False values") {
        REQUIRE(parseBooleanLike("0") == false);
        REQUIRE(parseBooleanLike("false") == false);
        REQUIRE(parseBooleanLike("no") == false);
        REQUIRE(parseBooleanLike("off") == false);
        REQUIRE(parseBooleanLike("") == false);
        REQUIRE(parseBooleanLike("random_string") == false);
    }
    SECTION("False values with quotes") {
        REQUIRE(parseBooleanLike("\"0\"") == false);
        REQUIRE(parseBooleanLike("'false'") == false);
        REQUIRE(parseBooleanLike("\"no\"") == false);
    }
}
