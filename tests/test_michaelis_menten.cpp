// Regression tests for the free substrate calculation of the Michaelis-Menten rate law.
//
// See https://github.com/RuleWorld/bionetgen/issues/323. The textbook form
//
//     b = St - Km - Et;  S = 0.5*(b + sqrt(b*b + 4*St*Km))
//
// cancels catastrophically when b < 0, i.e., when Km is small and the enzyme is in
// excess, and rounds to exactly zero once 4*St*Km drops below about 1e-16*b*b, which
// silently stops the reaction. Reference values below come from 60 digit arithmetic.

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include <cmath>
#include <string>
#include <vector>

#include "ast/Expression.hpp"
#include "util/misc.hh"  // bng2/Network3/src/util/misc.hh

namespace {

// Rate of a MM(kcat,Km) reaction as evaluated by the expression engine
double mmRate(double kcat, double Km, double St, double Et) {
    using bng::ast::Expression;
    const Expression expr = Expression::function(
        "MM", {Expression::number(kcat), Expression::number(Km), Expression::number(St),
               Expression::number(Et)});
    return expr.evaluate([](const std::string&) { return 0.0; });
}

struct SubstrateCase {
    double St, Km, Et;
    double S;  // exact free substrate
};

struct RateCase {
    double kcat, Km, St, Et;
    double rate;  // exact rate
};

// Loose enough to absorb differences in rounding between platforms, tight enough that
// the old form fails every case with the enzyme in excess.
constexpr double kTol = 1e-13;

}  // namespace

TEST_CASE("Michaelis-Menten free substrate", "[michaelis-menten]") {
    SECTION("Matches high precision arithmetic") {
        const std::vector<SubstrateCase> cases = {
            // Enzyme in excess (b < 0): the regime that used to lose precision
            {100.0, 1e-10, 200.0, 9.9999999999800004e-11},
            {100.0, 1e-13, 200.0, 9.9999999999999803e-14},
            {100.0, 1e-14, 200.0, 9.9999999999999980e-15},
            {100.0, 1e-15, 200.0, 1.0000000000000001e-15},
            {100.0, 1e-16, 200.0, 9.9999999999999998e-17},
            {100.0, 1e-20, 200.0, 9.9999999999999995e-21},
            {1e-3, 1e-9, 1e6, 1.0000000009999991e-18},
            {1e6, 1e-8, 1e9, 1.0010010010010010e-11},
            // Substrate in excess (b > 0) and ordinary parameter values
            {200.0, 1e-14, 100.0, 100.00000000000001},
            {10.0, 1.0, 5.0, 5.7416573867739414},
            {2.0, 0.5, 7.0, 0.17617497767990628},
        };
        for (const SubstrateCase& c : cases) {
            INFO("St=" << c.St << " Km=" << c.Km << " Et=" << c.Et);
            REQUIRE_THAT(Util::mm_free_substrate(c.St, c.Km, c.Et),
                         Catch::Matchers::WithinRel(c.S, kTol));
        }
    }

    SECTION("Stays positive for positive Km with the enzyme in excess") {
        // The old form returned exactly zero here, which stopped the reaction outright
        for (double Km = 1e-8; Km > 1e-300; Km *= 1e-8) {
            INFO("Km=" << Km);
            REQUIRE(Util::mm_free_substrate(100.0, Km, 200.0) > 0.0);
        }
    }

    SECTION("Reports the square root of the discriminant") {
        const double St = 100.0, Km = 1e-14, Et = 200.0;
        const double b = St - Km - Et;
        double sqrt_disc = 0.0;
        const double S = Util::mm_free_substrate(St, Km, Et, &sqrt_disc);
        REQUIRE_THAT(sqrt_disc, Catch::Matchers::WithinRel(std::sqrt(b * b + 4.0 * St * Km), kTol));
        // S is a root of S^2 - b*S - St*Km = 0, so 2*S - b is that same square root
        REQUIRE_THAT(2.0 * S - b, Catch::Matchers::WithinRel(sqrt_disc, kTol));
    }
}

TEST_CASE("Michaelis-Menten rate law", "[michaelis-menten]") {
    SECTION("Matches high precision arithmetic") {
        const std::vector<RateCase> cases = {
            {1.0, 1e-10, 100.0, 200.0, 99.999999999900000},
            {1.0, 1e-12, 100.0, 200.0, 99.999999999999000},
            {1.0, 1e-13, 100.0, 200.0, 99.999999999999900},
            {1.0, 1e-14, 100.0, 200.0, 99.999999999999990},
            {1.0, 1e-15, 100.0, 200.0, 99.999999999999999},
            {1.0, 1e-16, 100.0, 200.0, 100.00000000000000},
            {1.0, 1e-20, 100.0, 200.0, 100.00000000000000},
            {2.0, 1e-14, 200.0, 100.0, 199.99999999999998},
            {1.0, 1.0, 10.0, 5.0, 4.2583426132260586},
            {3.0, 0.5, 2.0, 7.0, 5.4714750669602812},
            {1.0, 1e-9, 1e-3, 1e6, 9.9999999999999990e-4},
        };
        for (const RateCase& c : cases) {
            INFO("kcat=" << c.kcat << " Km=" << c.Km << " St=" << c.St << " Et=" << c.Et);
            REQUIRE_THAT(mmRate(c.kcat, c.Km, c.St, c.Et),
                         Catch::Matchers::WithinRel(c.rate, kTol));
        }
    }

    SECTION("Approaches kcat*min(St,Et) as Km goes to zero") {
        for (double Km = 1e-8; Km > 1e-300; Km *= 1e-8) {
            INFO("Km=" << Km);
            REQUIRE_THAT(mmRate(1.0, Km, 100.0, 200.0), Catch::Matchers::WithinRel(100.0, 1e-7));
            REQUIRE_THAT(mmRate(1.0, Km, 200.0, 100.0), Catch::Matchers::WithinRel(100.0, 1e-7));
        }
    }
}
