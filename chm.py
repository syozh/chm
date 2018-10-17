#!/usr/bin/env python3 

import os, sys, subprocess, configparser, pickle, poplib

title = 'Pechkin'
conffile = 'chm.cfg'
datafile = 'chm.dat'

def readconf(file):
    conf = configparser.ConfigParser()
    conf.read(file)
    return conf

def readdata(file):
    data = {}
    if os.path.isfile(file) and os.path.getsize(file) > 0:
        with open(file, 'rb') as f:
            data = pickle.load(f)
    return data

def loaduidl(mboxname, mboxconf):
    conn = poplib.POP3_SSL(mboxconf['host'], mboxconf['port'])
    conn.user(mboxconf['user'])
    conn.pass_(mboxconf['pass'])
    resp, uidl, size = conn.uidl()
    conn.quit()
    if resp != b'+OK':
        raise Exception('Can not load UIDL from ' + mboxname)
    return uidl

def main():
    changed = False
    #summary = []
    try:
        conf = readconf(conffile)
        data = readdata(datafile)
        for mboxname in conf.sections():
            mboxconf = dict(conf.items(mboxname))
            newuidl = set(loaduidl(mboxname, mboxconf))
            olduidl = data.get(mboxname, set())
            if newuidl != olduidl:
                changed = True
                newuids = newuidl - olduidl
                numnew = len(newuids)
                if numnew > 0:
                    #summary.append('%s: %s' % (mboxname, numnew))
                    print('Mailbox [%s]: %s new messages(s)' % (mboxname, numnew))
                data[mboxname] = newuidl
    except Exception as ex:
        #os.system('notify-send -i dialog-error %s "%s"' % (title, ex))
        print('Error: %s' % (ex), file=sys.stderr)
        sys.exit()

    if changed:
        with open(datafile, 'wb') as f:
            pickle.dump(data, f)
        #if summary != '':
        #    os.system('notify-send -i dialog-information %s "%s"' % (title, ', '.join(summary)))
    else:
        print('No new messages')

if __name__ == '__main__':
    main()
