#!/usr/bin/python
#-*- coding: utf-8 -*-


#  2do:


#
import ctypes
import os
import stat
import fnmatch
import platform
import sys
import traceback
#import msvcrt
import time
import colorama
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer
import struct
from socket import *
from optparse import OptionParser

#
#from hwdef import *

#
OS_TYPE = 'L'

CDPFILENAME = 'default_test.cdp'
CDP_STRUCTURE_LENGTH = 196  #common length

SILENT_TIME = 0.001 

# LOCAL_IP = '192.168.2.233'
LOCAL_IP = '172.16.12.12'
# LOCAL_IP = '127.0.0.1'
# LOCAL_IP = '192.168.1.13'

DEST_GIP = '235.0.0.1'
DEST_GPORT = 25911

class _stADT_1553_CDP(ctypes.Structure):
    _fields_ = [('NextPtr',ctypes.c_uint),
                ('BMCount',ctypes.c_uint),
                ('APIinfo',ctypes.c_uint),
                ('Rsvd1',ctypes.c_uint),
                ('Rsvd2',ctypes.c_uint),
                ('MaskValue',ctypes.c_uint),
                ('MaskCompare',ctypes.c_uint),
                ('CDPControlWord',ctypes.c_uint),
                ('CDPStatusWord',ctypes.c_uint),
                ('TimeHigh',ctypes.c_uint),
                ('TimeLow',ctypes.c_uint),
                ('IMGap',ctypes.c_uint),
                ('Rsvd3',ctypes.c_uint),
                ('CMD1info',ctypes.c_uint),
                ('CMD2info',ctypes.c_uint),
                ('STS1info',ctypes.c_uint),
                ('STS2info',ctypes.c_uint),
                ('DATAinfo',ctypes.c_uint * 32)];

    def __str__(self):
        return ''
#
def kbpress():
    x = msvcrt.kbhit()
    if x:
        ret = ord(msvcrt.getch())
    else:
        ret = 0
    return ret



#
def decideOS():
    global OS_TYPE
    print('\n\nos:\t\t\t\t' + platform.platform())
    print('script:\t\t\t\tPython ' + platform.python_version())

    sysstr = platform.system()
    if(sysstr == "Windows"):
        # print ("Windows tasks")
        OS_TYPE = 'W'
        return 0
    elif(sysstr == "Linux"):
        # print ("Call Linux tasks")
        OS_TYPE = 'L'
        return 0
    else:
        print("where r u?")
        return -1




def main():
    usagestr = "Usage: %prog [options] [cdp file name] ."  
    parser = OptionParser(usage = usagestr)
    parser.add_option('-r', '--rewind', action = "store_true", \
                                        dest = 'isrewind', \
                                        default = False, \
                                        help = 'resend cdp blocks over and over.')
    parser.add_option('-l', '--local_ip', action = 'store', \
                                        type = 'string', \
                                        dest = 'localip',\
                                        default = LOCAL_IP, \
                                        help = 'local ip address to send cdp blocks with, default is %s.' % LOCAL_IP)
    parser.add_option('-f', '--filename', action = 'store', \
                                        type = 'string', \
                                        dest = 'filename',\
                                        default = CDPFILENAME, \
                                        help = 'cdp files to be sent, default is %s.' % CDPFILENAME)
    parser.add_option('-d', '--dest_ip', action = 'store', \
                                        type = 'string', \
                                        dest = 'destgip',\
                                        default = DEST_GIP, \
                                        help = 'destination group ip address, default is %s .' % DEST_GIP)
    parser.add_option('-p', '--dest_port', action = 'store', \
                                        type = 'int', \
                                        dest = 'destgport',\
                                        default = DEST_GPORT, \
                                        help = 'destination port of group ip address, default is %d .' % DEST_GPORT)
    parser.add_option('-i', '--interval', action = 'store', \
                                        type = 'float', \
                                        dest = 'interval',\
                                        default = SILENT_TIME, \
                                        help = 'interval(seconds) between tow cdp blocks, default is %fs.' % SILENT_TIME)
    
    options, args = parser.parse_args() 
    # parser.print_help()
    # print options.localip
    # print args
    # sys.exit()
 

    decideOS()
    colorama.init(autoreset = True)  
    
    
    try:

        #print gethostbyname_ex(gethostname())
        #print gethostbyname(gethostname())  

        cdpfile = open(options.filename, 'rb')
        cdpfilelength = os.path.getsize(options.filename)

        s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # print options.localip
        s.bind((options.localip, 0))
        #ttl_bin = struct.pack('@i', 255)
        #s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl_bin)
        #s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton('235.0.0.1') + inet_aton('192.168.12.12'))
        
        lazycnt = 1
        c = 0
        
        print colorama.Fore.LIGHTGREEN_EX + '\n\nrewind mode:\t\t\tYES' if options.isrewind else colorama.Fore.LIGHTGREEN_EX + '\n\nrewind mode: NO.'
        print colorama.Fore.LIGHTGREEN_EX + 'interval:\t\t\t%f second(s)' % (options.interval)
        print colorama.Fore.LIGHTGREEN_EX + 'source local ip:\t\t%s' % (options.localip)
        print colorama.Fore.LIGHTGREEN_EX + 'destination group ip:\t\t%s' % (options.destgip)
        print colorama.Fore.LIGHTGREEN_EX + 'port of destination group ip:\t%s' % (options.destgport)

        print colorama.Fore.LIGHTGREEN_EX + '\n\nusing file:\t\t\t%s' % (options.filename)
        print colorama.Fore.LIGHTGREEN_EX + '\t\t\t\t%d bytes, %d CDP blocks' % (cdpfilelength, cdpfilelength/CDP_STRUCTURE_LENGTH)
        
        # print colorama.Fore.LIGHTGREEN_EX + '\n>press \'q\' to exit.\n\n'                                  
        print colorama.Fore.LIGHTBLUE_EX + '\n>press \'Ctrl-C\' to exit\n\n'                                  
        
        # cdpcnt = cdpfile.__sizeof__() / CDP_STRUCTURE_LENGTH

        while(True): #means 'q'
            # c = kbpress();
            cdpfile.seek(lazycnt * CDP_STRUCTURE_LENGTH)
            cdpdata = cdpfile.read(CDP_STRUCTURE_LENGTH)
            #print len(cdpdata)
            if len(cdpdata) < 196:
                if options.isrewind:
                    lazycnt = 0
                    print colorama.Fore.LIGHTGREEN_EX + '\n!rewind!' 
                else:    
                    raise EOFError
            s.sendto(cdpdata, (options.destgip, options.destgport)) 
            lazycnt+=1

            time.sleep(options.interval)
            
            print colorama.Fore.LIGHTRED_EX + "\r>>> %d (%.3f%%)" % (lazycnt, lazycnt*CDP_STRUCTURE_LENGTH*100./cdpfilelength),
            print colorama.Fore.LIGHTGREEN_EX + " cdp blocks sent...",
            pass

        print colorama.Fore.GREEN + '\n>normal out'
    
    #except BaseException :
    
    except EOFError:      
        print colorama.Fore.GREEN + '\n>sent all cdps.'
        print colorama.Fore.GREEN + '\n>normal out'      
    
    except KeyboardInterrupt:
        print colorama.Fore.GREEN + '\n\n>stopped by user'
        print colorama.Fore.GREEN + '>normal out'
    
    except:
        traceback.print_exc()
        si = sys.exc_info()
        print colorama.Fore.RED + "line: %d\nError:%s" % (si[2].tb_lineno, si[1])
        print colorama.Fore.RED + '\n>exp out'
        sys.exit()
    

    finally:
        cdpfile.close()
        sys.exit()





if __name__ == '__main__':
    main()




