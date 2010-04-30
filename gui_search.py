# -*- coding: utf8 -*-

import gtk, os, urllib, hashlib
from xl import trax, common, settings, playlist
from xml.etree import ElementTree


class MyPanel():
	def __init__(self, exaile):
		self.gui_create(exaile)
		self.events_connect()
		self.play = exaile.gui.main
		
	def unescape(self, s):
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&apos", "'")
		s = s.replace("&quot;", "\"")
		s = s.replace("&amp;", "&")
		return s
	
	def gui_create(self, exaile):
		self.vbox = gtk.VBox()
		self.searchLabel = gtk.Label('Поиск:')
		self.searchImage = gtk.Image()
		self.searchImage.set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
		self.logo = gtk.Image()
		self.logo.set_from_file(os.path.join(os.path.dirname(__file__), 'logo_vkontakte_bw.png'))
		
		self.vbox.pack_start(self.logo, False, True, 0)
		self.hbox = gtk.HBox()
		self.entry = gtk.Entry()
		self.vbox.pack_start(self.hbox, False, True, 5)
	
		self.hbox.pack_start(self.searchLabel, False, True, 5)
		self.hbox.pack_start(self.entry, True, True, 0)
		self.but = gtk.Button()
		self.but.set_image(self.searchImage)
		self.hbox.pack_start(self.but, False, True, 5)
		
		self.scroll = gtk.ScrolledWindow()
		self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.vbox.pack_start(self.scroll, True, True, 5)
		
		self.list = gtk.ListStore(str,str)
		self.tw = gtk.TreeView(self.list)

		self.tsel = self.tw.get_selection()
		self.tsel.set_mode(gtk.SELECTION_MULTIPLE)
		
		self.track_cell = gtk.CellRendererText()
		self.dur_cell = gtk.CellRendererText()
		self.dur_cell.set_property('xalign', 1.0)
		
		self.track = gtk.TreeViewColumn("Трек", self.track_cell, text=0)
		self.track.set_property('resizable', True)
		self.track.set_property('sizing', gtk.TREE_VIEW_COLUMN_FIXED)
		self.track.set_property('fixed-width', 250)
		
		self.dur = gtk.TreeViewColumn("Длительность", self.dur_cell, text=1)
		self.dur.set_property('sizing', gtk.TREE_VIEW_COLUMN_FIXED)
		self.dur.set_property('fixed-width', 40)
		
		self.track.pack_start(self.track_cell, True)
		self.dur.pack_start(self.dur_cell, True)
		
		self.tw.set_headers_visible(True)
		
		self.context_m = gtk.Menu()
		self.to_playlist = gtk.ImageMenuItem("Добавить в список")
		self.to_playlist.set_image(gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU))
		self.download = gtk.ImageMenuItem("Скачать...")
		self.download.set_image(gtk.image_new_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_MENU))
		self.context_m.add(self.to_playlist)
		self.context_m.add(self.download)
		self.context_m.show_all()
		
		self.tw.append_column(self.track)
		self.tw.append_column(self.dur)

		self.scroll.add(self.tw)
		
		self.title='Vkontakte'
		self.vbox.show_all()
		exaile.gui.add_panel(self.vbox, self.title)

	def add_to_playlist(self, widget, start_editing=None, wget=False):
		playlist_handle = self.play.get_selected_playlist().playlist
		model, mysel = self.tw.get_selection().get_selected_rows()
		myTrack = []
		for i in mysel:
			tr = trax.Track(self.comp[i[0]]["mp3"])
			tr.set_tag_raw("artist",  self.comp[i[0]]["artist"])
			tr.set_tag_raw("title", self.comp[i[0]]["track"])
			tr.set_tag_raw("album", "Vkontakte.ru")
			myTrack.append(tr)
		if not wget:
			playlist_handle.add_tracks(myTrack, None)
		else:
			for i in mysel:
				path = "~/"
				res = os.system('wget -b -P %s -O "%s - %s.mp3" %s -o /dev/null' % (path, self.comp[i[0]]["artist"], self.comp[i[0]]["track"], self.comp[i[0]]["mp3"]))
			
	
	def menu_popup(self, tw, event):
		if event.button == 3:
			time = event.time
			self.context_m.popup( None, None, None, event.button, time)
			return 1
		elif event.type == gtk.gdk._2BUTTON_PRESS:
			self.add_to_playlist(self)

	def start_search(self, exaile):		
		self.list.clear()
		queryString = self.entry.get_text().strip()
		md5hash =  hashlib.md5('2168735api_id=1848079count=200method=audio.searchq='+queryString+'test_mode=1oI0L6UgIyG').hexdigest()
		url =  'http://api.vkontakte.ru/api.php?api_id=1848079&count=200&method=audio.search&sig='+md5hash+'&test_mode=1&q='+queryString
		
		try:
			XMLfile = urllib.urlopen(url).read()
			ss = ElementTree.XML(XMLfile)
		except:	
			showerr = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Can't get XML file! Check your internet connection!")
			showerr.run()
			showerr.destroy()
			return
			
		self.comp = []
		
		for audio in ss.findall("audio"):
			tracks={}
			tracks["duration"] ="%2d:%02d" % (int(audio[4].text)/60, int(audio[4].text) % 60)
			tracks["artist"] = self.unescape(audio[2].text)
			tracks["track"] = self.unescape(audio[3].text)
			tracks["mp3"] = audio[5].text
			self.comp.append(tracks)
		self.comp = dict((a['track'], a) for a in self.comp).values()
		for each in self.comp:
			self.list.append([each["artist"]+" - "+each["track"], each["duration"]])
		self.tw.get_selection().select_path(0)

	def events_connect(self):
		self.entry.connect("activate", self.start_search)
		self.tw.connect("button-press-event", self.menu_popup)
		self.but.connect("pressed", self.start_search)
		self.tw.connect("select-cursor-row", self.add_to_playlist)
		self.to_playlist.connect("activate", self.add_to_playlist)
		self.download.connect("activate", self.add_to_playlist, None, True)
