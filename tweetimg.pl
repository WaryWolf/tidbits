#!/usr/bin/perl

######################################
#
# tweetimg.pl - (c) Anthony Vaccaro, 2015
#
# This perl script periodically checks a Twitter "list"
# and downloads any images posted to the list.
# An API key is needed which can be acquired at 
# https://apps.twitter.com/app/new .
# 
# Now saves information about the tweet the image was attached to
# in the image metadata. This script was written for my true bud,
# Heaud (http://twitter.com/RobHued).
#
#
# Note: This version has the while loop removed.
#
######################################

use strict;
use warnings;

use Net::Twitter::Lite::WithAPIv1_1;
use LWP::UserAgent;
use Time::HiRes 'gettimeofday';
use POSIX 'strftime';
use IO::Handle;
use Image::ExifTool;
use Fcntl qw(:DEFAULT :flock :seek);
use Getopt::Long;
use Config::Simple;


my $log;

my %urlhash;

sub print_and_log($);



my $cfile = 'tweetimg.cfg';
my $cfg = new Config::Simple(syntax=>'http');


#Load from configuration file and assign values
$cfg->read($cfile) or die "Unable to open $cfile." if (-e $cfile);
my $api_key = $cfg->param("api_key");
my $api_secret = $cfg->param("api_secret");
my $access_token = $cfg->param("access_token");
my $access_token_secret = $cfg->param("access_token_secret");
my @slugs = $cfg->param("slugs");
my $outpath = $cfg->param("outpath");
my $userdirs = $cfg->param("userdirs");
my $tweetcount = $cfg->param("tweetcount");
my $include_retweets = $cfg->param("retweets");
my %slughash;


print "Twitter API keys are missing from the configuration file. Please sign up at https://apps.twitter.com/app/new and obtain your API keys.\n" if (!$api_key or !$api_secret);

until ($api_key) {
    print "Please enter your API key.\nAPI key: ";
    $api_key = <STDIN>;
    chomp $api_key;
    $cfg->param('api_key', $api_key);
}

until ($api_secret) {
    print "Please enter your API secret key.\nAPI secret: ";
    $api_secret = <STDIN>;
    chomp $api_secret;
    $cfg->param('api_secret', $api_secret);
}


$cfg->write($cfile) or die "Unable to write $cfile.";

mkdir "logs" unless (-d "logs");
my $filename = strftime("logs/tweetimg-%Y-%m.log", localtime);
open($log, ">>", $filename) or die "Unable to open log file: $!\n";
$log->autoflush;

print_and_log("starting run.");

my $nt = Net::Twitter::Lite::WithAPIv1_1->new(
    traits              => [ 'OAuth', 'API::RESTv1_1' ],
    consumer_key        => $api_key,
    consumer_secret     => $api_secret,
    legacy_lists_api    => 0,
    ssl                 => 1,
);

if ($access_token && $access_token_secret) {
    $nt->access_token($access_token);
    $nt->access_token_secret($access_token_secret);
}

#API authorization check
unless ( $nt->authorized ) {
    print "\nClient has not been authorized. Visit ", $nt->get_authorization_url, " to grant access. Obtain the PIN from the website and enter it below.\nPIN: ";

    my $pin = <STDIN>;
    chomp $pin;

    my($access_token, $access_token_secret, $user_id, $screen_name) = $nt->request_access_token(verifier => $pin);
    
    $cfg->param('access_token', $access_token);
    $cfg->param('access_token_secret', $access_token_secret);
}

until ($tweetcount) {
    $tweetcount = 60;
    $cfg->param('tweetcount', $tweetcount);
}


$cfg->write($cfile) or die "Unable to write $cfile.";


until (@slugs) {
    print "Please enter the list title and list creator's handle separated by a space. Multiple lists can be added by separating each entry with a comma. (example-list creator1, second-list creator2)\nTitle & creator: ";
    my $input = <STDIN>;
    chomp $input;
    
    #Prepare the input
    $input =~ s/, /,/g; 
    my $list;
    foreach my $entry(split(/,/, $input)) {
        my ($l,$c) = split(/ /, $entry);
        $list .= $entry . ',' if ($l and $c);
    }
    chop $list;
    
    #Write and reopen so that the value becomes an array
    $cfg->param("slugs", $list);
    $cfg->write($cfile) or die "Unable to write $cfile.";
    $cfg->read($cfile) or die "Unable to open $cfile.";
    @slugs = $cfg->param("slugs");

}

#Converts array from cfg into hash
foreach (@slugs) {
    my ($l,$c) = split(/ /, $_);
    $slughash{$l} = $c;
}


my %state;
my $statefile;
if (-e "tweetimg.state") {
    open ($statefile, "<", "tweetimg.state") or die "couldn't open state file: $!\n";
    while (my $line = <$statefile>) {
        chomp $line;
        my @fields = split(/ /, $line);
        my $slugname = $fields[0];
        my $lastid = $fields[1];
        $state{$slugname} = $lastid;
    }
    close $statefile;
}
#Parse the tweets
    my $imgcountsum;



    foreach my $slugtitle(keys %slughash) {
        my $slugowner = $slughash{$slugtitle};
        $outpath = "images/$slugtitle";
        #note: implement File::Path::Tiny
        mkdir "images" unless (-d "images");
        mkdir $outpath unless (-d $outpath);
        my $lastid;
        if (exists($state{$slugtitle})) {
            $lastid = $state{$slugtitle};
        } else {
            $lastid = 0;
        }
        
        my $list;
        my $imgcount = 0;
        my $start = gettimeofday();

        if ($lastid) {
            $list = $nt->list_statuses({    
                    "owner_screen_name"     => $slugowner,
                    "slug"                  => $slugtitle,
                    "include_entities"      => "true",
                    "include_rts"           => $include_retweets,
                    "count"                 => $tweetcount,
                    "since_id"              => $lastid
            });
        } else {
            $list = $nt->list_statuses({
                    "owner_screen_name" => $slugowner,
                    "slug"              => $slugtitle,
                    "include_entities"  => "true",
                    "include_rts"       => $include_retweets,
                    "count"             => $tweetcount
            });
        }    

        $lastid = @$list[0]->{'id'} if (scalar @$list > 0);

        #Start searching tweets
        print_and_log("Searching $slugtitle for new images...\n");
        foreach my $tweet (@$list) {
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
        }

        $state{$slugtitle} = $lastid;
    
        my $dur = gettimeofday() - $start;

        my $msg = sprintf("Saved %d images from $slugtitle in %.2f seconds.", $imgcount, $dur);
        
        print_and_log($msg) if ($imgcount > 0);
        
        $imgcountsum += $imgcount;
    }

print_and_log("saving lastids...");

open ($statefile, ">", "tweetimg.state") or die "couldn't open state file: $!\n";
foreach my $slug (keys %state) {
    print $statefile "$slug $state{$slug}\n";
}
close $statefile;
print_and_log("finished run.");



#### SUBROUTINES

sub grab_tweet_image {

    my ($username, $handle, $description, $tweetid, $tweeturl, $media) = @_;


    my $ua = new LWP::UserAgent;
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
        my $errmsg = $res->status_line;
        my $code = $res->code;
        print_and_log("error downloading $url: $code - $errmsg");
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
        #print_and_log("Not overwriting $imgname");
        return 0;
    }

    open (my $fh, ">", $imgname)
        or do {
            print_and_log("Cannot open \"$imgname\" for writing: $!");
            return 0;
        };
    print_and_log("Saving $url");

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
    my $date = strftime "%Y-%m-%d_%H:%M:%S", localtime;
    chomp($msg);
    print $log "$date: $msg\n";
    print "$date: $msg\n";
}
