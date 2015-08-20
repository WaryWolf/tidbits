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
use Fcntl qw(:DEFAULT :flock :seek);
use Getopt::Long;




my $ua = new LWP::UserAgent;

my $log;

my %urlhash;

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

my $outpath = "images";
my $userdirs;
my $tweetcount = 50;
my $sleep = 180;

# Checks for custom user commands that were added at the call of the script. 
GetOptions (
	"outpath=s" => \$outpath,	#--outpath "string" sets custom directory to save images in
    "userdirs" => \$userdirs,	#--userdirs enables saving images within directories sorted by Twitter handle
    "count=i" => \$tweetcount,	#--count "integer" sets amount of tweets to parse within each cylce
    "sleep=i" => \$sleep,		#--sleep "integer" sets duration to sleep in seconds
);

die "bad input for --sleep\n" if (($sleep < 1) or ($sleep > 9999));
die "bad input for --count\n" if (($tweetcount < 1) or ($tweetcount > 9999));



if (!$owner or !$slug) {
    print "did you forget to set the list info in the source file?\n";
    exit;
}


if (!$api_key or !$api_secret) {
    print "go to https://apps.twitter.com/app/new, sign up for an API key/secret, and put that key in the source code.\n";
    exit;
}


open($log, ">>", "tweetimg.log") or die "couldn't open tweetimg.log: $!\n";

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

my $lastidfilename = 'lastid';

`touch $lastidfilename` if (!-e $lastidfilename);

open(my $lastidfile, "<", "lastid") or die "couldn't open lastid file: $!\n";

my $lastid = <$lastidfile>;

close($lastidfile);

open($lastidfile, ">", "lastid") or die "couldn't open lastid file: $!\n";


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
                "count"                 => $tweetcount,
                "since_id"              => $lastid
        });
    } else {
        $list = $nt->list_statuses({
                "owner_screen_name" => $owner,
                "slug"              => $slug,
                "include_entities"  => "true",
                "include_rts"       => "true",
                "count"             => $tweetcount
        });
    }    

    $lastid = @$list[0]->{'id'} if (scalar @$list > 0);


    foreach my $tweet (@$list) {
        #print Dumper($tweet);	# used for debugging
        
        
        undef %urlhash;

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
        my $medias = $tweet->{'extended_entities'}->{'media'};
        foreach my $media (@$medias) {
            $imgcount += grab_tweet_image($username, $handle, $description, $tweetid, $tweeturl, $media);
        }
        $medias = $tweet->{'entities'}->{'media'};
        foreach my $media (@$medias) {
            $imgcount += grab_tweet_image($username, $handle, $description, $tweetid, $tweeturl, $media);
        }
        my $urlcount = scalar keys %urlhash;
        print "got $urlcount imgs\n";
    }


    print $lastidfile $lastid;
    seek($lastidfile, 0, SEEK_SET);
    
    my $dur = gettimeofday() - $start;

    my $msg = sprintf("saved %d images in %.2f seconds. Sleeping for $sleep seconds...\n", $imgcount, $dur);

    print_and_log($msg) if ($imgcount > 0);

    sleep($sleep);

}





#### SUBROUTINES

sub grab_tweet_image {

    my ($username, $handle, $description, $tweetid, $tweeturl, $media) = @_;


    return 0 if ((!exists($media->{'media_url'})) and (!exists($media->{'media_url_https'})));
    
    my $url;
    
    if (!exists($media->{'media_url_https'})) {
        $url = $media->{'media_url_https'};
    } else {
        $url = $media->{'media_url'};
    }
    
    # skip video thumbnails
    return 0 if $url =~ /video/;


    
    

    (my $strippedurl = $url) =~ s/\//-/g;

    $strippedurl = substr $strippedurl, 7;

    $url .= ":orig";
    

    # if we already saw this url for this tweet already, don't download it.
    return 0 if (exists($urlhash{$url}));

    my $res = $ua->get($url);

    if (!$res->is_success) {
        print_and_log("error downloading $url: $res->status_line");
        return 0;
    }

    my $imgname;

    if ($userdirs) {

        if (!-d "$outpath/$handle") {
            print_and_log("creating $handle\n");
            mkdir "$outpath/$handle";
        }

        $imgname = "$outpath/$handle/$strippedurl";

    } else {

        $imgname = "$outpath/$strippedurl";
    }

    if (-e $imgname) {
        print_and_log("not overwriting $imgname");
        return 0;
    }

    open (my $fh, ">", $imgname)
        or do {
            print_and_log("cannot open \"$imgname\" for writing: $!");
            return 0;
        };
    print_and_log("saving $url");

    #save the url to the urlhash.
    $urlhash{$url} = 1;

    print $fh $res->content;
    
    close $fh;

    # save metadata to image
    my $et = new Image::ExifTool;
    
    my $info = $et->ImageInfo($imgname);
    
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
    return 1;
}

sub print_and_log ($) {
    my $msg = shift;
    my $date = strftime "%Y-%m-%d-%H:%M:%S", localtime;
    chomp($msg);
    print $log "$date: $msg\n";
    print "$date: $msg\n";
}
