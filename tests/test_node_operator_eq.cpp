#include <catch2/catch_test_macros.hpp>
#include "../src/core/BNGcore.hpp"

using namespace BNGcore;

TEST_CASE("Node operator== comparisons", "[Node]") {
    NullStateType null_state_type;
    NodeType type1("Type1", null_state_type);
    NodeType type2("Type2", null_state_type);

    Node node1(type1);
    Node node2(type1);
    Node node_diff_type(type2);

    SECTION("Equal nodes") {
        REQUIRE(node1 == node2);
        REQUIRE(node2 == node1);
    }

    SECTION("Different types") {
        REQUIRE_FALSE(node1 == node_diff_type);
    }

    SECTION("Compartment differences") {
        // pattern empty compartment acts as wildcard
        node1.set_compartment("");
        node2.set_compartment("cyto");

        // node1 (pattern) == node2 (target) is true
        REQUIRE(node1 == node2);

        // However, node2 (pattern) == node1 (target) is false
        // because node2 requires "cyto" and node1 has ""
        REQUIRE_FALSE(node2 == node1);

        // Both same compartment
        node1.set_compartment("cyto");
        REQUIRE(node1 == node2);

        // Different compartment
        node2.set_compartment("nuc");
        REQUIRE_FALSE(node1 == node2);
    }

    SECTION("Different states") {
        LabelStateType label_state_type("LabelStateType", "A");
        NodeType type_with_state("TypeWithState", label_state_type);

        Node node3(type_with_state);
        Node node4(type_with_state);

        REQUIRE(node3 == node4);

        // Change state on node4
        LabelState state_b(label_state_type, "B");
        node4.set_state(state_b);

        REQUIRE_FALSE(node3 == node4);
    }
}
