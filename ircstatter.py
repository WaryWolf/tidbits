#!/usr/bin/env python

# Creates cool graphs of IRC channel popularity.



import re
import datetime
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

# period over which to calculate the running average for a set of data. used when calling runningMeanFast
AVERAGE_PERIOD = 30


# populate this with people's alternate nicknames, and they'll get combined when creating the stats
nick_groups = {
    'user_laptop': 'user',
    'user123': 'user',
    'user_': 'user',
    'dave_phone': 'dave',
    'dave_work': 'dave',
}


def add_date(date_dict, day, month, year):

    if year not in date_dict:
        date_dict[year] = {}

    if month not in date_dict[year]:
        date_dict[year][month] = {}

    if day not in date_dict[year][month]:
        date_dict[year][month][day] = 0
    else:
        date_dict[year][month][day] += 1


def add_msg_to_dict(people_dict, overall_dict, date, nick, msg):

    day = date.day
    month = date.month
    year = date.year

    if nick in people_dict:
        people_dict[nick]['msgcount'] += 1
        #people_dict[nick]['msgs'].append(msg)
    else:
        people_dict[nick] = {}
        people_dict[nick]['msgcount'] = 1
        people_dict[nick]['dates'] = {}
        #people_dict[nick]['msgs'] = [msg]

    add_date(overall_dict, day, month, year)
    add_date(people_dict[nick]['dates'], day, month, year)

# shamelessly stolen from https://stackoverflow.com/questions/13728392/moving-average-or-running-mean 
def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

def build_date_arrays(datedict):
    datearr = []
    cntarr = []
    for year in sorted(datedict.keys()):
        for month in sorted(datedict[year].keys()):
            for day in sorted(datedict[year][month].keys()):
                num = datedict[year][month][day]
                date = datetime.datetime(year, month, day)
                datearr.append(date)
                cntarr.append(num)

    avgarr = runningMeanFast(cntarr, AVERAGE_PERIOD)

    return (datearr, avgarr)

def parse_mirc_logfile(logfilename):
    '''
    Session Start: Thu Jun 19 23:28:51 2008
    Session Ident: #channelname
    [23:28] * Now talking in #channelname
    [23:28] * Topic is 'John McCain called his wife a cunt.'
    [23:28] * Set by derp!~xxx@Rizon-CD694582.dsl.stlsmo.sbcglobal.net on Thu Jun 19 15:31:43
    [23:28] * Reinforce sets mode: +o WaryWolf
    [23:29] <user1> and how
    [23:29] <user1> this channel needed more druid faggots
    '''
    dater = 'Session\s(Start|Time)\:\s\w{3}\s(\w{3}\s\d{1,2}\s\d{2}\:\d{2}\:\d{2}\s\d{4})'
    dater2 = '\-\-\-\sDay\schanged\s\w{3}\s(\w{3}\s\d{2}\s\d{4})'
    logr = '\d?\d?\[?\d\d\:\d\d\:?\d?\d?\]?\s(\*|\[|\-|\<[\@\~\&\+]?([a-zA-Z0-9_\-\[\]\^\`\|\\\{\}]{1,30})\>(\s.*)?)'

    people = {}
    overall = {}
    lineno = 0

    day = None
    month = None
    year = None

    date = None

    first_date = None

    with open(logfilename, 'r') as logfile:


        for line in logfile:
            lineno += 1

            line = line.rstrip()
            
            if len(line) < 2:
                continue
            
            # get rid of control character at start of line
            if ord(line[0]) == 3:
                line = line[1:]



            if line[:14] == 'Session Ident:':
                continue

            if line[:14] == 'Session Close:':
                continue

            dateres = re.match(dater, line)
            
            if dateres:
                datestr = dateres.group(2)
                #print("got >{}<".format(datestr))
                try:
                    date = datetime.datetime.strptime(datestr, '%b %d %H:%M:%S %Y')
                    if first_date == None:
                        first_date = date

                    day = date.day
                    month = date.month
                    year = date.year
                except ValueError:
                    print("couldn't parse date on line {} in {}".format(lineno, logfilename))
                    exit()
                continue
            
            dateres = re.match(dater2, line)
            
            if dateres:
                datestr = dateres.group(1)
                try:
                    date = datetime.datetime.strptime(datestr,'%b %d %Y')
                    if first_date == None:
                        first_date = date

                    day = date.day
                    month = date.month
                    year = date.year
                except ValueError:
                    print("couldn't parse date on line {} in {}".format(lineno, logfilename))
                    exit()
                continue



            res = re.match(logr, line)

            if not res:
                hexl = ":".join("{:02x}".format(ord(c)) for c in line)
                print("line {} in {} did not match: >{}<".format(lineno, logfilename, line))
                #print("line {} in {} did not match: >{}<".format(lineno, logfilename, hexl))
                continue

            if res:
                #print("it matched!")
                #datestr = res.group(1)
                linetype = res.group(1)
                nick = res.group(2)
                msg = res.group(3)
                
                if nick in nick_groups:
                    nick = nick_groups[nick]
                
                control_msg_chars = ['*', '-', '[', '#']

                if linetype[0] in control_msg_chars:
                    linetype = 'ACTION'
                else:
                    linetype = 'MESSAGE'
                    add_msg_to_dict(people, overall, date, nick, msg)



            #print("date = >{}< linetype = >{}< nick = >{}< msg = >{}<".format(date, linetype, nick, msg))
    return (people, overall, first_date, date)

def parse_thelounge_logfile(logfilename):
    '''
    [2016-07-11 03:47:27] * User join
    [2016-07-11 03:47:27] * #Channel topic CONTINUE TALKING
    [2016-07-11 03:47:27] * [^_^] mode +o User
    [2016-07-11 03:47:33] <user1> oh I love a good ear rest
    [2016-07-11 03:47:47] <user2> (22:38:51) (&user1) it's a shitty song and it sucks and the chart sucks
    [2016-07-11 03:47:49] <user2> YOU SUCK
    [2016-07-11 03:48:05] <user2> we aren't friends anymore
    '''
    # see examples above, please don't ask me to explain this
    logr = '\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]\s(\*|<([a-zA-Z0-9_\-\[\]\^\`\|\\\{\}]{1,30})>)\s(.*)'

    #TODO handle logfile not existing
    logfile = open(logfilename, "r")
    log = logfile.readlines()
    logfile.close()

    print("got {} lines.".format(len(log)))

    people = {}
    overall = {}
    lineno = 0
    for line in log:
        lineno += 1
        res = re.match(logr, line)

        if not res:
            print("line {} in {} did not match: {}".format(lineno, logfilename, line))

        if res:
            #print("it matched!")
            datestr = res.group(1)
            linetype = res.group(2)
            nick = res.group(3)
            msg = res.group(4)
            
            try:
                date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("couldn't parse date on line {} in {}".format(lineno, logfilename))
                continue

            if nick in nick_groups:
                nick = nick_groups[nick]

            if linetype[0] == '*':
                linetype = 'ACTION'
            else:
                linetype = 'MESSAGE'
                add_msg_to_dict(people, overall, date, nick, msg)

            #print("date = >{}< linetype = >{}< nick = >{}< msg = >{}<".format(date, linetype, nick, msg))

    # get first and last dates in the log
    res = re.search('\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]', log[0])
    first_date = datetime.datetime.strptime(res.group(0), '[%Y-%m-%d %H:%M:%S]')

    res = re.search('\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]', log[-1])
    last_date = datetime.datetime.strptime(res.group(0), '[%Y-%m-%d %H:%M:%S]')

    #print("first date is {}\nlast date is {}".format(str(first_date),str(last_date)))
    return (people, overall, first_date, last_date)


def pad_zeroes(date_dict, first_date, last_date):
    
    delta = last_date - first_date
    
    for i in range(delta.days + 1):

        this_date = first_date + datetime.timedelta(days = i)
        
        year = this_date.year
        month = this_date.month
        day = this_date.day

        if year not in date_dict:
            date_dict[year] = {}

        if month not in date_dict[year]:
            date_dict[year][month] = {}

        if day not in date_dict[year][month]:
            date_dict[year][month][day] = 0
    

def plot_graph(people, overall, output, individuals):
    # i dunno what this stuff is but it makes the graph happen

    years = YearLocator()   # every year
    months = MonthLocator()  # every month
    yearsFmt = DateFormatter('%Y-%m')

    fig, ax = plt.subplots(figsize=(16,12), dpi=80)

    fig.suptitle('#PLACEHOLDER activity per day', fontsize=20)
    
    legend = []

    if individuals:
        top_talkers = sorted(people, reverse=True, key=lambda k: people[k]['msgcount'])[:individuals]
        for person in top_talkers:
            (p_dates, p_activity) = build_date_arrays(people[person]['dates'])
            print("plotting {}'s activity: {} lines".format(person, people[person]['msgcount']))
            ax.plot_date(p_dates, p_activity, '-')
            legend.append(person)
            
            #print(str(people[person]['dates']))
            #print(str(p_activity))
            #i = 0
            #while i < len(p_dates):
            #    print("{}: {}".format(str(p_dates[i]), p_activity[i]))
            #    i += 1
            #print(str(p_dates))
            #break
    else:
        (o_dates,o_activity) = build_date_arrays(overall)
        ax.plot_date(o_dates, o_activity, '-')
        legend.append('Overall')

    # TODO figure out how to show individual months along the x axis, right now it's kinda bare

    plt.legend(legend, loc='upper right')
    #ax.set_yscale('log') # doesn't work as well as i'd hoped :(
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.autoscale_view()

    ax.fmt_xdata = DateFormatter("%Y-%m-%d")
    ax.grid(True)

    fig.autofmt_xdate()

    if output == 'x11':
        plt.show()
    else:
        filename = 'ircstatter_{}.png'.format(time.strftime('%Y-%m-%d_%H:%M:%S'))
        plt.savefig(filename)
        print('graph saved as {}'.format(filename))


def main():

    #TODO take in logfile name from argv

    parser = argparse.ArgumentParser(description='Create activity graphs from IRC logs')

    parser.add_argument('--output', choices = ['x11', 'png'], default = 'png')
    parser.add_argument('--logtype', choices = ['mirc','thelounge'], required=True)
    parser.add_argument('--individuals', type=int)
    parser.add_argument('logname')

    args = parser.parse_args()

    if args.logtype == 'mirc':
        (people, overall, first_date, last_date) = parse_mirc_logfile(args.logname)
    elif args.logtype == 'thelounge':
        (people, overall, first_date, last_date) = parse_thelounge_logfile(args.logname)
    else:
        parser.print_help()
        exit()



    for p in people.keys():
        pad_zeroes(people[p]['dates'], first_date, last_date)

    pad_zeroes(overall, first_date, last_date)

    plot_graph(people, overall, args.output, args.individuals)



if __name__ == '__main__':
    main()
