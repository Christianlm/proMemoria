# -*- coding: UTF-8 -*-
# Promemoria installation tasks
# Copyright (C) 2022
# Released under GPL2

import os
import shutil
import globalVars
import glob

configPath = globalVars.appArgs.configPath
addonDir = os.path.abspath(os.path.dirname(__file__))
PREVIOUS_REMINDERS = os.path.join(configPath, "addons",
	"promemoria", "globalPlugins", "promemoria", "reminder.txt"
)

def copyTree(src, dst):
	try:
		shutil.copytree(src, dst)
	except IOError:
		pass

def onInstall():
	REMINDERS_PATH = os.path.join(addonDir, "globalPlugins", "promemoria", "reminders")
	PREVIOUS_PATH = os.path.join(
		configPath, "addons", "promemoria", "globalPlugins", "promemoria", "reminders"
	)
	ADDON_PATH = os.path.join(configPath, "addons",
		"promemoria", "globalPlugins", "promemoria"
	)
	if os.path.isfile(PREVIOUS_REMINDERS):
		GET_FILE = glob.glob(ADDON_PATH + "\\*.txt")
		if not os.path.isdir(REMINDERS_PATH):
			os.makedirs(REMINDERS_PATH)
		for file in GET_FILE:
			try:
				shutil.copy(file, REMINDERS_PATH)
			except IOError:
				pass

	if os.path.isdir(PREVIOUS_PATH):
		copyTree(PREVIOUS_PATH, REMINDERS_PATH)
