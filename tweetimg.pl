#!/usr/bin/perl

######################################
#
# tweetimg.pl - (c) Anthony Vaccaro, 2015
#
# This perl script periodically checks a Twitter "list"
# and downloads any images posted to the list, to an "images"
# folder. It requires an API key, which can be acquired at 
# https://apps.twitter.com/app/new .
# 
# Now saves information about the tweet the image was attached to
# in the image metadata. This script was written for my true bud,
# Heaud (http://twitter.com/RobHued).
#
######################################

use strict;
use warnings;

use Net::Twitter;
use Data::Dumper;
use LWP::UserAgent;
use Time::HiRes 'gettimeofday';
use POSIX 'strftime';
use IO::Handle;
use Image::ExifTool;
#use open ':std', ':encoding(UTF-8)';

my $ua = new LWP::UserAgent;

my $log;

my $outpath = "images";

sub print_and_log($);


# FILL IN THESE SIX VARIABLES TO MAKE THE PROGRAM "WORK".

# you get these by signing up to the twitter API at https://apps.twitter.com/app/new .
my $api_key = '';
my $api_secret = '';

# you get these by running the program and following the instructions to auth the app.
my $access_token = '';
my $access_token_secret = '';

# add the list information here. the owner is the twitter handle of the owner of the list.
# the slug is the name of the list as it appears in URLs (usually all lowercase and spaces replaced by hyphens).
my $owner = '';
my $slug = '';



if (!$owner or !$slug) {
    print "did you forget to set the list info in the source file?\n";
    exit;
}


if (!$api_key or !$api_secret) {
    print "go to https://apps.twitter.com/app/new, sign up for an API key/secret, and put that key in the source code.\n";
    exit;
}


open($log, ">>", "tweetimg.log") or die "couldn't open tweetimg.log\n";

$log->autoflush;


my $nt = Net::Twitter->new(
    traits          => [ 'OAuth', 'API::RESTv1_1' ],
    consumer_key    => $api_key,
    consumer_secret => $api_secret,
);

if ($access_token && $access_token_secret) {
    $nt->access_token($access_token);
    $nt->access_token_secret($access_token_secret);
}

unless ( $nt->authorized ) {
    # The client is not yet authorized: Do it now
    print "Authorize this app at ", $nt->get_authorization_url, " and enter the PIN number below:\n";

    my $pin = <STDIN>; # wait for input
    chomp $pin;

    my($access_token, $access_token_secret, $user_id, $screen_name) = $nt->request_access_token(verifier => $pin);

    print "access_token = $access_token\n";
    print "access_token_secret = $access_token_secret\n";
    print "put those into your source and run again...\n";
    exit;
}

my $lastid = '';

while(1) {

    my $list;
    my $imgcount = 0;
    my $start = gettimeofday();

    if ($lastid) {
        $list = $nt->list_statuses({    
                "owner_screen_name"     => $owner,
                "slug"                  => $slug,
                "include_entities"      => "true",
                "include_rts"           => "true",
                "count"                 => 50,
                "since_id"              => $lastid
        });
    } else {
        $list = $nt->list_statuses({
                "owner_screen_name" => $owner,
                "slug"              => $slug,
                "include_entities"  => "true",
                "include_rts"       => "true",
                "count"             => 50
        });
    }    

    $lastid = @$list[0]->{'id'} if (scalar @$list > 0);

    foreach my $tweet (@$list) {
        #print Dumper($tweet);

        # username = full username
        # handle = @user
        # description = tweet text
        my $username;
        my $handle;
        my $description;
        my $tweetid;
        my $tweeturl;
        # if it's a retweet, assign ownership properly
        if (exists($tweet->{'retweeted_status'})) {
            $username = $tweet->{'retweeted_status'}->{'user'}->{'name'};
            $handle = $tweet->{'retweeted_status'}->{'user'}->{'screen_name'};
            $description = $tweet->{'retweeted_status'}->{'text'};
            $tweetid = $tweet->{'retweeted_status'}->{'id_str'};
        } else {
            $username = $tweet->{'user'}->{'name'};
            $handle = $tweet->{'user'}->{'screen_name'};
            $description = $tweet->{'text'};
            $tweetid = $tweet->{'id_str'};
        }

        $tweeturl = "https://twitter.com/$handle/status/$tweetid";


        next if (!exists($tweet->{'entities'}));
        next if (!exists($tweet->{'entities'}->{'media'}));
        my $medias = $tweet->{'entities'}->{'media'};
        foreach my $media (@$medias) {
            next if ((!exists($media->{'media_url'})) and (!exists($media->{'media_url_https'})));
            
            my $url;
            
            if (!exists($media->{'media_url_https'})) {
                $url = $media->{'media_url_https'};
            } else {
                $url = $media->{'media_url'};
            }
            
            # skip video thumbnails
            next if $url =~ /video/;


            # remove the suffix from the tweet url
            #$tweeturl =~ s/([A-Z]*)\/photo\/\d$/$1/;

            (my $strippedurl = $url) =~ s/\//-/g;

            $strippedurl = substr $strippedurl, 7;

            $url .= ":orig";
            
            my $res = $ua->get($url);

            if (!$res->is_success) {
                print_and_log("error downloading $url: $res->status_line");
                next;
            }

            if (!-d "$outpath/$handle") {
                print_and_log("creating $handle\n");
                mkdir "$outpath/$handle";
            }

            my $imgname = "$outpath/$handle/$strippedurl";

            if (-e $imgname) {
                print_and_log("not overwriting $imgname");
                next;
            }

            open (my $fh, ">", $imgname)
                or do {
                    print_and_log("cannot open \"$imgname\" for writing: $!");
                    next;
                };
            print_and_log("saving $url");
            print $fh $res->content;
            $imgcount++;
            close $fh;

            # save metadata to image
            my $et = new Image::ExifTool;
            #$et->Options(PNGEarlyXMP => 1);
            my $info = $et->ImageInfo($imgname);
            #$et->SetNewGroups('XMP', 'EXIF', 'IPTC');
            $et->SetNewValue('XMP:Creator', $username);
            $et->SetNewValue('XMP:Description', $description);
            $et->SetNewValue('XMP:Source', $tweeturl);
            my $err = $et->WriteInfo($imgname);

            if ($err != 1) {
                my $warn = $et->GetValue('Warning');
                my $errmsg = $et->GetValue('Error');
                print_and_log("WARNING: $warn") if $warn;
                print_and_log("ERROR: $errmsg") if $errmsg;
            }
        }
    }

    my $dur = gettimeofday() - $start;

    my $msg = sprintf("saved %d images in %.2f seconds. Sleeping for 3 minutes...\n", $imgcount, $dur);

    print_and_log($msg);

    sleep(180);

}





#### SUBROUTINES

sub print_and_log ($) {
    my $msg = shift;
    my $date = strftime "%Y-%m-%d-%H:%M:%S", localtime;
    chomp($msg);
    print $log "$date: $msg\n";
    print "$date: $msg\n";
}
