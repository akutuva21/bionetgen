#include <iostream>
#include <chrono>
#include <sstream>

#include "../src/ast/Model.hpp"
#include "../src/engine/NetworkGenerator.hpp"
#include "../src/engine/OdeIntegrator.hpp"
#include "../src/parser/PatternGraphBuilder.hpp"
#include "BNGLexer.h"
#include "BNGParser.h"

using namespace bng::ast;
using namespace bng::engine;

static SpeciesGraph makeSpeciesGraph(const std::string& patternText, Model& model) {
    antlr4::ANTLRInputStream input(patternText);
    BNGLexer lexer(&input);
    antlr4::CommonTokenStream tokens(&lexer);
    BNGParser parser(&tokens);
    auto* species = parser.species_def();
    auto graph = bng::parser::buildPatternGraph(species, model, false);
    return SpeciesGraph(std::move(graph));
}

int main() {
    Model model;
    model.addMoleculeType(MoleculeType("A", {}));

    // Add many parameters
    for (int i = 0; i < 50; ++i) {
        Parameter p("p" + std::to_string(i), Expression::number(1.0));
        p.setValue(1.0);
        model.addParameter(p);
    }

    // Add many functions
    for (int i = 0; i < 50; ++i) {
        model.addFunction(Function("f" + std::to_string(i), {}, Expression::number(1.0)));
    }

    GeneratedNetwork network;
    for (int i = 0; i < 500; ++i) {
        network.species.add(Species(makeSpeciesGraph("A()", model), 1.0));
    }

    for (int i = 0; i < 200; ++i) {
        network.reactions.add(Rxn("R" + std::to_string(i), {static_cast<std::size_t>(i)}, {static_cast<std::size_t>((i+1)%500)}, "1.5 * p1 + 0.1", 1.0, "Rule1"));
    }

    auto start = std::chrono::high_resolution_clock::now();

    OdeIntegrator integrator(model, network);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "Time: " << diff.count() << " s\n";

    return 0;
}
