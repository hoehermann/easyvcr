# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"EPG", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_headline = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer61 = wx.BoxSizer( wx.HORIZONTAL )
		
		
		self.m_headline.SetSizer( bSizer61 )
		self.m_headline.Layout()
		bSizer61.Fit( self.m_headline )
		bSizer5.Add( self.m_headline, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_scrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow.SetScrollRate( 25, 25 )
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		
		self.m_scrolledWindow.SetSizer( bSizer6 )
		self.m_scrolledWindow.Layout()
		bSizer6.Fit( self.m_scrolledWindow )
		bSizer5.Add( self.m_scrolledWindow, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer5 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class ChannelPanel
###########################################################################

class ChannelPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.VSCROLL )
		
		channelPanelSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.m_channelNameLabel = wx.StaticText( self, wx.ID_ANY, u"ChannelName", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_channelNameLabel.Wrap( -1 )
		channelPanelSizer.Add( self.m_channelNameLabel, 0, wx.ALL, 5 )
		
		
		self.SetSizer( channelPanelSizer )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class TitlePanel
###########################################################################

class TitlePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_titleLabel = wx.StaticText( self, wx.ID_ANY, u"Title", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_titleLabel.Wrap( -1 )
		bSizer3.Add( self.m_titleLabel, 0, wx.ALL, 5 )
		
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_startLabel = wx.StaticText( self, wx.ID_ANY, u"start", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_startLabel.Wrap( -1 )
		bSizer4.Add( self.m_startLabel, 0, wx.ALL, 5 )
		
		self.m_stopLabel = wx.StaticText( self, wx.ID_ANY, u"stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stopLabel.Wrap( -1 )
		bSizer4.Add( self.m_stopLabel, 0, wx.ALL, 5 )
		
		self.m_sheduleRecordButton = wx.Button( self, wx.ID_ANY, u"Aufzeichnen", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_sheduleRecordButton, 0, wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer3 )
		self.Layout()
		
		# Connect Events
		self.m_sheduleRecordButton.Bind( wx.EVT_BUTTON, self.onSheduleRecordButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def onSheduleRecordButtonClick( self, event ):
		event.Skip()
	

###########################################################################
## Class ChannelListPanel
###########################################################################

class ChannelListPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		gSizer1 = wx.GridSizer( 0, 3, 0, 0 )
		
		
		self.SetSizer( gSizer1 )
		self.Layout()
	
	def __del__( self ):
		pass
	

