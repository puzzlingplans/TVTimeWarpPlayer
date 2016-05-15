
import urllib, json, datetime

SERVER_ROOT = "http://prod.tvtimewarp.com"

DOW_TO_STRING = [ "?","Mo","Tu","We","Th","Fr","Sa","Su" ]

class ChannelArea:

    def __init__(self, area='free'):
        self.area = area
        url = '%s/channels/%s/area.json' % (SERVER_ROOT, self.area)
        data = json.load(urllib.urlopen(url))
        self.minChannel = data['minChannel']
        self.maxChannel = data['maxChannel']
        self.defaultChannel = data['defaultChannel']

    def get_listing(self, channel, isoweekday):
        url = '%s/channels/%s/%d-%s.json' % (SERVER_ROOT, self.area, channel, DOW_TO_STRING[isoweekday])
        data = json.load(urllib.urlopen(url))
        return data

class ChannelListing:

    def __init__(self, area):
        self.area = area
        self.listing = None
        self.dow = None

    def get_schedule_for_time(self, channel, time):
        dow = time.isoweekday()
        if self.dow != dow:
            self.listing = self.area.get_listing(channel, dow)
        tmins = get_time_mins(time)
        playlist = self.listing['playlist']
        for i,item in enumerate(playlist):
            if item['time'] + item['duration'] >= tmins:
                return playlist[i:]


def get_time_mins(time):
    return (time.second + time.minute*60 + time.hour*3600) / 60.0
    

###

#area = ChannelArea()
#listing = ChannelListing(area)
#sched = listing.get_schedule_for_time(50, datetime.datetime.now())
#print(sched)
#area.get_listing(50, 1)

