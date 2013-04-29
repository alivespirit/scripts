#!/usr/bin/env python

import subprocess, sys, datetime, time

class bcolors:
    HEADER = '\033[97m'
    OKBLUE = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def ping(ip):
    devnull = open('/dev/null', 'w')
    trig = cnt = 0
    start = datetime.datetime.now()
    down = up = datetime.timedelta(milliseconds=1)
    while True:
        newping = subprocess.Popen(["ping", "-c", "1", "-w", "1", ip],\
                                   shell=False, stdout=devnull, stderr=devnull)
        newping.wait()
        if newping.returncode == trig:
            cnt += 1
            if cnt % 30 == 0:
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + bcolors.OKBLUE + " No changes in state of host." + bcolors.ENDC
            time.sleep(5)
        else:
            cnt = 0
            trig = newping.returncode
            if trig == 0:
                down += (datetime.datetime.now()-start)
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + bcolors.WARNING + " State changed, now host is UP. Downtime: " + \
                      str(datetime.datetime.now()-start)[:-7] + bcolors.ENDC
            else:
                up += (datetime.datetime.now()-start)
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + bcolors.WARNING + " State changed, now host is DOWN. Uptime: " + \
                      str(datetime.datetime.now()-start)[:-7] + bcolors.ENDC
            start = datetime.datetime.now()
            print bcolors.OKBLUE + "Total uptime/downtime: " + bcolors.ENDC + \
                  bcolors.OKGREEN + str(up)[:-7] + bcolors.ENDC + "/" + bcolors.FAIL + str(down)[:-7] + bcolors.ENDC

def main():
    if len(sys.argv)==2:
        ip=sys.argv[1]
    else:
        sys.exit("Usage: newping.py <IP>")
    print bcolors.HEADER + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
          " Start, suppose host is up. If host actually is down, you'll see message below in 1 second." + bcolors.ENDC
    try:
        ping(ip)
    except KeyboardInterrupt:
        print "aught keyboard interrupt, exiting."
        print "On " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " host is in previous state."
        sys.exit(0)

if __name__ == '__main__':
    main()
