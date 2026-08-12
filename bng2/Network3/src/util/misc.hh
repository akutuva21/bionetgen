/*
 * misc.hh
 *
 *  Created on: Apr 20, 2012
 *      Author: Leonard Harris
 */

#ifndef MISC_HH_
#define MISC_HH_

#include <string>
#include <iostream>
#include <cmath>
#include <stdlib.h>

using namespace std;

namespace Util {

	// Check whether a variable is NAN
	bool isNAN(double x);

	// Remove leading and trailing whitespace from a string
	void remove_whitespace(string& s);

	// Ratio of Kummer confluent hypergeometric functions M(a+1,b+1,z)/M(a,b,z)
	// See https://en.wikipedia.org/wiki/Confluent_hypergeometric_function
	double Mratio(double a, double b, double z);

	// Free (unbound) substrate concentration of the quasi-steady-state Michaelis-Menten
	// rate law, i.e., the non-negative root of S^2 - b*S - St*Km = 0, b = St - Km - Et.
	// If sqrt_disc is non-NULL, sqrt(b*b + 4*St*Km) is returned through it.
	double mm_free_substrate(double St, double Km, double Et, double* sqrt_disc = NULL);
}

#endif /* MISC_HH_ */
