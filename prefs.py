# -*- coding: utf8 -*-

from xl.nls import gettext as _
import os
from xlgui.preferences import widgets

name = _("Vk_Exaile")
basedir = os.path.dirname(os.path.realpath(__file__))
ui = os.path.join(basedir, "preference.ui")

class PathPreference(widgets.ComboEntryPreference):
	name = 'vk_exaile/path'
	preset_items = ["%s/" % os.getenv("HOME")]
	default = "%s/" % os.getenv("HOME")