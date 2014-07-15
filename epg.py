#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import vcrui
from datetime import datetime, timedelta
import subprocess
import threading
import sys
import traceback
import xml.etree.ElementTree as ET
import pickle

RECORD_BUFFER_MINUTES = 5
CRON_BUFFER_MINUTES = 2
EPG_MAX_TITLE_LENGTH = 35
EPG_TITLE_LANGUAGES = ['de','DEU']
EPG_CACHE_FILENAME = 'programme.pkl'
EPG_CACHE_MAX_AGE_DAYS = 2
TEXT_LIVERECORD_SUCCESS = "\"%s\" wird jetzt vielleicht live aufgezeichnet."
TEXT_LIVERECORD_FAILURE = "Live Aufzeichnung konnte nicht gestartet werden."
TEXT_SCHEDULE_SUCCESS = "\"%s\" wurde zur Aufnahme eingeplant."
TEXT_SCHEDULE_FAILURE = "Sendung konnte nicht zur Aufnahme eingeplant werden."
TEXT_SCHEDULE_PAST = "Sendung schon vorbei."
TEXT_EPG_UPDATING = "Bitte warten. Aktuelle Programminformationen werden geholt..."
TEXT_EPG_NOINFO = "Keine Programminformationen verfügbar."
TEXT_EPG_NOTITLE = 'UNKNOWN'
TEXT_EPG_TOCHANNELOVERVIEW = "zur Senderwahl"
TEXT_EPG_LISTALLCHANNELS = "alle Sender"


EPGDataEventType = wx.NewEventType()
EPG_DATA_EVENT = wx.PyEventBinder(EPGDataEventType, 1)
class EPGDataEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, status=None, data=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.status = status
        self.data = data

class TitlePanel ( vcrui.TitlePanel ):
  def __init__( self, parent ):
    vcrui.TitlePanel.__init__(self,parent)
    
  def SetChannelName(self, channelName):
    self.channelName = channelName
    
  def SetShow(self, show):
    self.show = show
    title = show['title']
    if EPG_MAX_TITLE_LENGTH > 0 and len(title) > EPG_MAX_TITLE_LENGTH:
      title = title[:EPG_MAX_TITLE_LENGTH]+'...'
    self.m_titleLabel.SetLabel(title.replace('&', '&&'))
    self.m_startLabel.SetLabel(show['start'].strftime('%a, %d. %b. %H:%M')) # TODO: eigenes label für tag, separator für "von... bis..."
    self.m_stopLabel.SetLabel(show['stop'].strftime('%H:%M'))
    
  def onSheduleRecordButtonClick( self, event ):
    now = datetime.now()
    start = self.show['start']
    stop = self.show['stop']
    if RECORD_BUFFER_MINUTES != 0:
      start = start - timedelta(minutes=RECORD_BUFFER_MINUTES)
      stop = stop + timedelta(minutes=RECORD_BUFFER_MINUTES)
    channelName = self.channelName
    title = self.show['title']
    if start > now + timedelta(minutes=CRON_BUFFER_MINUTES):
      startMinute = start.minute
      startHour = start.hour
      startDay = start.day
      startMonth = start.month
      startYear = start.day 
      weekday = ""
      length = stop-start
      args = map(str,['tv-schedule-record',startMinute, startHour, startDay, startMonth, startYear, weekday, length, channelName, title.encode('utf-8')])
      try:
        returncode = subprocess.call(args)
      except e:
        returncode = -1
      if returncode == 0:
        wx.MessageDialog(self, TEXT_SCHEDULE_SUCCESS%(title), "", wx.OK | wx.ICON_INFORMATION).ShowModal()
      else:
        wx.MessageDialog(self, TEXT_SCHEDULE_FAILURE, "", wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    elif stop > now:
      length = stop-now
      args = map(str,['screen', '-m', '-d', 'tv-record', channelName, title.encode('utf-8'), length])
      try:
        returncode = subprocess.call(args)
      except e:
        returncode = -1
      if returncode == 0:
        wx.MessageDialog(self, TEXT_LIVERECORD_SUCCESS%(title), "", wx.OK | wx.ICON_INFORMATION).ShowModal()
      else:
        wx.MessageDialog(self, TEXT_SCHEDULE_FAILURE, "", wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    else:
      wx.MessageDialog(self, TEXT_SCHEDULE_PAST, "", wx.OK | wx.ICON_EXCLAMATION).ShowModal()

class MainFrame ( vcrui.MainFrame ):
  def __init__(self,parent):
    vcrui.MainFrame.__init__(self,parent)
    backButton = wx.Button( self.m_headline, wx.ID_ANY, TEXT_EPG_TOCHANNELOVERVIEW, wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_headline.GetSizer().Add(backButton, 0, wx.ALL)
    backButton.Bind( wx.EVT_BUTTON, lambda event: self.listChannels() )
    self.Bind(EPG_DATA_EVENT, self.onEPGData)
    self.Layout()
    
  def addChannelSelectButton(self, channelName, channelID, parent):
    button = wx.Button( parent, wx.ID_ANY, channelName, wx.DefaultPosition, wx.DefaultSize, 0 )
    parent.GetSizer().Add( button, 0, wx.ALL|wx.EXPAND, 5 )
    button.Bind( wx.EVT_BUTTON, lambda event: self.onChannelSelectButtonClick(channelName, channelID ) )
    
  def onChannelSelectButtonClick( self, channelName, channelID ):
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.m_scrolledWindow.GetSizer().Add(wx.StaticText(self.m_scrolledWindow, wx.ID_ANY, TEXT_EPG_UPDATING), 0, wx.ALL|wx.EXPAND)
    
    self.m_gauge = wx.Gauge( self.m_scrolledWindow, wx.ID_ANY, 1000, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
    self.m_gauge.SetValue( 0 ) 
    self.m_scrolledWindow.GetSizer().Add( self.m_gauge, 0, wx.ALL|wx.EXPAND )
    self.Layout()
    wx.Yield()

    # remember which channel was chosen, then read epg data in background
    self._selectedChannelName = channelName 
    self._selectedChannelID = channelID
    self.readProgrammeData(channelName, channelID)
  
  def onEPGData(self, evt):
    if evt.status:
      self.m_gauge.SetValue(10+ int(990.0/(1.0+2**(-float(evt.status)/200.0+10.0))) ) # fake status progress
    if evt.data:
      self.parseProgrammeData(evt.data)
  
  def onProgrammeDataReady(self, programs):
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.addChannel(programs, self._selectedChannelName, self._selectedChannelID)
    self.Layout()
    
  def addChannel(self, programs, channelName, channelID, forceDisplay=True):
    #debugStart = datetime.now()
    channelID = "%s.dvb.guide"%channelID # TODO: move all instances of this conversion into separate function
    if channelID in programs or forceDisplay:
      channelPanel = vcrui.ChannelPanel(self.m_scrolledWindow)
      channelPanel.m_channelNameLabel.SetLabel(channelName)
      self.m_scrolledWindow.GetSizer().Add(channelPanel, 0, wx.ALL|wx.EXPAND)
    if channelID not in programs:
      if forceDisplay:
        channelPanel.GetSizer().Add(wx.StaticText(channelPanel, wx.ID_ANY, TEXT_EPG_NOINFO), 0, wx.ALL|wx.EXPAND)
    else:
      now = datetime.now()
      for show in programs[channelID]: #programs[channelID] should be pre-sorted
        if show['stop'] > now:
          titlePanel = TitlePanel(channelPanel)
          titlePanel.SetShow(show)
          titlePanel.SetChannelName(channelName)
          channelPanel.GetSizer().Add(titlePanel, 0, wx.ALL|wx.EXPAND)
    #sys.stderr.write('generation of showlist for channel took %s\n'%(str(datetime.now() - debugStart)))

  def loadProgrammeDataFromCache(self):
    try:
      cache = open(EPG_CACHE_FILENAME, 'rb')
      programs = pickle.load(cache)
      # remove shows which are already over from cache
      now = datetime.now()
      for channel in programs.keys():
        shows = [show for show in programs[channel] if show['stop'] > now]
        if not shows:
          del programs[channel]
        else:
          programs[channel] = shows
      cache.close()
    except:
      programs = dict() # cache unavailable, use empty dict
    return programs
    
  def readProgrammeData(self, channelName, channelID): # TODO: diese funktionen von GUI trennen
    programs = self.loadProgrammeDataFromCache()
    channelID = "%s.dvb.guide"%channelID
    if channelID in programs \
    and programs[channelID][0]['start'] > datetime.today() - timedelta(days=EPG_CACHE_MAX_AGE_DAYS):
      self.onProgrammeDataReady(programs) # use cache if requested channel information is recent enough
      return
      
    try:
      sub = subprocess.Popen(["tv-grab-xmltv", channelName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      def readProgrammeDataStatus():
        statusstring = ""
        while sub.poll() is None:
          statusbytes = sub.stderr.read(64)
          if statusbytes:
            statusstring += statusbytes
            statuses = statusstring.split(':')
            if len(statuses) > 2:
              statusstring = ""
              status = statuses[1]
              info = status.split(',')
              packetsstring = info[0].strip()
              packets = int(packetsstring.split(' ')[0])
              evt = EPGDataEvent(EPGDataEventType, -1, status=packets)
              wx.PostEvent(self, evt)
      def readProgrammeDataXML():
        xmlepgdata = sub.stdout.read()
        sub.wait()
        if sub.returncode != 0:
          raise RuntimeError("Abnormal script termination")
        evt = EPGDataEvent(EPGDataEventType, -1, data=xmlepgdata)
        wx.PostEvent(self, evt)
          
      backgroundStatusReader = threading.Thread(target=readProgrammeDataStatus)
      backgroundStatusReader.start() # falls sub zu schnell lösläuft, kann es hier einen deadlock mit race-condidion geben
      backgroundDataReader = threading.Thread(target=readProgrammeDataXML)
      backgroundDataReader.start()
      
    except:
      sys.stderr.write(traceback.format_exc())
      wx.MessageDialog(self, str(sys.exc_info()[0].__name__)+" "+str(sys.exc_info()[1]), "Unexpected error during subscript execution", wx.OK | wx.ICON_EXCLAMATION).ShowModal()
      
  def parseProgrammeData(self, xmlepgdata):
    programs = self.loadProgrammeDataFromCache()
    try:
      transponderChannels = []
      #tree = ET.parse('program.xml')
      #root = tree.getroot()
      root = ET.fromstring(xmlepgdata)
      for programme in root.iter('programme'):
        sChannel = programme.get('channel')
        sTitle = TEXT_EPG_NOTITLE
        #sys.stderr.write('received programme without title - check language filter\n')
        for title in programme.findall('title'):
          titleLang = title.get('lang',EPG_TITLE_LANGUAGES[0])
          if titleLang in EPG_TITLE_LANGUAGES:
            sTitle = title.text
        
        # these ignore timezone information
        dtStart = datetime.strptime(programme.get('start').split(' ')[0], '%Y%m%d%H%M%S')
        dtStop = datetime.strptime(programme.get('stop').split(' ')[0], '%Y%m%d%H%M%S')
        show = {'start':dtStart, 'stop':dtStop, 'title':sTitle}
        if sChannel not in transponderChannels:
          transponderChannels.append(sChannel)
          programs[sChannel] = [show] # purge cached, probabaly old information by overwriting
        else:
          if sChannel not in programs:
            programs[sChannel] = [show]
          else:
            programs[sChannel].append(show)
          
      for channelID in programs.keys():
        programs[channelID].sort(key=lambda x:x['start'])

    except:
      wx.MessageDialog(self, str(sys.exc_info()[0].__name__)+" "+str(sys.exc_info()[1]), "Unexpected error during parsing", wx.OK | wx.ICON_EXCLAMATION).ShowModal()
          
    # TODO : surround this with try
    cache = open(EPG_CACHE_FILENAME, 'wb')
    pickle.dump(programs, cache)
    cache.close()
    
    self.onProgrammeDataReady(programs)

    
  def addListAllChannelsButton(self, parent):
    button = wx.Button( parent, wx.ID_ANY, TEXT_EPG_LISTALLCHANNELS, wx.DefaultPosition, wx.DefaultSize, 0 )
    parent.GetSizer().Add( button, 0, wx.ALL|wx.EXPAND, 5 )
    button.Bind( wx.EVT_BUTTON, lambda event: self.addAllChannels() )

  def listChannels(self):
    self.m_scrolledWindow.GetSizer().Clear(True)
    channelListPanel = vcrui.ChannelListPanel(self.m_scrolledWindow)
    for line in sorted([line.strip() for line in open('channels.conf')]): # TODO: try/catch for file-operation and possible encoding issues
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        self.addChannelSelectButton(split[0], split[8], channelListPanel)
    self.addListAllChannelsButton(channelListPanel)
    self.m_scrolledWindow.GetSizer().Add(channelListPanel, 0, wx.ALL|wx.EXPAND)
    self.Layout()
        
  def addAllChannels(self):
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.m_scrolledWindow.GetSizer().SetOrientation(wx.HORIZONTAL)
    programs = self.readProgrammeData(None,None) # TODO: this is now defunct
    for line in sorted([line.strip() for line in open('channels.conf')]):
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        self.addChannel(programs, split[0], split[8], forceDisplay=False, showBackButton=False)
    self.Layout()

if __name__ == "__main__":
  app = wx.App(False)
  frame = MainFrame(None)
  frame.Maximize(True)
  frame.listChannels()
  frame.Show()
  app.MainLoop()
