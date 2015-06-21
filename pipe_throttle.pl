#!/usr/bin/perl

use strict;
use warnings;

use Time::HiRes 'usleep';
use Getopt::Long;

$| = 1;

my $limit;
my $delay;
my $data;

GetOptions( 'limit=i' => \$limit );

die "please give a throttle limit with --limit=X, where X is in megabytes per second.\n" if !$limit;

$delay = 100000 / $limit;


while(!eof(STDIN)) {

	read STDIN, $data, 102400 or die "error reading from stdin: $!\n";
	usleep($delay);
	print STDOUT $data;
}


