
from listing import *
import subprocess, datetime

class Player:

    def __init__(self):
        self.area = ChannelArea('free')
        self.listing = ChannelListing(self.area)
        self.channel = 57
        self.schedule = None

    def get_yturl(self, ytid):
        return subprocess.check_output(['youtube-dl','-g',ytid])

    def next(self):
        t0 = datetime.datetime.now()
        if self.schedule is None or len(self.schedule) == 0:
            self.schedule = self.listing.get_schedule_for_time(self.channel, t0)
        nextitem = self.schedule[0]
        self.schedule = self.schedule[1:]
        print(nextitem)
        url = nextitem.get('streamUrl')
        if url is None and nextitem['id'][0:3] == 'yt:':
            url = self.get_yturl(nextitem['id'][3:])
        tmins = get_time_mins(t0)
        skipsecs = (tmins - nextitem['time']) * 60.0
        self.play(url, skipsecs)

class OmxPlayer(Player):

    def play(self, url, skipsecs):
        subprocess.call(['omxplayer', '--pos', str(skipsecs), url])

class FFMPEGPlayer(Player):

    def play(self, url, skipsecs):
        subprocess.call(['ffplay', '-ss', str(skipsecs), url])

###

player = OmxPlayer()
while True:
    player.next()


