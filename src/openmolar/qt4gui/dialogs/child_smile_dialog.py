#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

import logging
import re
import socket
import urllib2
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.upper_case_line_edit import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

LOOKUP_URL = "http://www.psd.scot.nhs.uk/dev/simd/simdLookup.aspx"

# here is the result when using this

EXAMPLE_RESULT = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>
 SIMD Lookup for PSD
</title></head>
<body>
    <form method="post" action="simdLookup.aspx?_=1348071532912&amp;pCode=IV2+5XQ" id="form1">
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJODExMDE5NzY5D2QWAgIDD2QWAgIBDw8WAh4EVGV4dAUMU0lNRCBBcmVhOiA0ZGRkXUm1+PLLKbrXDulhPdHkxpJgof6hEmrnSC3uCZiOeQ0=" />
    <div>
        <span id="simd">SIMD Area: 4</span>
    </div>
    </form>
</body>
</html>
'''

TODAYS_LOOKUPS = {}  # {"IV1 1PP": "SIMD Area: 1"}


class ChildSmileDialog(BaseDialog):
    result = ""
    is_checking_website = False

    def __init__(self, parent):
        BaseDialog.__init__(self, parent)

        self.main_ui = parent
        self.header_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pcde_le = UpperCaseLineEdit()
        self.pcde_le.setText(self.main_ui.pt.pcde)
        self.simd_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.tbi_checkbox = QtGui.QCheckBox(
            _("ToothBrushing Instruction Given"))
        self.tbi_checkbox.setChecked(True)

        self.di_checkbox = QtGui.QCheckBox(_("Dietary Advice Given"))
        self.di_checkbox.setChecked(True)

        self.fl_checkbox = QtGui.QCheckBox(_("Fluoride Varnish Applied"))
        self.fl_checkbox.setToolTip(
            _("Fee claimable for patients betwen 2 and 5"))
        self.fl_checkbox.setChecked(2 <= self.main_ui.pt.ageYears <= 5)

        self.insertWidget(self.header_label)
        self.insertWidget(self.pcde_le)
        self.insertWidget(self.simd_label)
        self.insertWidget(self.tbi_checkbox)
        self.insertWidget(self.di_checkbox)
        self.insertWidget(self.fl_checkbox)

        self.pcde_le.textEdited.connect(self.check_pcde)

        self._simd = None

    @property
    def pcde(self):
        try:
            return str(self.pcde_le.text())
        except:
            return ""

    @property
    def valid_postcode(self):
        return bool(re.match("[A-Z][A-Z](\d+) (\d+)[A-Z][A-Z]", self.pcde))

    def postcode_warning(self):
        if not self.valid_postcode:
            QtGui.QMessageBox.warning(self, "error", "Postcode is not valid")

    def check_pcde(self):
        if self.valid_postcode:
            QtCore.QTimer.singleShot(50, self.simd_lookup)
        else:
            self.header_label.setText(_("Please enter a valid postcode"))
            self.simd_label.setText("")
            self.enableApply(False)

    def simd_lookup(self):
        '''
        poll the server for a simd for a postcode
        '''
        QtGui.QApplication.instance().processEvents()
        global TODAYS_LOOKUPS
        try:
            self.result = TODAYS_LOOKUPS[self.pcde]
            self.simd_label.setText("%s %s" % (_("KNOWN SIMD"), self.result))
            self.enableApply(True)
            LOGGER.debug("simd_lookup unnecessary, value known")
            return
        except KeyError:
            pass

        self.header_label.setText(_("Polling website with Postcode"))

        pcde = self.pcde.replace(" ", "%20")

        url = "%s?pCode=%s" % (LOOKUP_URL, pcde)

        try:
            QtGui.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)
            req = urllib2.Request(url)
            response = urllib2.urlopen(req, timeout=10)
            result = response.read()
            self.result = self._parse_result(result)
        except urllib2.URLError as exc:
            raise socket.timeout(exc)
            LOGGER.error("url error polling NHS website?")
            self.result = _("Error polling website")
        except socket.timeout as e:
            LOGGER.error("timeout error polling NHS website?")
            self.result = _("Timeout polling website")
        finally:
            QtGui.QApplication.instance().restoreOverrideCursor()

        self.simd_label.setText("%s = %s" % (_("RESULT"), self.result))
        QtGui.QApplication.instance().processEvents()

        TODAYS_LOOKUPS[self.pcde] = "SIMD: %s" % self.simd_number
        self.enableApply(self.simd_number is not None)

        self.header_label.setText("SIMD %d" % self.simd_number)

    def _parse_result(self, result):
        try:
            dom = minidom.parseString(result)
            e = dom.getElementsByTagName("span")[0]
            return e.firstChild.data
        except ExpatError:
            return "UNDECIPHERABLE REPLY"

    def manual_entry(self):
        simd, result = QtGui.QInputDialog.getInteger(self,
                                                     _(
                                                     "Manual Input Required"),
                                                     _(
                                                     "Online lookup has failed, please enter the SIMD manually"),
                                                     4, 1, 5)
        if not result:
            self.reject()
        return simd

    @property
    def simd_number(self):
        if self._simd is None:
            m = re.search("(\d+)", self.result)
            if m:
                self._simd = int(m.groups()[0])
            else:
                self._simd = 4
                self._simd = self.manual_entry()
        return self._simd

    @property
    def tbi_performed(self):
        return self.tbi_checkbox.isChecked()

    @property
    def di_performed(self):
        return self.di_checkbox.isChecked()

    @property
    def fl_applied(self):
        return self.fl_checkbox.isChecked()

    @property
    def tx_items(self):
        age = self.main_ui.pt.ageYears
        dentist = localsettings.clinicianNo in localsettings.dentDict.keys()
        LOGGER.debug("Performed by dentist = %s" % dentist)
        if age < 3:
            if self.simd_number < 4:
                yield ("other", "CS1")
            else:
                yield ("other", "CS2")
            if self.tbi_performed:
                code = "TB1" if dentist else "TB2"
                yield ("other", code)
            if self.di_performed:
                code = "DI1" if dentist else "DI2"
                yield ("other", code)
        else:
            if self.simd_number < 4:
                yield ("other", "CS3")
            if self.tbi_performed:
                code = "TB3" if dentist else "TB4"
                yield ("other", code)
            if self.di_performed:
                code = "DI3" if dentist else "DI4"
                yield ("other", code)

        if 2 <= age <= 5:
            if self.fl_applied:
                yield ("other", "CSFL")

    def exec_(self):
        QtCore.QTimer.singleShot(100, self.check_pcde)
        QtCore.QTimer.singleShot(500, self.postcode_warning)

        if BaseDialog.exec_(self):
            if self.valid_postcode:
                self.main_ui.pt.pcde = self.pcde

            self.main_ui.addNewNote("CHILDSMILE (postcode '%s'): %s" %
                                   (self.pcde, self.result))

            return True


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    def _mock_function(*args):
        pass
    from collections import namedtuple

    localsettings.initiate()
    app = QtGui.QApplication([])

    ui = QtGui.QMainWindow()
    ui.pt = namedtuple("pt", ("pcde", "ageYears"))

    ui.pt.pcde = "Iv1 1P"
    ui.pt.ageYears = 3
    ui.addNewNote = _mock_function

    dl = ChildSmileDialog(ui)
    # print dl._parse_result(EXAMPLE_RESULT)
    if dl.exec_():
        print (dl.result)
        print (dl.simd_number)
        print ("toothbrush instruction = %s" % dl.tbi_performed)
        print ("dietary advice = %s" % dl.di_performed)

        for item in dl.tx_items:
            print item
