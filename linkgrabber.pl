#!/usr/bin/perl

##########################
#
# linkgrabber.pl - Anthony Vaccaro, 2015
#
# A simple perl IRC bot that listens for urls in channels.
# It performs a HEAD request on any URL, and then grabs it if it thinks it's an image.
# Useful for saving stuff like 4chan links that expire quickly.
#
##########################


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

#config file
our (%bot1conf, %bot2conf);
require "lg-config.pl";


sub print_and_log ($);


my %checksums;
my $checksumfile;
my $log;
my $ua = new LWP::UserAgent;

# 5 megabyte limit on downloading images
my $maxsize = 10 * 1024 * 1024;


my $outpath = "images";

my %ignoreurls = (
    'http://s.rizon.net/FAQ' => 1,
    'http://s.rizon.net/authline' => 1,
    'http://warywolf.net/stats/' => 1,
    );


sub said {
    my $self = shift;
    my $message = shift;
    my $body = $message->{"body"};
    
    # shutdown command
    if ($message->{"who"} eq "pem" and $message->{"body"} eq "die now" and $message->{"channel"} eq "msg") {
        print_and_log("shutting down due to kill command");
        close $log;
        close $checksumfile;
        $self->{"otherbot"}->shutdown();
        $self->shutdown();
    }

    # ignore PMs.
    return if $message->{"channel"} eq "msg";


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
    

    my $chan = $message->{"channel"};
    $chan =~ s/\#//;
    
    # fix for infinityb's dumb channel
    if ($chan eq '') {
        $chan = 'yshi';
    }

    if (exists($ignoreurls{$url})) {
        return;
    }

    # imgur webms are embedded in html pages. cute, but annoying...
    $url =~ s/gifv/webm/ if ($url =~ m/^http.*imgur.*gifv$/);;

    # rewrite gfycat urls
    if ($url =~ /gfycat*((?!webm|mp4).)*$/) {
            $url = gfycat_url_rewrite($url);
    }

    my $head = $ua->head($url);

    if ($head->header("Content-Type") =~ m/(image|video\/webm|video\/mp4)/) {
        download_url($url, $head, $chan);
    }
}

sub download_url {

    my $url = shift;
    my $head = shift;
    my $chan = shift;

    my $date = strftime "%Y-%m-%d-%H:%M:%S", localtime;
    (my $strippedurl = $url) =~ s/\//-/g;


    #remove any crap after a question mark in the url
    $strippedurl =~ s/^([^?]*)\?.*/$1/ if ($strippedurl =~ /\?/);

    # remove the ":large" stuff too (found in twitter image urls)
    $strippedurl =~ s/^([^:]*)\:.*/$1/ if ($strippedurl =~ /\:/);


    my $size = $head->header("Content-Length");

    if (!$size) {
        print_and_log "skipping $url from $chan because it has no Content-Length header!";
        return;
    }

    if ($size > $maxsize) {
        print_and_log "skipping $url from $chan because its size is too large!";
        return;
    }

    my $imgname = "$outpath/$chan/$date-$strippedurl";


    my $data = $ua->get($url);

    my $thischecksum = md5_hex($data->content);

    if (exists($checksums{$thischecksum})) {
        print_and_log "not grabbing $url from $chan due to checksum collision";
        return;
    }
    
    print_and_log "$date: grabbing $url from $chan\n";

    $checksums{$thischecksum} = 1;

    print $checksumfile "$thischecksum\n";
    $checksumfile->flush();


    if (!-d "$outpath/$chan") {
        print_and_log "creating $chan\n";
        mkdir "$outpath/$chan";
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

sub gfycat_url_rewrite {
    my $url = shift;

    my $data = $ua->get($url);

    my $cont = $data->content;
    my $urlline;
    my $realurl;
    foreach my $line (split(/^/, $cont)) {
        if ($line =~ /gfyWebmUrl/) {
            $urlline = $line;
            last;
        }
    }
    foreach my $field (split(/"/, $urlline)) {
        if ($field =~ /http/) {
            $realurl = $field;
            last;
        }
    }
    return $realurl;
}

sub print_and_log ($) {
    my $msg = shift;
    my $date = strftime "%Y-%m-%d-%H:%M:%S", localtime;
    chomp($msg);
    print $log "$date: $msg\n";
    print "$date: $msg\n";
}


### PROGRAM START


open ($log, ">>", "linkgrabber.log") or die "couldn't open linkgrabber.log!";

$log->autoflush;


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

my $bot1 = LinkGrabber->new(
    server => $bot1conf{"server"},
    port => $bot1conf{"port"},
    ssl => $bot1conf{"ssl"},
    channels => $bot1conf{"channels"},
    nick => $bot1conf{"nick"},
    alt_nicks => $bot1conf{"alt_nicks"},
    username => $bot1conf{"username"},
    name => $bot1conf{"name"},
    no_run => $bot1conf{"no_run"},
    ignore_list => $bot1conf{"ignore_list"},
);

my $bot2 = LinkGrabber->new(
    server => $bot2conf{"server"},
    port => $bot2conf{"port"},
    ssl => $bot2conf{"ssl"},
    channels => $bot2conf{"channels"},
    nick => $bot2conf{"nick"},
    alt_nicks => $bot2conf{"alt_nicks"},
    username => $bot2conf{"username"},
    name => $bot2conf{"name"},
    no_run => $bot2conf{"no_run"},
    ignore_list => $bot2conf{"ignore_list"},
);

$bot1->{"otherbot"} = $bot2;
$bot2->{"otherbot"} = $bot1;


$bot1->run();
$bot2->run();
use POE;
$poe_kernel->run();

close $log;
