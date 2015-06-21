#!/usr/bin/perl

##########
#
# (c) Anthony Vaccaro, 2015
#
# pipe_throttle.pl - this script prints stdin to stdout, 
# but throttles the speed of the throughput to the limit set
# in the arguments. It is very simple but works well enough.
# 
# You are probably better off using something called "throttle"
# which can be found at the links below:
#
# http://klicman.org/default_007.html
# http://pkgs.fedoraproject.org/repo/pkgs/throttle/throttle-1.2.tar.gz/
#
##########

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


