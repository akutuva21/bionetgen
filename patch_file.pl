my $file = 'bng2/Perl2/BNGAction.pm';
open(my $fh, '<', $file) or die;
my $content = do { local $/; <$fh> };
close($fh);

$content =~ s/my \$sc_ext = \(\$ext eq "cdat"\) \? "csc" : "gsc";/my \$sc_ext = (\$ext eq 'cdat') ? 'csc' : 'gsc';/g;
$content =~ s/open\(my \$bfh, "<", \$base_file\) or next;/open(my \$bfh, '<', \$base_file) or next;/g;
$content =~ s/open\(my \$pfh, "<", \$bump_file\) or do \{ close\(\$bfh\); next; \};/open(my \$pfh, '<', \$bump_file) or do { close(\$bfh); next; };/g;

open($fh, '>', $file) or die;
print $fh $content;
close($fh);
