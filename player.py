
from listing import *
import subprocess, datetime, os, signal, curses, logging

class Player:

    def __init__(self):
        self.area = ChannelArea('free')
        self.listing = ChannelListing(self.area)
        self.channel = 57
        self.schedule = None
        self.proc = None

    def get_yturl(self, ytid):
        return subprocess.check_output(['youtube-dl','-g',ytid])

    def show_info(self, stdscr, item):
        stdscr.clear()
        stdscr.addstr(0, 0, "Channel %d" % self.channel)
        if item is not None:
            stdscr.addstr(1, 0, item['name'])
            stdscr.addstr(2, 0, item['title'])
            stdscr.addstr(3, 0, '%4.1f mins' % item['duration'])
        stdscr.refresh()

    def play_next(self, stdscr):
        self.show_info(stdscr, None)
        t0 = datetime.datetime.now()
        # load schedule if it is empty
        if self.schedule is None or len(self.schedule) == 0:
            self.schedule = self.listing.get_schedule_for_time(self.channel, t0)
            logging.debug("Loaded %d items" % len(self.schedule))
        # get next schedule item
        nextitem = self.schedule[0]
        self.schedule = self.schedule[1:]
        logging.debug(nextitem)
        # get streaming url
        url = nextitem.get('streamUrl')
        if url is None and nextitem['id'][0:3] == 'yt:':
            url = self.get_yturl(nextitem['id'][3:])
        # find out how many seconds to skip into video
        tmins = get_time_mins(t0)
        skipsecs = (tmins - nextitem['time']) * 60.0
        # start player
        self.proc = self.play(url, skipsecs)
        # show info
        self.show_info(stdscr, nextitem)

    def is_playing(self):
        return self.proc.poll() is None
    
    def set_channel(self, channel):
        if channel < self.area.minChannel:
            channel = self.area.maxChannel-1
        elif channel > self.area.maxChannel:
            channel = self.area.minChannel
        if channel != self.channel:
            self.channel = channel
            self.schedule = None
            logging.debug('channel %d' % self.channel)
            self.stop()

    def stop(self):
        if self.proc is not None:
            logging.debug("stop process %r" % self.proc)
            os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
            #self.proc.terminate()

class OmxPlayer(Player):

    def play(self, url, skipsecs):
        return subprocess.Popen(['omxplayer', '--no-osd', '--no-keys', '--pos', str(skipsecs), url],
            preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class FFMPEGPlayer(Player):

    def play(self, url, skipsecs):
        return subprocess.Popen(['ffplay', '-ss', str(skipsecs), url],
            preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

###

player = OmxPlayer()

def main(stdscr):
    curses.halfdelay(2)
    while True:
        player.play_next(stdscr)
        while player.is_playing():
            ch = stdscr.getch()
            if ch >= 0:
                if ch == 259 or ch == 261:
                    player.set_channel(player.channel + 1)
                elif ch == 258 or ch == 260:
                    player.set_channel(player.channel - 1)
                elif ch == 27:
                    return
                else:
                    logging.debug(str(ch))

try:
    curses.wrapper(main)
finally:
    player.stop()
