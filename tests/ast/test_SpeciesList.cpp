#include <catch2/catch_test_macros.hpp>
#include "ast/SpeciesList.hpp"
#include "ast/SpeciesGraph.hpp"
#include "core/BNGcore.hpp"

using namespace bng::ast;

TEST_CASE("SpeciesList functionality", "[ast][SpeciesList]") {
    BNGcore::PatternGraph pg;
    SpeciesGraph sg(pg);
    Species s1(sg);

    SECTION("checkIso disabled allows duplicate additions") {
        SpeciesList list;

        // Turn off isomorphism checking
        list.setCheckIso(false);
        REQUIRE(list.getCheckIso() == false);

        // Add the same species twice
        list.add(s1);
        list.add(s1);

        // Since checkIso is false, both should be added unconditionally
        // rather than deduped.
        REQUIRE(list.size() == 2);
    }

    SECTION("checkIso enabled prevents duplicate additions") {
        SpeciesList list;

        // Isomorphism checking should be true by default
        REQUIRE(list.getCheckIso() == true);

        // Add the same species twice
        list.add(s1);
        list.add(s1);

        // Since checkIso is true, the second addition should be deduped
        REQUIRE(list.size() == 1);
    }
}

TEST_CASE("SpeciesList preserves compartment-aware deduplication", "[ast][SpeciesList]") {
    BNGcore::EntityType moleculeType("M", BNGcore::ENTITY_NODE_TYPE, BNGcore::NULL_STATE_TYPE);
    BNGcore::EntityType componentType("site", BNGcore::COMPONENT_NODE_TYPE, BNGcore::NULL_STATE_TYPE);

    auto makeSpecies = [&](const std::string& moleculeCompartment) {
        BNGcore::PatternGraph graph;
        BNGcore::Node molecule(moleculeType);
        BNGcore::Node component(componentType);
        auto* moleculeNode = graph.add_node(molecule);
        auto* componentNode = graph.add_node(component);
        moleculeNode->set_compartment(moleculeCompartment);
        graph.add_edge(moleculeNode, componentNode);
        return Species(
            SpeciesGraph(std::move(graph), "NM"),
            0.0,
            false,
            "NM");
    };

    Species cytosolic = makeSpecies("CP");
    Species nuclear = makeSpecies("NU");
    SpeciesList list;

    const auto first = list.add(cytosolic);
    const auto second = list.add(nuclear);
    const auto duplicate = list.add(cytosolic);

    REQUIRE(first.second);
    REQUIRE(second.second);
    REQUIRE_FALSE(duplicate.second);
    REQUIRE(duplicate.first == first.first);
    REQUIRE(list.size() == 2);
}
