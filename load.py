import xml.etree.ElementTree as ET
import os
import sys
import getopt
from datetime import datetime
import signal
import time
import subprocess

cwd = os.getcwd()
JMXfile = cwd + '/LOAD.jmx'
logPath = cwd + '/logs/' + str(datetime.now()).replace(" ", ".").replace(":", ".") + '.jtl'
# jmeterStartStr = '/home/ubuntu/apache-jmeter-3.1/bin/jmeter ' + '-n -t ' + JMXfile + ' -l ' + logPath

def startJmeterTest(duration):
    p = subprocess.Popen(['bash', '/home/ubuntu/apache-jmeter-3.1/bin/jmeter', '-n', '-t', JMXfile, '-l', logPath])
    pid = p.pid
    time.sleep(duration)
    try:
        os.killpg(os.getpgid(pid), signal.SIGINT)
    except: print "Test completed"
    exit()


def changeAttrib(elem, urlParts):
    attributes = elem.attrib.values()
    if 'playlist' in attributes:
        for el in elem.iter('stringProp'):
            if 'HTTPSampler.domain' in el.attrib.values():
                el.text = urlParts[2]
            elif 'HTTPSampler.path' in el.attrib.values():
                el.text = '/'.join(urlParts[3:])
            elif 'HTTPSampler.protocol' in el.attrib.values():
                el.text = urlParts[0].replace(':', "")
    elif 'chunk' in attributes:
        for el in elem.iter('stringProp'):
            if 'HTTPSampler.domain' in el.attrib.values():
                el.text = urlParts[2]
            elif 'HTTPSampler.path' in el.attrib.values():
                tmp = urlParts[:]
                del tmp[-1]
                el.text = '/'.join(tmp[3:]) + '/chunklist_${chunk}.m3u8'
            elif 'HTTPSampler.protocol' in el.attrib.values():
                el.text = urlParts[0].replace(':', "")
    elif 'stream' in attributes:
        for el in elem.iter('stringProp'):
            if 'HTTPSampler.domain' in el.attrib.values():
                el.text = urlParts[2]
            elif 'HTTPSampler.path' in el.attrib.values():
                tmp = urlParts[:]
                del tmp[-1]
                el.text = '/'.join(tmp[3:]) + '/media_${stream}.ts'
            elif 'HTTPSampler.protocol' in el.attrib.values():
                el.text = urlParts[0].replace(':', "")

def updateJMX(url):
    urlParts = url.split('/')
    tree = ET.parse(JMXfile)
    root = tree.getroot()
    for elem in root.iter('HTTPSamplerProxy'):
        changeAttrib(elem, urlParts)
    try:
        tree.write(JMXfile, xml_declaration=True)
    except: print 'JMX NOT updated'


def get_cmd_args(args):
    duration = 900
    try:
        opts, args = getopt.getopt(args, 'u:t:', ['url=', 'time='])
    except getopt.GetoptError:
        print 'test.py -u <url>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-u', '--url'):
            url = arg
        elif opt in ('-t', '--time'):
            duration = int(arg)
        else:
            print 'No arguments found'
    updateJMX(url)
    startJmeterTest(duration)

if __name__ == '__main__':
    get_cmd_args(sys.argv[1:])