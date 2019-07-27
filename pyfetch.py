from curses import wrapper
from datetime import timedelta
import cpuinfo, psutil, os, re, curses, time, dbus, subprocess

# code taken from/inspired by spotify-cli @ https://github.com/pwittchen/spotify-cli-linux/
def get_spotify_property(spotify_property):
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify","/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    return spotify_properties.Get("org.mpris.MediaPlayer2.Player", spotify_property)

def get_song():
    metadata = get_spotify_property("Metadata")
    artist = metadata['xesam:artist'][0]
    title = metadata['xesam:title']
    length = metadata['mpris:length']
    return (artist, title, length)

def status():
    artist, title, length = get_song()
    minutelength = str(timedelta(microseconds=length)).split('.')[0].split('0:')[1]
    return f'song: {artist} - {title} {minutelength}'
# ends here
def getuptime():
    with open('/proc/uptime', 'r') as f:
        return str(timedelta(seconds=float(f.read().split()[0]))).split('.')[0]

def read1line(file):
    with open(file, 'r') as f:
        return f.readline()

def getramusage():
    return round(psutil.virtual_memory().used / 1024 / 1024), round(psutil.virtual_memory().total / 1024 / 1024)

def checkproc(procname):
    for i in psutil.process_iter():
        try:
            if str(procname) in i.name().lower():
                return True
        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

def checkcurrmerge():
    return re.findall(r'\d+ out of \d+|\S+\/\S+', subprocess.check_output(['genlop', '-c']).decode('utf-8'))

if not(len(os.getenv("USER") + "@" + os.uname().nodename)&1):
    user = "fetch for " + os.getenv("USER") + "@" + os.uname().nodename
else:
    user = "fetch for: " + os.getenv("USER") + "@" + os.uname().nodename

cpu = cpuinfo.get_cpu_info().get('brand')
kernel = os.uname().sysname + " " + os.uname().release + " " + os.uname().machine
distro = re.findall(r'NAME="?(\w*)"?', read1line('/etc/os-release'))
desktop = os.getenv("XDG_CURRENT_DESKTOP")

def main(stdscr):
    curses.use_default_colors()
    curses.cbreak()
    curses.curs_set(0)
    maxx = stdscr.getmaxyx()[1]
    while True:
        stdscr.clear()
       # stdscr.addstr(1, round(maxx/2) - round(len(user)/2), user)
        stdscr.addstr(1, 1, f'distro: {distro[0]}')
        stdscr.addstr(2, 1, f'cpu: {cpu} ({psutil.cpu_percent()}%)')
        stdscr.addstr(3, 1, f'mem: {getramusage()[0]}mib of {getramusage()[1]}mib')
        stdscr.addstr(4, 1, f'uptime: {getuptime()}')
        stdscr.addstr(5, 1, f'kernel: {kernel}')
        #if isinstance(desktop, str):
        stdscr.addstr(6, 1, 'wm: openbox')
        try:
            stdscr.addstr(7, 1, status())
        except:
            pass
        stdscr.addstr(8, maxx - 9, re.findall(r'\d\d:\d\d:\d\d', time.ctime())[0])
        if checkproc('emerge'):
            try:
                stdscr.addstr(8, 1, f'em: pkg {checkcurrmerge()[1]} {checkcurrmerge()[0]}')
            except IndexError:
                pass
        stdscr.refresh()
        time.sleep(1)
wrapper(main)
