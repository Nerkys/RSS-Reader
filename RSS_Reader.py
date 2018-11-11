import feedparser
import os
import unidecode
import wx
import wx.html2 as webview
import re
import sqlite3
import sys
 
from ObjectListView import ObjectListView, ColumnDefn


conn = sqlite3.connect("database_rasp.db")
cursor = conn.cursor()


def insert_sth_smw( name, link, category):

	sql = "INSERT INTO pages VALUES (?,?,?)"
	cursor.executemany(sql, [(name, link, category)])
	conn.commit()

def select_sth():

	sql = "SELECT name, link, category FROM pages"
	cursor.execute(sql)
	return cursor.fetchall()

#cursor.execute("""CREATE TABLE pages (name text, link text,category text)""")

class RSS(object):
	def __init__(self, title, link, website, summary, all_data):
		"""Constructor"""
		self.title = title
		self.link = link
		self.all_data = all_data
		self.website = website
		self.summary = summary
 

class RssPanel(wx.Panel):

	def __init__(self, parent):

		wx.Panel.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		self.data = []
 
		lbl = wx.StaticText(self, label="Feed URL:")
		lbl2 = wx.StaticText(self, label="Search by key words in title:")
		lbl3 = wx.StaticText(self, label="Search by key words in text:")
		self.rssSearch = wx.TextCtrl(self, value="")
		self.rssSearch2 = wx.TextCtrl(self, value="")
		self.rssUrlTxt = wx.TextCtrl(self, value="https://www.newsinlevels.com/feed/")
		
		searchBtn = wx.Button(self, label="Get Search")
		searchBtn.Bind(wx.EVT_BUTTON, self.searchTitle)
		searchBtn2 = wx.Button(self, label="Get Search")
		searchBtn2.Bind(wx.EVT_BUTTON, self.searchSummary)
		urlBtn = wx.Button(self, label="Get Feed")
		urlBtn.Bind(wx.EVT_BUTTON, self.get_data)
 
		self.rssOlv = ObjectListView(self, 
									 style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.rssOlv.SetEmptyListMsg("No data")
		self.rssOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
		self.rssOlv.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click)
		self.summaryTxt = webview.WebView.New(self)

		self.searchOlv = ObjectListView(self, 
									 style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.searchOlv.SetEmptyListMsg("No results")
		self.searchOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select1)
		self.searchOlv.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click1)

		self.searchOlv2 = ObjectListView(self, 
									 style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.searchOlv2.SetEmptyListMsg("No results")
		self.searchOlv2.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select2)
		self.searchOlv2.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click2)
 
		self.wv = webview.WebView.New(self)
		
		self.listoffeeds = []

		
		# add sizers
		
		toolbar2 = wx.ToolBar(self)
		qtool = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('greenplus.png'))
		qtool2 = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('redplus.png'))
		qtool3 = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('notif.png'))

		toolbar2.Realize()

		
		toolbar2.Bind(wx.EVT_TOOL, self.enterCategory, qtool)
		toolbar2.Bind(wx.EVT_TOOL, self.save_page, qtool2)
		toolbar2.Bind(wx.EVT_TOOL, self.new_window, qtool3)

		rowSizer = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer.Add(lbl, 0, wx.ALL, 5)
		rowSizer.Add(self.rssUrlTxt, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer.Add(urlBtn, 0, wx.ALL, 5)
 
		vSizer = wx.BoxSizer(wx.VERTICAL)
		vSizer.Add(self.rssOlv, 1, wx.EXPAND|wx.ALL, 5)
		vSizer.Add(self.summaryTxt, 1, wx.EXPAND|wx.ALL, 5)
		
		rowSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer1.Add(lbl2, 0, wx.ALL, 5)
		rowSizer1.Add(self.rssSearch, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer1.Add(searchBtn, 0, wx.ALL, 5)

		rowSizer3 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer3.Add(lbl3, 0, wx.ALL, 5)
		rowSizer3.Add(self.rssSearch2, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer3.Add(searchBtn2, 0, wx.ALL, 5)

		rowSizer4 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer4.Add(self.searchOlv, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer4.Add(self.searchOlv2, 1,  wx.EXPAND|wx.ALL, 5)

		dispSizer = wx.BoxSizer(wx.HORIZONTAL)
		dispSizer.Add(vSizer, 1, wx.EXPAND|wx.ALL, 5)
		
		dispSizer1 = wx.BoxSizer(wx.VERTICAL)
		dispSizer1.Add(self.wv, 2, wx.EXPAND|wx.ALL, 5)
		dispSizer1.Add(rowSizer4, 1, wx.EXPAND|wx.ALL, 5)


		rowSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer2.Add(dispSizer, 0, wx.EXPAND|wx.ALL, 5)
		rowSizer2.Add(dispSizer1, 1, wx.EXPAND|wx.ALL, 5)
		

		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(toolbar2, 0 , wx.RIGHT)
		mainSizer.Add(rowSizer, 0, wx.EXPAND)
		mainSizer.Add(rowSizer1, 0, wx.EXPAND)
		mainSizer.Add(rowSizer3, 0, wx.EXPAND)
		mainSizer.Add(rowSizer2, 1, wx.EXPAND|wx.ALL)
		
		self.SetSizer(mainSizer)
 
		self.update_display()
		

	def enterCategory(self, event):
		global category
		dlog=wx.TextEntryDialog(None,"Enter the category:")
		dlog.ShowModal()
		category=dlog.GetValue()
	#----------------------------------------------------------------------
		
	def new_window(self, event):
        # Окно с сохраненными ссылкамистраницы
		window = wx.Frame(None, -1, "All data")
		list_view = wx.ListCtrl(window, -1, style = wx.LC_REPORT) 
		

		list_view.InsertColumn(0, 'title', width = 100) 
		list_view.InsertColumn(1, 'link', wx.LIST_FORMAT_RIGHT, 100) 
		list_view.InsertColumn(2, 'category', wx.LIST_FORMAT_RIGHT, 100) 
		for i in select_sth(): 

			index = list_view.InsertStringItem(sys.maxsize, i[0]) 
			list_view.SetStringItem(index, 1, i[1]) 
			list_view.SetStringItem(index, 2, i[2])


		window.Show()

	#----------------------------------------------------------------------
	def save_page(self, event):
	
		obj = self.rssOlv.GetSelectedObject()
		name = obj.title
		link = obj.link
		insert_sth_smw( name, link, category)
	#----------------------------------------------------------------------
	def get_data(self, event):
		
		# Получить RSS feed и добавить на дисплей
		
		
		msg = "Processing feed..."
		busyDlg = wx.BusyInfo(msg)
		rss = self.rssUrlTxt.GetValue()
		feed = feedparser.parse(rss)
		website = feed["feed"]["title"]
		for key in feed["entries"]:
			title = unidecode.unidecode(key["title"])
			link = unidecode.unidecode(key["link"])
			summary = unidecode.unidecode(key["summary"])
			self.data.append(RSS(title, link, website, summary, key))
 
		busyDlg = None
		self.update_display()
	
	#----------------------------------------------------------------------
	def searchTitle(self, event):

		# Поиск по названию статьи
		search_list = []
		for key in self.data:
			title = key.title
			result = re.search('\s*%s' % self.rssSearch.GetValue(), title)
			if result != None:
				search_list.append(key)

		self.search_list = search_list
		self.update_display1()

	#----------------------------------------------------------------------
	def searchSummary(self, event):
        # Поиск по краткому содержанию статьи
		
		search_list1 = []
		for key in self.data:
			summary = key.summary
			result1 = re.search('\s*%s' % self.rssSearch2.GetValue(), summary)
			if result1 != None:
				search_list1.append(key)

		self.search_list1 = search_list1
		self.update_display2()

	#----------------------------------------------------------------------
	def on_double_click(self, event):
		
		# Загрузить выбранную ссылку в виджет браузера
		
		obj = self.rssOlv.GetSelectedObject()
		self.wv.LoadURL(obj.link)
	#----------------------------------------------------------------------
	def on_double_click1(self, event):
	
		obj = self.searchOlv.GetSelectedObject()
		self.wv.LoadURL(obj.link)
	#----------------------------------------------------------------------
	def on_double_click2(self, event):
		
		obj = self.searchOlv2.GetSelectedObject()
		self.wv.LoadURL(obj.link)
 
	#----------------------------------------------------------------------
	def on_select(self, event):
		
		# Загрузить ссылку в меню для краткого содержания
		
		base_path = os.path.dirname(os.path.abspath(__file__))        
		obj = self.rssOlv.GetSelectedObject()
		html = "<html><body>%s</body></html>" % obj.summary
		fname = "summary.html"
		full_path = os.path.join(base_path, fname)
		try:
			with open(full_path, "w") as fh:
				fh.write(html)
				print ("file:///" + full_path)
				self.summaryTxt.LoadURL("file:///" + full_path)
		except (OSError, IOError):
			print ("Error writing html summary")
	  #----------------------------------------------------------------------
	def on_select1(self, event):
		
		base_path = os.path.dirname(os.path.abspath(__file__))        
		obj = self.searchOlv.GetSelectedObject()
		html = "<html><body>%s</body></html>" % obj.summary
		fname = "summary.html"
		full_path = os.path.join(base_path, fname)
		try:
			with open(full_path, "w") as fh:
				fh.write(html)
				print ("file:///" + full_path)
				self.summaryTxt.LoadURL("file:///" + full_path)
		except (OSError, IOError):
			print ("Error writing html summary")
	#----------------------------------------------------------------------
	def on_select2(self, event):
	
		base_path = os.path.dirname(os.path.abspath(__file__))        
		obj = self.searchOlv2.GetSelectedObject()
		html = "<html><body>%s</body></html>" % obj.summary
		fname = "summary.html"
		full_path = os.path.join(base_path, fname)
		try:
			with open(full_path, "w") as fh:
				fh.write(html)
				print ("file:///" + full_path)
				self.summaryTxt.LoadURL("file:///" + full_path)
		except (OSError, IOError):
			print ("Error writing html summary")
	#----------------------------------------------------------------------
	def update_display(self):
		# Обновить RSS feed дисплей
		
		self.rssOlv.SetColumns([
			ColumnDefn("Title", "left", 200, "title"),
			ColumnDefn("Website", "left", 200, "website"),
			])
		self.rssOlv.SetObjects(self.data)

	#----------------------------------------------------------------------
	def update_display1(self):

		self.searchOlv.SetColumns([
			ColumnDefn("Title", "left", 200, "title"),
			ColumnDefn("Website", "left", 200, "website"),
			])
		self.searchOlv.SetObjects(self.search_list)
	#----------------------------------------------------------------------
	def update_display2(self):
		
		self.searchOlv2.SetColumns([
			ColumnDefn("Title", "left", 200, "title"),
			ColumnDefn("Website", "left", 200, "website"),
			])
		self.searchOlv2.SetObjects(self.search_list1)
		

class RssFrame(wx.Frame):
	
	def __init__(self):
		wx.Frame.__init__(self, None, title="RSS Reader", size=(1200,800))
		panel = RssPanel(self)
		self.Show()
 

if __name__ == "__main__":
	app = wx.App(False)
	frame = RssFrame()
	app.MainLoop()
