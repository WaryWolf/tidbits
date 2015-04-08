#!/usr/bin/perl

use strict;
use warnings;

package LinkGrabber;
use base "Bot::BasicBot";
use URI::Find::Simple "list_uris";
use LWP::UserAgent;
use POSIX "strftime";
use Digest::MD5 "md5_hex";
use IO::Handle;
use Data::Dumper;


sub print_and_log ($);

my %checksums;
my $checksumfile;


# 5 megabyte limit on downloading images
my $maxsize = 5 * 1024 * 1024;


my %ignoreurls = (
    'http://s.rizon.net/FAQ' => 1,
    'http://s.rizon.net/authline' => 1,
    'http://warywolf.net/stats/' => 1,
    );

my $ua = new LWP::UserAgent;

open (my $log, ">>", "linkgrabber.log") or die "couldn't open linkgrabber.log!";

my $startdate = strftime "%Y-%m-%d-%H:%M:%S", localtime;

print_and_log "started on $startdate\n";

if (!-e "linkgrabber-checksums.log") {
    open ($checksumfile, ">", "linkgrabber-checksums.log") or die "couldn't open linkgrabber-checksums.log!";
} else {
    open ($checksumfile, "+<", "linkgrabber-checksums.log") or die "couldn't open linkgrabber-checksums.log!";

    foreach my $line (<$checksumfile>) {

        chomp $line;
        $checksums{$line} = 1;
    }
}

sub said {
    my $self = shift;
    my $message = shift;
    my $body = $message->{body};
    
    # ignore PMs.
    return if $message->{channel} eq "msg";

    if ($message->{"who"} eq "pem" and $message->{"body"} eq "die now") {
        close $log;
        close $checksumfile;
        $self->shutdown();
    }

    my @urls = list_uris($body);

    if (@urls) {
        #$self->reply($message, "that was a url!");
         process_url($_, $message) for (@urls);
    } else {
        return;
    }    
}

sub process_url {

    my $url = shift;
    my $message = shift;
    
    my $date = strftime "%Y-%m-%d-%H:%M:%S", localtime;

    my $chan = $message->{channel};
    $chan =~ s/\#//;
    
    if (exists($ignoreurls{$url})) {
        return;
    }

    my $strippedurl = $url;

    $strippedurl =~ s/\//-/g;

    my $head = $ua->head($url);

    if ($head->header("Content-Type") =~ m/image/) {

        my $size = $head->header("Content-Length");

        if (!$size) {
            print_and_log "$date: skipping $url from $chan because it has no Content-Length header!\n";
            return;
        }

        if ($size > $maxsize) {
            print_and_log "$date: skipping $url from $chan because its size is too large!\n";
            return;
        }

        my $imgname = "$chan/$date-$strippedurl";

        my $data = $ua->get($url);

        my $thischecksum = md5_hex($data->content);

        if (exists($checksums{$thischecksum})) {
            print_and_log "$date: not grabbing $url from $chan due to checksum collision\n";
            return;
        }
        
        print_and_log "$date: grabbing $url from $chan\n";

        $checksums{$thischecksum} = 1;

        print $checksumfile "$thischecksum\n";
        $checksumfile->flush();


        if (!-d $chan) {
            print_and_log "creating $chan\n";
            mkdir $chan;
        }
        return if (-f $imgname);

        open(my $fh, ">", $imgname)
            or do {
                print "cannot open \"$imgname\" for writing: $!\n";
                return;
            };

        print $fh $data->content;

        close $fh;

    }
}

sub print_and_log ($) {
    my $msg = shift;
    print $log $msg;
    print $msg;
}

my $bot = LinkGrabber->new(
    server => "irc.rizon.sexy",
    port => "7000",
    channels => ["#dsfargeg"],
    nick => "pembot",
    alt_nicks => ["pembot2", "pembot3"],
    username => "dingus",
    name => "qtpi",

    ignore_list => ["dokuro", "minako", "YouTube", "erlen"],

    );

$bot->run();


close $log;
