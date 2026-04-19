#include <catch2/catch_all.hpp>
#include "../src/engine/HybridModelGenerator.hpp"
#include "../src/ast/Model.hpp"
#include "../src/engine/NetworkGenerator.hpp"
#include <fstream>
#include <iostream>

using namespace bng::engine;
using namespace bng::ast;

TEST_CASE("HybridModelGenerator tests", "[hybrid]") {
    SECTION("Empty model should throw due to missing definitions") {
        Model model;
        PopulationMap pmap;
        pmap.label = "map1";
        pmap.patternText = "A()";
        pmap.populationFunction = "pop_A";
        model.addPopulationMap(pmap);

        model.addMoleculeType(MoleculeType("A", {}));

        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;
        opts.prefix = "test_empty";
        opts.overwrite = true;

        REQUIRE_THROWS_AS(generator.generate("dummy_source.bngl", opts), std::runtime_error);
    }

    SECTION("Model with population map generates proper rules") {
        Model model;
        PopulationMap pmap;
        pmap.label = "map1";
        pmap.patternText = "A()";
        pmap.populationFunction = "pop_A";
        model.addPopulationMap(pmap);

        model.addCompartment(Compartment("C", 3, 1.0));
        model.addMoleculeType(MoleculeType("A", {}));
        model.addSeedSpecies(SeedSpecies("A()", Expression::number(100)));
        model.addReactionRule(ReactionRule("rule1", "r1", {"A()"}, {}, {Expression::number(1)}, {}, false));
        model.addObservable(Observable("obs1", "Molecules", {"A()"}));

        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;
        opts.prefix = "test_model";
        opts.overwrite = true;

        auto result = generator.generate("dummy_source.bngl", opts);

        REQUIRE(result.hybridModelName == "test_model_hpp");
        REQUIRE(result.nPopulationMaps == 1);
        REQUIRE(result.nMoleculeTypes == 2);
        REQUIRE(result.nSeedSpecies == 1);
        REQUIRE(result.nZeroPopulations == 0);
        REQUIRE(result.nRules >= 1);
    }

    SECTION("Rule expansion should correctly copy or specialize rules") {
        Model model;
        PopulationMap pmap;
        pmap.label = "map1";
        pmap.patternText = "A()";
        pmap.populationFunction = "pop_A";
        model.addPopulationMap(pmap);

        model.addMoleculeType(MoleculeType("A", {}));
        model.addMoleculeType(MoleculeType("B", {}));
        model.addSeedSpecies(SeedSpecies("A()", Expression::number(100)));
        model.addSeedSpecies(SeedSpecies("B()", Expression::number(10)));

        model.addReactionRule(ReactionRule("rule_B", "rB", {"B()"}, {}, {Expression::number(1)}, {}, false));
        model.addReactionRule(ReactionRule("rule_A", "rA", {"A()"}, {}, {Expression::number(1)}, {}, false));

        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;
        opts.prefix = "test_rules";
        opts.overwrite = true;
        opts.safe = false;

        auto result = generator.generate("dummy_source.bngl", opts);

        REQUIRE(result.nRules == 2);

        std::ifstream bngl("test_rules_hpp.bngl");
        std::string content((std::istreambuf_iterator<char>(bngl)), std::istreambuf_iterator<char>());

        REQUIRE(content.find("rule_B:") != std::string::npos);
        REQUIRE(content.find("rule_A:") != std::string::npos);
        REQUIRE(content.find("rule_A_pop:") != std::string::npos);
        REQUIRE(content.find("_map_pop_A:") != std::string::npos);
    }

    SECTION("Preconditions validation") {
        Model model;
        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;

        REQUIRE_THROWS_AS(generator.generate("dummy", opts), std::runtime_error);
    }

    SECTION("isIsomorphic replaces isomorphic population equivalents correctly") {
        Model model;
        PopulationMap pmap;
        pmap.label = "map1";
        pmap.patternText = "A(b!1).B(a!1)";
        pmap.populationFunction = "pop_AB";
        model.addPopulationMap(pmap);

        model.addMoleculeType(MoleculeType("A", {{"b"}}));
        model.addMoleculeType(MoleculeType("B", {{"a"}}));

        model.addSeedSpecies(SeedSpecies("B(a!1).A(b!1)", Expression::number(100)));
        model.addSeedSpecies(SeedSpecies("A(b)", Expression::number(50)));
        // Add a dummy reaction rule to bypass the throw
        model.addReactionRule(ReactionRule("rule1", "r1", {"A()"}, {}, {Expression::number(1)}, {}, false));

        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;
        opts.prefix = "test_isomorphic";
        opts.overwrite = true;

        auto result = generator.generate("dummy_source.bngl", opts);

        std::ifstream bngl("test_isomorphic_hpp.bngl");
        std::string content((std::istreambuf_iterator<char>(bngl)), std::istreambuf_iterator<char>());

        REQUIRE(content.find("pop_AB() 100") != std::string::npos);
        REQUIRE(content.find("A(b) 50") != std::string::npos);
        REQUIRE(content.find("B(a!1).A(b!1) 100") == std::string::npos);
    }

    SECTION("countMatches correctly counts matches in observable") {
        Model model;
        PopulationMap pmap;
        pmap.label = "map1";
        pmap.patternText = "A(b!1).B(a!1)"; // This pattern forms pop_AB
        pmap.populationFunction = "pop_AB";
        model.addPopulationMap(pmap);

        model.addMoleculeType(MoleculeType("A", {{"b"}}));
        model.addMoleculeType(MoleculeType("B", {{"a"}}));

        // Let's add observables matching parts
        model.addObservable(Observable("obs_A", "Molecules", {"A()"}));
        model.addObservable(Observable("obs_B", "Molecules", {"B()"}));

        // Seed species
        model.addSeedSpecies(SeedSpecies("A(b!1).B(a!1)", Expression::number(100)));
        model.addReactionRule(ReactionRule("rule1", "r1", {"A()"}, {}, {Expression::number(1)}, {}, false));

        GeneratedNetwork network;
        HybridModelGenerator generator(model, network);
        HybridModelGenerator::Options opts;
        opts.prefix = "test_matches";
        opts.overwrite = true;

        auto result = generator.generate("dummy_source.bngl", opts);

        std::ifstream bngl("test_matches_hpp.bngl");
        std::string content((std::istreambuf_iterator<char>(bngl)), std::istreambuf_iterator<char>());

        // obs_A and obs_B should both now include pop_AB() because A() and B() both match inside pop_AB()
        bool contains_A = content.find("obs_A A(),pop_AB()") != std::string::npos || content.find("obs_A Molecules A(),pop_AB()") != std::string::npos;
        REQUIRE(contains_A);
    }
}
