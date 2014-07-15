#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import momsui
from momsui import MainFrame, ChannelPanel, TitlePanel, ChannelListPanel
from datetime import datetime, timedelta
import subprocess
import sys
import xml.etree.ElementTree as ET

RECORD_BUFFER_MINUTES = 5
EPG_MAX_TITLE_LENGTH = 25
EPG_TITLE_LANGUAGES = ['de','DEU']
TEXT_SCHEDULE_SUCCESS = "\"%s\" wurde zur Aufnahme eingeplant."
TEXT_SCHEDULE_FAILURE = "Ein Problem ist aufgetreten."
TEXT_EPG_UPDATING = "Bitte warten. Aktuelle Programminformationen werden geholt..."
TEXT_EPG_NOINFO = "No information available"
TEXT_EPG_NOTITLE = 'UNKNOWN'

class TitlePanel ( momsui.TitlePanel ):
  def __init__( self, parent ):
    momsui.TitlePanel.__init__(self,parent)
    
  def SetChannelName(self, channelName):
    self.channelName = channelName
    
  def SetShow(self, show):
    self.show = show
    title = show['title']
    if True and len(title) > EPG_MAX_TITLE_LENGTH:
      title = title[:EPG_MAX_TITLE_LENGTH]+'...'
    self.m_titleLabel.SetLabel(title)
    self.m_startLabel.SetLabel(show['start'].strftime('%a %H:%M'))
    self.m_stopLabel.SetLabel(show['stop'].strftime('%H:%M'))
    
  def onSheduleRecordButtonClick( self, event ):
    start = self.show['start']
    stop = self.show['stop']
    if RECORD_BUFFER_MINUTES != 0:
      start = start - timedelta(minutes=RECORD_BUFFER_MINUTES)
      stop = stop + timedelta(minutes=RECORD_BUFFER_MINUTES)
    startMinute = start.minute
    startHour = start.hour
    startDay = start.day
    startMonth = start.month
    startYear = start.day 
    weekday = ""
    length = str(stop-start)
    channelName = self.channelName
    title = self.show['title']
    args = map(str,['tv-schedule-record',startMinute, startHour, startDay, startMonth, startYear, weekday, length, channelName, title.encode('utf-8')])
    #print args
    try:
      returncode = subprocess.call(args)
    except e:
      returncode = 255
    if returncode == 0:
      wx.MessageDialog(self, TEXT_SCHEDULE_SUCCESS%(title), "", wx.OK | wx.ICON_INFORMATION).ShowModal()
    else:
      wx.MessageDialog(self, TEXT_SCHEDULE_FAILURE, "", wx.OK | wx.ICON_EXCLAMATION).ShowModal()

class MainFrame ( momsui.MainFrame ):
  def __init__(self,parent):
    momsui.MainFrame.__init__(self,parent)
    
  def addChannelSelectButton(self, channelName, channelID, parent):
    button = wx.Button( parent, wx.ID_ANY, channelName, wx.DefaultPosition, wx.DefaultSize, 0 )
    parent.GetSizer().Add( button, 0, wx.ALL|wx.EXPAND, 5 )
    button.Bind( wx.EVT_BUTTON, lambda event: self.onChannelSelectButtonClick(channelName, channelID ) )
    
  def onChannelSelectButtonClick( self, channelName, channelID ):
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.m_scrolledWindow.GetSizer().Add(wx.StaticText(self.m_scrolledWindow, wx.ID_ANY, TEXT_EPG_UPDATING), 0, wx.ALL|wx.EXPAND)
    self.Layout()
    wx.Yield()
    self.m_scrolledWindow.GetSizer().Clear(True)
    programs = self.readProgrammeData(channelName)
    self.addChannel(programs, channelName, channelID, True)
    self.Layout()
    
  def addChannel(self, programs, channelName, channelID, forceDisplay=False ):
    channelID = "%s.dvb.guide"%channelID
    if channelID in programs or forceDisplay:
      channelPanel = ChannelPanel(self.m_scrolledWindow)
      channelPanel.m_channelNameLabel.SetLabel(channelName)
      self.m_scrolledWindow.GetSizer().Add(channelPanel, 0, wx.ALL|wx.EXPAND)
    if channelID not in programs:
      if forceDisplay:
        channelPanel.GetSizer().Add(wx.StaticText(channelPanel, wx.ID_ANY, TEXT_EPG_NOINFO), 0, wx.ALL|wx.EXPAND)
    else:
      now = datetime.now()
      for show in sorted(programs[channelID],key=lambda x:x['start']):
        if show['start'] > now:
          titlePanel = TitlePanel(channelPanel)
          titlePanel.SetShow(show)
          titlePanel.SetChannelName(channelName)
          channelPanel.GetSizer().Add(titlePanel, 0, wx.ALL|wx.EXPAND)

  def readProgrammeData(self, channelName):
    programs = dict()
    sub = subprocess.Popen(["tv-grab-xmltv", channelName], stdout=subprocess.PIPE)
    xmlepgdata = sub.communicate()[0]
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
      if sChannel not in programs:
        programs[sChannel] = [show]
      else:
        programs[sChannel].append(show)
    return programs

  def listChannels(self):
    self.m_scrolledWindow.GetSizer().Clear(True)
    channelListPanel = ChannelListPanel(self)
    for line in [line.strip() for line in open('channels.conf')]:
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        self.addChannelSelectButton(split[0], split[8], channelListPanel)
    self.m_scrolledWindow.GetSizer().Add(channelListPanel, 0, wx.ALL|wx.EXPAND)
    self.Layout()
        
  def addAllChannels(self): # for debug purposes only
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.m_scrolledWindow.GetSizer().SetOrientation(wx.HORIZONTAL)
    programs = self.readProgrammeData("Tele 5")
    for line in [line.strip() for line in open('channels.conf')]:
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        self.addChannel(programs, split[0], split[8])
    self.Layout()

if __name__ == "__main__":
  app = wx.App(False)
  frame = MainFrame(None)
  frame.Maximize(True)
  frame.listChannels()
  #frame.addAllChannels()
  frame.Show()
  app.MainLoop()
