package main;

use File::Basename;
use File::Spec;
use lib File::Spec->catdir(dirname(__FILE__), 'bng2', 'Perl2');

use BNGModel;

my $val = eval 'system("echo hello")';
print "Result: $val\n";
