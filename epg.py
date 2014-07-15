#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import momsui
from momsui import MainFrame, ChannelPanel, TitlePanel
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

class TitlePanel ( momsui.TitlePanel ):
  def __init__( self, parent ):
    momsui.TitlePanel.__init__(self,parent)
    
  def SetChannelName(self, channelName):
    self.channelName = channelName
    
  def SetShow(self, show):
    self.show = show
    title = show['title']
    if True and len(title) > 25:
      title = title[:25]+'...'
    self.m_titleLabel.SetLabel(title)
    self.m_startLabel.SetLabel(show['start'].strftime('%a %H:%M'))
    self.m_stopLabel.SetLabel(show['stop'].strftime('%H:%M'))
    
  def onSheduleRecordButtonClick( self, event ):
    start = self.show['start']
    stop = self.show['stop']
    if True:
      start = start - timedelta(minutes=5)
      stop = stop + timedelta(minutes=5)
    startMinute = start.minute
    startHour = start.hour
    startDay = start.day
    startMonth = start.month
    startYear = start.day 
    weekday = ""
    length = str(stop-start)
    channelName = self.channelName
    title = self.show['title']
    print 'tv-shedule-record "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"'%(startMinute, startHour, startDay, startMonth, startYear, weekday, length, channelName, title)
    # 0 0 30 3 ? 2011  /command
    # 05 18 * * 1-4 /usr/local/bin/tv-record "Tele 5" "Voyager" "01:10:00"

class MainFrame ( momsui.MainFrame ):
  def __init__(self,parent):
    momsui.MainFrame.__init__(self,parent)
    
  def addChannelSelectButton(self, channelName, channelID):
    self.m_channelSelectButton = wx.Button( self.m_scrolledWindow, wx.ID_ANY, channelName, wx.DefaultPosition, wx.DefaultSize, 0 )
    self.m_scrolledWindow.GetSizer().Add( self.m_channelSelectButton, 0, wx.ALL|wx.EXPAND, 5 )
    self.m_channelSelectButton.Bind( wx.EVT_BUTTON, lambda event: self.onChannelSelectButtonClick(channelName, channelID ) )
    
  def onChannelSelectButtonClick( self, channelName, channelID ):
    self.m_scrolledWindow.GetSizer().Clear(True)
    programs = self.readProgrammeData()
    self.addChannel(programs, channelName, channelID)
    self.Layout()
    
  def addChannel(self, programs, channelName, channelID, forceDisplay=False ):
    channelID = "%s.dvb.guide"%channelID
    if channelID in programs or forceDisplay:
      channelPanel = ChannelPanel(self.m_scrolledWindow)
      channelPanel.m_channelNameLabel.SetLabel(channelName)
      self.m_scrolledWindow.GetSizer().Add(channelPanel)
    if channelID not in programs:
      if forceDisplay:
        channelPanel.GetSizer().Add(wx.StaticText(channelPanel, wx.ID_ANY, "No information available"), 0, wx.ALL|wx.EXPAND)
    else:
      for show in sorted(programs[channelID],key=lambda x:x['start']):
        titlePanel = TitlePanel(channelPanel)
        titlePanel.SetShow(show)
        titlePanel.SetChannelName(channelName)
        channelPanel.GetSizer().Add(titlePanel, 0, wx.ALL|wx.EXPAND)

  def readProgrammeData(self):
    programs = dict()
    tree = ET.parse('program.xml')
    root = tree.getroot()
    for programme in root.iter('programme'):
      sChannel = programme.get('channel')
      sTitle = 'UNKNOWN - Check language filter'
      for title in programme.findall('title'):
        titleLang = title.get('lang','de')
        if titleLang == 'de' or titleLang == 'DEU':
          sTitle = title.text
      
      dtStart = datetime.strptime(programme.get('start').split(' ')[0], '%Y%m%d%H%M%S')
      dtStop = datetime.strptime(programme.get('stop').split(' ')[0], '%Y%m%d%H%M%S')
      show = {'start':dtStart, 'stop':dtStop, 'title':sTitle}
      if sChannel not in programs:
        programs[sChannel] = [show]
      else:
        programs[sChannel].append(show)
    return programs

  def listChannels(self):
    for line in [line.strip() for line in open('channels.conf')]:
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        frame.addChannelSelectButton(split[0], split[8])
        
  def addAllChannels(self):
    self.m_scrolledWindow.GetSizer().Clear(True)
    self.m_scrolledWindow.GetSizer().SetOrientation(wx.HORIZONTAL)
    programs = self.readProgrammeData()
    for line in [line.strip() for line in open('channels.conf')]:
      if line[0] != '#' and line[0] != ';' :
        split = line.split(':')
        self.addChannel(programs, split[0], split[8])
    self.Layout()

if __name__ == "__main__":
  app = wx.App(False)
  frame = MainFrame(None)
  #frame.listChannels()
  frame.addAllChannels()
  frame.Show()
  app.MainLoop()
