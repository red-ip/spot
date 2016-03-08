#!/usr/bin/python


#       Dieses Modul wird verwendet, um sein aktuelles Skript in eine Daemon-App. zu versetzen.
#       Sollte ihr Daemon ueber inetd laufen (s. inet daemon Linux) so sind die meisten, hier
#   angefuehrten Routinen nicht notwendig. Ist dies der Fall, dass std -in,-out u. -err ueber
#   das "Netzwerk" arbeiten, so sollten forks-commands u. Session Manipulation vermieden werden.
#   Nur chdir() und unmask() erweisen sich in diesem Fall als brauchbar.
#
#       Quellennachweise:
#            UNIX Programming FAQ
#                   1.7 How do I get my program to act like a daemon?
#                   http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
#           Advanced Programming in the Unix Environment
#                   W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.
#           (http://www.yendor.com/programming/unix/apue/ch13.html)
#
#   Geschichte:
#           2001/07/10 by J|rgen Hermann
#           2002/08/28 by Noah Spurrier
#           2003/02/24 by Clark Evans
#       2004/06/16 by Peter Landl / IFO.net
#
#       http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012

import sys
import os
import time
from signal import SIGTERM

def deamonize(stdout = '/dev/null', stderr = None, stdin = '/dev/null', pidfile = None, startmsg = 'started with pid %s' ):
    '''
    Diese Routine gabelt ("forks", kloned) den aktuellen Prozess in einen Daemon.
    Die Parameter stdin, stdout und stderr sind Dateinamen, welche die
    Standard- Err-/Ein-/Aus- gabe "ersetzen". Diese Argumente sind optional
    und zeigen standardmaessig ins Nirvana (/dev/null).
    Zu beachten ist, dass stderr ungepuffert geoeffnet ist und so, wenn es
    doppelt offen scheint, nicht die Daten enthaellt, die sie erwarten.
        [Letzter Satz im Original: Note that stderr is opened unbuffered, so
         if it shares a file with stdout then interleaved output
         may not appear in the order that you expect.]
    '''
    # Erstes fork (erster Klon) => fork erstellt aus dem gesamten Prozess einen child-Prozess
    try:
        pid = os.fork()
        if (pid > 0):
            sys.exit(0) # Parent-Prozess schliessen
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Parent "Table/Umgebung" verlassen
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Zweites fork
    try:
        pid = os.fork()
        if (pid > 0):
            sys.exit(0) # Zweiten Parent-Prozess schliessen
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Standard Ein-/Ausgaben oeffnen und Standard-message ausgeben
    if (not stderr):    # Wurde stderr nicht uebergeben => stdout-Pfad nehmen
        stderr = stdout

    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    sys.stderr.write("\n%s\n" % startmsg % pid)
    sys.stderr.flush()
    if pidfile: file(pidfile,'w+').write("%s\n" % pid)

    # Standard Ein-/Ausgaben auf die Dateien umleiten
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def startstop(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile='pid.txt', startmsg='started with pid %s', action='start'):
    if action:
        try:
            pf  = file(pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if 'stop' == action or 'restart' == action:
            if not pid:
                mess = "Could not stop, pid file '%s' missing.\n"
                sys.stderr.write(mess % pidfile)
                if 'stop' == action:
                    sys.exit(1)
                action = 'start'
                pid = None
            else:
                try:
                    while 1:
                        os.kill(pid, SIGTERM)
                        time.sleep(1)
                except OSError, err:
                    err = str(err)
                    if err.find("No such process") > 0:
                        os.remove(pidfile)
                        if 'stop' == action:
                            sys.exit(0)
                        action = 'start'
                        pid = None
                    else:
                        print str(err)
                        sys.exit(1)

        if 'start' == action:
            if pid:
                mess = "Start aborded since pid file '%s' exists.\n"
                sys.stderr.write(mess % pidfile)
                sys.exit(1)

            deamonize(stdout, stderr, stdin, pidfile, startmsg)
            return

        if 'status' == action:
            if not pid:
                sys.stderr.write('Status: Stopped\n')
            else:
                sys.stderr.write('Status: Running\n')
            sys.exit(0)

