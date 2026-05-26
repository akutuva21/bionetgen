#include <catch2/catch_test_macros.hpp>
#include "../src/engine/NetworkGenerator.hpp"
#include "../src/ast/Model.hpp"
#include "../src/parser/PatternGraphBuilder.hpp"
#include "BNGLexer.h"
#include "BNGParser.h"
// Include implementation to exercise evaluateRateString in anonymous namespace.
#include "../src/engine/NetworkGenerator.cpp"

using namespace bng::engine;
using namespace bng::ast;

TEST_CASE("parseBooleanLike behaves correctly", "[NetworkGenerator]") {
    // positive cases
    REQUIRE(parseBooleanLike("1") == true);
    REQUIRE(parseBooleanLike("true") == true);
    REQUIRE(parseBooleanLike("yes") == true);
    REQUIRE(parseBooleanLike("on") == true);

    // case insensitivity
    REQUIRE(parseBooleanLike("TRUE") == true);
    REQUIRE(parseBooleanLike("YeS") == true);
    REQUIRE(parseBooleanLike("ON") == true);

    // negative cases
    REQUIRE(parseBooleanLike("0") == false);
    REQUIRE(parseBooleanLike("false") == false);
    REQUIRE(parseBooleanLike("no") == false);
    REQUIRE(parseBooleanLike("off") == false);

    // empty string and invalid
    REQUIRE(parseBooleanLike("") == false);
    REQUIRE(parseBooleanLike("asdf") == false);
    REQUIRE(parseBooleanLike("2") == false);
}

static SpeciesGraph makeSpeciesGraph(const std::string& patternText, Model& model) {
    antlr4::ANTLRInputStream input(patternText);
    BNGLexer lexer(&input);
    antlr4::CommonTokenStream tokens(&lexer);
    BNGParser parser(&tokens);
    auto* species = parser.species_def();
    auto graph = bng::parser::buildPatternGraph(species, model, false);
    return SpeciesGraph(std::move(graph));
}

TEST_CASE("withinStoichLimits handles empty limits", "[NetworkGenerator]") {
    Model model;
    model.addMoleculeType(MoleculeType("A", {}));
    SpeciesGraph graph = makeSpeciesGraph("A()", model);
    std::map<std::string, std::size_t> limits; // empty limits
    REQUIRE(withinStoichLimits(graph, limits) == true);
}

TEST_CASE("withinStoichLimits enforces molecule counts", "[NetworkGenerator]") {
    Model model;
    model.addMoleculeType(MoleculeType("A", {}));
    model.addMoleculeType(MoleculeType("B", {}));

    // A().B().A() implies 2 of A, 1 of B
    SpeciesGraph graph = makeSpeciesGraph("A().B().A()", model);

    SECTION("No limits applied") {
        std::map<std::string, std::size_t> limits;
        REQUIRE(withinStoichLimits(graph, limits) == true);
    }

    SECTION("Within limits for both") {
        std::map<std::string, std::size_t> limits = {{"A", 2}, {"B", 1}};
        REQUIRE(withinStoichLimits(graph, limits) == true);
    }

    SECTION("Above limit for A") {
        std::map<std::string, std::size_t> limits = {{"A", 1}, {"B", 1}};
        REQUIRE(withinStoichLimits(graph, limits) == false);
    }

    SECTION("Above limit for B") {
        std::map<std::string, std::size_t> limits = {{"A", 2}, {"B", 0}};
        REQUIRE(withinStoichLimits(graph, limits) == false);
    }

    SECTION("Limits have unrelated entries") {
        std::map<std::string, std::size_t> limits = {{"A", 2}, {"C", 0}};
        REQUIRE(withinStoichLimits(graph, limits) == true);
    }
}
