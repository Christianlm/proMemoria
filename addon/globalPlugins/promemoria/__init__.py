# -*- coding: UTF-8 -*-
#Copyright (C) 2020-2022 by chris llajta2012@gmail.com
# Released under GPL 2
# Promemoria addon for NVDA screen reader 
# version 0.4.20220319-dev:

import addonHandler
import globalPluginHandler
import wx 
import core
import ui
import gui
from gui import guiHelper
import os
from scriptHandler import script
import time
import datetime
from datetime import date
import re
from urllib.request import urlopen, Request
import json
from .skipTranslation import translate

addonHandler.initTranslation()

ADDON_DIR = os.path.dirname(__file__)
file_path = os.path.join(ADDON_DIR, "reminder.txt")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		core.postNvdaStartup.register(self.onNVDAStart)

	# menu .
		self.menu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.promemoriaMenu = wx.Menu()
		# Translators: name of a submenu.
		self.mainItem = self.menu.AppendSubMenu(self.promemoriaMenu, _("Pro&memoria"))
		# Translators: the name of a menu item.
		self.promemoriaItem = self.promemoriaMenu.Append(wx.ID_ANY, _("Insert Pro&memoria"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onPromemoriaDialog, self.promemoriaItem)
		# Translators: the name of a menu item.
		self.upgradeItem = self.promemoriaMenu.Append(wx.ID_ANY, _("&Check updates"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.toGetUpdate, self.upgradeItem)

	def terminate(self):
		try:
			self.menu.Remove(self.mainItem)
		except: #(RuntimeError, AttributeError, wx.PyDeadObjectError):
			pass

	def onNVDAStart(self):
		if os.path.exists(file_path):
			lookup_file = open(file_path, 'r')
			today = time.strftime("%e/%m: ")
			bday_flag = 0
			for entry in lookup_file:
				if today in entry:
					bday_flag = 1
					wx.CallAfter(toReminder, None)
			else:
				pass

	def onPromemoriaDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(PromemoriaDialog)

	@script(
		# Translators: message presented in input mode.
		description=_("Show the promemoria dialog.")
	)
	def script_showPromemoriaDialog(self, gesture):
		wx.CallAfter(self.onPromemoriaDialog, None)

	def onCheckUpdatesDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(checkUpdatesDialog)

	def toGetUpdate(self, evt):
		version = addonHandler.getCodeAddon().manifest["version"]
		h = "iuuqt;00bqj/hjuivc/dpn0sfqpt0Disjtujbomn0qspnfnpsjb0sfmfbtft0mbuftu"
		req = Request("".join(map(lambda x: chr(ord(x) - 1), h)))
		res = urlopen(req)
		results = {}
		results.update(json.load(res))
		res.close()
		ASSETS = results.get("assets")
		browserDownloadUrl = ASSETS[0].get("browser_download_url")
		remoteVersion = re.search("(?P<name>)-(?P<version>.*).nvda-addon", browserDownloadUrl.split("/")[-1]).groupdict()["version"]
		if remoteVersion != version:
			wx.CallAfter(self.onCheckUpdatesDialog, None)
		else:
			ui.browseableMessage(_("The current version {ver} is the latest.").format(ver=version), _("Promemoria addon  is up to date!"))

# Dialogs:

class ReminderDialog(wx.Dialog):

	def __init__(self, parent):
		# Translators: Title for the Reminder dialog.
		super(ReminderDialog,self).__init__(parent,title=_("Actung!"))
		text = setWarnig()
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sizerHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		sizerHelper.addItem(wx.StaticText(self, label=text))

		bHelper = sizerHelper.addDialogDismissButtons(guiHelper.ButtonHelper(wx.HORIZONTAL))
		self.okButton = bHelper.addButton(self, label=_("&Ok"))
		self.okButton.Bind(wx.EVT_BUTTON, self.onOk)
		# Translators: The label for a button.
		self.removeButton = bHelper.addButton(self, label=_("&Remove reminder"))
		self.removeButton.Bind(wx.EVT_BUTTON, self.onDelete)

		mainSizer.Add(sizerHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.Sizer = mainSizer
		mainSizer.Fit(self)
		self.CentreOnScreen()
		wx.CallAfter(self.Show)

	def onOk(self, evt):
		self.Destroy()

	def onDelete(self, evt):
		if gui.messageBox(
			# Translators: Confirmation warnig.
			_("Are you sure you want to delete this reminder?"),
			# Translators: Title of Confirm warnig
			_("Confirm"),
			wx.OK | wx.CANCEL | wx.ICON_QUESTION, self
		) != wx.OK:
			return

		substr = time.strftime("%e/%m: ")
		with open(file_path, 'r+') as f:
			d = f.readlines()
			f.seek(0)
			for i in d:
				if substr not in i:
					f.write(i)
					f.truncate()
		self.Destroy()

def toReminder(evt):
	gui.mainFrame.prePopup()
	wx.Bell()
	ReminderDialog(gui.mainFrame).Show()
	gui.mainFrame.postPopup()

class PromemoriaDialog(wx.Dialog):

	def __init__(self, parent):
		# Translators: Title of the promemoria dialog.
		super(PromemoriaDialog, self).__init__(parent, title=_("Promemoria"))

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: The label of an edit box in the  dialog.
		promemoriaLabel = _("&Event:")
		self.promemoriaEdit = sHelper.addLabeledControl(promemoriaLabel, wx.TextCtrl)

		# Translators: The label of a list box.
		daysLabel = _("Select &day")
		daysChoices = [datetime.date(2000, 1, d).strftime('%e') for d in range(1, 32)]
		self.daysListBox = sHelper.addLabeledControl(daysLabel, wx.ListBox , choices=daysChoices)
		self.daysListBox.SetStringSelection(date.today().strftime("%e"))
		self.daysListBox.Bind(wx.EVT_LISTBOX, self.onSetDate)

		# Translators: The label of a list box.
		monthsLabel = _("Select &mounth")
		monthsChoices = [datetime.date(2000, m, 1).strftime('%B') for m in range(1, 13)]
		self.monthsListBox = sHelper.addLabeledControl(monthsLabel, wx.ListBox , choices=monthsChoices)
		self.monthsListBox.SetStringSelection(date.today().strftime("%B"))
		self.monthsListBox.Bind(wx.EVT_LISTBOX, self.onSetDate)

		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.Sizer = mainSizer
		mainSizer.Fit(self)
		self.promemoriaEdit.SetFocus()
		self.CentreOnScreen()

	def onSetDate(self, evt):
		self.daysListBox.GetStringSelection()
		self.monthsListBox.GetSelection()

	def onOk(self, evt):
		d = self.daysListBox.GetStringSelection()
		ms = self.monthsListBox.GetStringSelection()
		m = dMonths.get(ms)
		r = self.promemoriaEdit.Value
		f = open(file_path,"a")
		f.write("\n" + d + "/" + m + ": - " + r + "\n") 
		f.close()
		self.Destroy()


def setWarnig():
	linesList = []
	linenum = 0
	substr =  time.strftime("%e/%m: ")
	with open(file_path, 'rt') as m:
		for line in m:
			linenum += 1
			if line.lower().find(substr) != -1:
				linesList.append(_("Do you remember? ") + line.rstrip('\n'))
	for e in linesList:
		text = e
		return text

dMonths = {datetime.date(1986, 1, 1).strftime('%B'): "01", datetime.date(1986, 2, 1).strftime('%B'): "02", datetime.date(1986, 3, 1).strftime('%B'): "03", datetime.date(1986, 4, 1).strftime('%B'): "04", datetime.date(1986, 5, 1).strftime('%B'): "05", datetime.date(1986, 6, 1).strftime('%B'): "06", datetime.date(1986, 7, 1).strftime('%B'): "07", datetime.date(2000, 8, 1).strftime('%B'): "08", datetime.date(1986, 9, 1).strftime('%B'): "09", datetime.date(1986, 10, 1).strftime('%B'): "10", datetime.date(1986, 11, 1).strftime('%B'): "11", datetime.date(1986, 12, 1).strftime('%B'): "12"}


# New Version Notification.
class checkUpdatesDialog(wx.Dialog):

	def __init__(self, parent):
		# Translators: The title of the check  updates dialog.
		super(checkUpdatesDialog,self).__init__(parent,title=_("New Version Notification"))
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sizerHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Message displayed when updates are available.
		sizerHelper.addItem(wx.StaticText(self, label=_("""...\nChange log not available in dis moment...\n""")))
		bHelper = sizerHelper.addDialogDismissButtons(guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: The label of a button.
		label = _("Proceed to &download page")
		self.upgradeButton = bHelper.addButton(self, label=label)
		self.upgradeButton.Bind(wx.EVT_BUTTON, self.onUpgrade)

		closeButton = bHelper.addButton(self, wx.ID_CLOSE, label=translate("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Bind(wx.EVT_CLOSE, lambda evt: self.onClose)
		self.EscapeId = wx.ID_CLOSE

		mainSizer.Add(sizerHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.Sizer = mainSizer
		mainSizer.Fit(self)
		self.CentreOnScreen()
		wx.CallAfter(self.Show)

	def onUpgrade(self, evt):
		downloadPage = "https://christianlm.github.io/promemoria/"
		os.startfile(downloadPage)
		self.Destroy()

	def onClose(self, evt):
		self.Destroy()
