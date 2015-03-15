#!/usr/bin/python

# derping around with movies, by pem
# 31/05/2014

#
# This script uses the Rotten Tomatoes web API, plus the 
# Python wrapper for that API written by zachwill, to
# sort a directory of movies (with directory names in 'scene' format)
# and recommend the lowest rated movies for deletion.
#

# Rotten Tomatoes API:
# http://developer.rottentomatoes.com

# Python wrapper:
# https://github.com/zachwill/rottentomatoes

# USAGE:
# ./movie_rater.py dirname threshold


from rottentomatoes import RT
import os
import sys
import requests
import json

if len(sys.argv) != 3:
    print "Usage: ./movie_rater.py dirname threshold"
    exit(1)

searchdir = sys.argv[1]
keepthreshold = int(sys.argv[2])

myrt = RT()

movielist = os.listdir(searchdir)

movielist.sort()


def omdbsearch(title):

    data = json.loads(requests.get("http://omdbapi.com/?t=" + title + "&r=json").text)
    #print str(data)
    return data


keepcount = 0
deletecount = 0

breakwords = ['720P','1080P','PROPER','DC','REPACK','LIMITED','REMASTERED','INTERNAL','RERIP','EXTENDED','THEATRICAL', 'UNRATED']

for movie in movielist:
    title = []
    year = 1
    for word in movie.split('.'):
        
        try:
            year = int(word)
        except ValueError:
            year = 1

        # catches the case of films whose titles only consist of a year, eg. '2012'
        if (year > 1900 and year < 2015) and len(title) > 0: 
            break
        if word.upper() in breakwords:
            break
        
        title.append(word)

    fulltitle = ' '.join(title)

    results = myrt.search(fulltitle)

    omdb = omdbsearch(fulltitle)


    try:
        genres = omdb["Genre"]
    except:
        genres = ""

    if "comedy" in genres.lower():
        #print "DELETE " + fulltitle.upper() + " ASAP! COMEDY FOUND!"
        comedyflag = True
    
    else:
        #print "Title: " + fulltitle + " Genres: " + genres
        comedyflag = False



    if len(results) == 0:
        results = myrt.search('.'.join(title))
        if len(results) == 0:
            print "no results for " + fulltitle
            continue
    
    
    ratings = []
    for result in results:
        thisrating = result["ratings"]["critics_score"]
        
        try:
            resyear = int(result["year"])
        except ValueError:
            resyear = 0

        # sometimes the year listed in the directory name will not match RT's exactly,
        # so allow some leeway
        yeardiff = abs(year - resyear)

        if thisrating != -1 and yeardiff < 3:
            ratings.append(thisrating)
    
    if len(ratings) == 0:
        continue
    
    avgrating = sum(ratings) / float(len(ratings))
    
    
    if avgrating < keepthreshold and comedyflag == True:
        print "%s has %d critic ratings, averaging %0.1f. better delete it!" % (fulltitle,len(ratings),avgrating)
        deletecount +=1
    else:
    #    print "%s has %d critic ratings, averaging %0.1f. better keep it!" % (fulltitle,len(ratings),avgrating)
        keepcount +=1

print "of %d movies, %d have over %d rating on RT." % (len(movielist),keepcount,keepthreshold)



