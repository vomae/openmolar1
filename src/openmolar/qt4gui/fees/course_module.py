# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
functions to open a course, close a course, or check if one is needed.
'''
from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings
from openmolar.dbtools import writeNewCourse
from openmolar.qt4gui.dialogs import newCourse, Ui_completionDate
from openmolar.qt4gui import contract_gui_module

def newCourseNeeded(parent):
    '''
    checks to see if the patient is under treatment.
    if not, start a course
    '''
    if parent.pt.underTreatment:
        return False
    else:
        if not setupNewCourse(parent):
            parent.advise("unable to plan or perform treatment if pt " + \
            "does not have an active course", 1)
            return True
        else:
            print "new course started with accd of '%s'"% parent.pt.accd
            
def setupNewCourse(parent):
    '''
    set up a new course of treament
    '''
    Dialog = QtGui.QDialog(parent)

    if localsettings.clinicianNo != 0 and \
    localsettings.clinicianInits in localsettings.activedents:
        #-- clinician could be a hygenist!
        cdnt = localsettings.clinicianNo
    elif parent.pt.dnt2 == 0:
        cdnt = parent.pt.dnt1
    else:
        cdnt = parent.pt.dnt2
    dl = newCourse.course(Dialog, localsettings.ops[parent.pt.dnt1], \
                          localsettings.ops[cdnt], parent.pt.cset)
    result = dl.getInput()

    #-- (True, ['BW', 'AH', '', PyQt4.QtCore.QDate(2009, 5, 3)])

    if result[0]:
        atts = result[1]
        dnt1 = localsettings.ops_reverse[atts[0]]
        if dnt1 != parent.pt.dnt1:
            contract_gui_module.changeContractedDentist(parent, atts[0])
        dnt2 = localsettings.ops_reverse[atts[1]]
        if dnt2 != parent.pt.dnt2:
            contract_gui_module.changeCourseDentist(parent, atts[1])
        if atts[2] != parent.pt.cset:
            contract_gui_module.changeCourseType(atts[2])

        accd = atts[3].toPyDate()

        course = writeNewCourse.write(parent.pt.serialno,
        localsettings.ops_reverse[atts[1]], str(accd))
        
        if course[0]:
            parent.pt.blankCurrtrt()
            parent.pt.courseno = course[1]
            parent.pt.courseno0 = course[1]
            parent.pt.setAccd(accd)
            parent.advise("Sucessfully started new course of treatment")
            parent.pt.estimates = []
            parent.pt.underTreatment = True
            #parent.load_newEstPage()
            parent.updateDetails()
            parent.pt.addHiddenNote("open_course")
            return True
        else:
            parent.advise("ERROR STARTING NEW COURSE, sorry", 2)

def closeCourse(parent):
    '''
    allow the user to add a completion Date to a course of treatment
    '''
    Dialog = QtGui.QDialog(parent)
    my_dialog = Ui_completionDate.Ui_Dialog()
    my_dialog.setupUi(Dialog)
    earliestDate = localsettings.pyDatefromUKDate(parent.pt.accd)
    my_dialog.dateEdit.setMinimumDate(earliestDate)
    my_dialog.dateEdit.setMaximumDate(QtCore.QDate().currentDate())
    my_dialog.dateEdit.setDate(QtCore.QDate().currentDate())
    
    if Dialog.exec_():
        cmpd = my_dialog.dateEdit.date().toPyDate()
        parent.pt.setCmpd(cmpd)
        parent.pt.underTreatment = False
        parent.updateDetails()
        parent.pt.addHiddenNote("close_course")
        return True
    
def resumeCourse(parent):
    '''
    resume the previous treatment course
    '''
    message = "Resume the previous course of treatment?"
    result = QtGui.QMessageBox.question(parent, "Confirm", message,
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
    if result == QtGui.QMessageBox.Yes:
        parent.pt.cmpd = None
        parent.pt.underTreatment = True
        parent.updateDetails()
        parent.pt.addHiddenNote("resume_course")
        return True