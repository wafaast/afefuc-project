'''
Created on Apr 27, 2013

@author: Bartosz Alchimowicz
'''

import re
import inspect

from PyQt4 import QtCore, QtGui
from generated.ui.UseCaseForm import Ui_UseCaseForm
from format import model
from utils import validation
from utils import converter
from SelectActorsFormWrapper import SelectActorsFormWrapper
from EventPropertiesFormWrapper import EventPropertiesFormWrapper


try:
        _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
        _fromUtf8 = lambda s: s

#class PushButtonDelegate(QtGui.QItemDelegate):
#   def __init__(self, owner, name):
#       QtGui.QItemDelegate.__init__(self, owner)
#       self.name = name
#
#   def paint(self, painter, option, index):
#       style = QtGui.QApplication.style()
#       opt = QtGui.QStyleOptionButton()
#
#       opt.text = self.name
#       opt.rect = option.rect
#       opt.state |= QtGui.QStyle.State_Enabled
#
#       style.drawControl(QtGui.QStyle.CE_PushButton, opt, painter)

class MainScenarioTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, afefuc, items, event_model):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.afefuc = afefuc
        self.item = items[1]
        self.item_orginal = items[0]
        self.parent = parent
        self.event_model = event_model
        
    def rowCount(self, parent):
        return len(self.item.scenario.items)

    def columnCount(self, parent):
        return 2 #4

    def data(self, index, role):
        if not index.isValid() and role not in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            return QtCore.QVariant()

        column = index.column()
        row = index.row()

        if column == 0 and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(row + 1)
        elif column == 1 and role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            edit = True if role == QtCore.Qt.EditRole else False

            step = self.item.scenario.items[row]

            retval = QtCore.QVariant(converter.itemsToText(step.items, edit))

            return QtCore.QVariant(retval)

        return QtCore.QVariant()

    def flags(self, index):
        flags = super(QtCore.QAbstractTableModel, self).flags(index)

        if index.column() == 1:
            flags |= QtCore.Qt.ItemIsEditable#|QtCore.Qt.ItemIsSelectable

        return flags

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole:
            value = unicode(value.toString().toUtf8(), 'utf-8')
            try:
                items = converter.textToItems(self.afefuc['project'], value, (self.item_orginal, self.item))
                self.item.scenario.items[index.row()].items = items
            except ValueError:
                validation.errorMessage(None, "Invalid reference")
                self.item.scenario.items[index.row()].items = [model.TextItem(value)]
                #form.mainScenarioView.setFocus()
                #form.mainScenarioView.setCurrentCell(index, 2)


            return True

        return False

    def insertItem(self, item, position = None):
        if position is None:
            first = self.rowCount(QtCore.QModelIndex())
            last = self.rowCount(QtCore.QModelIndex())
        else:
            first = position
            last = position

        self.beginInsertRows(QtCore.QModelIndex(), first, last)

        if position is None:
            self.item.scenario.items.append(item)
        else:
            self.item.scenario.items.insert(position, item)

        self.endInsertRows()

        self.event_model.reset()

    def removeItem(self, position):
        hasEvents = False

        if self.item.scenario.items[position].events: hasEvents = True

        self.beginRemoveRows(QtCore.QModelIndex(), position, position)

        del(self.item.scenario.items[position])

        if hasEvents: self.event_model.reset()

        self.endRemoveRows()

        return True

    def movePositionUp(self, position):
        if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
            return

        pos1 = position
        pos2 = position - 1

        (
                self.item.scenario.items[pos1],\
                self.item.scenario.items[pos2] \
        ) = (\
                self.item.scenario.items[pos2],\
                self.item.scenario.items[pos1] \
        )

        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                self.createIndex(min(pos1, pos2), 0, None),
                self.createIndex(max(pos1, pos2), 1, None)
        )

        self.event_model.reset()

    def movePositionDown(self, position):
        self.movePositionUp(position + 1)

#   def optButtons(self, index):
#       if index.column() == 3:
#           self.removeItem(index.row())

class EventsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, afefuc, items):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.afefuc = afefuc
        self.item = items[1]
        self.item_orginal = items[0]
        self.parent = parent

    def rowCount(self, parent):
        counter = 0

        for item in self.item.scenario.items:
            if len(item.events) > 0:
                for event in item.events:
                    counter += 1 + len(event.scenario.items)

        return counter

    def columnCount(self, parent):
        return 2 #3

    def positionToCoordinates(self, position):
        """
        returns (t, i, j, k)
        t - type - E for event (title), S step in event
        i - step in uc
        j - event number
        k - step in event
        """
        counter = 0

        for i, item in enumerate(self.item.scenario.items):
            if len(item.events) > 0:
                for j, event in enumerate(item.events):
                    if counter == position:
                        return ('E', i, j)
                    elif counter + len(event.scenario.items) < position:
                            counter += len(event.scenario.items) + 1
                    else:
                        counter += 1

                        for k, s in enumerate(event.scenario.items):
                            if counter == position:
                                return ('S', i, j, k)

                            counter += 1

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        row = index.row()

        if column == 0 and role == QtCore.Qt.DisplayRole:
            coords = self.positionToCoordinates(row)

            if coords[0] == 'E':
                retval = QtCore.QVariant("%d.%c" % (coords[1]+1, chr(coords[2]+65)))
            else:
                retval = QtCore.QVariant("%d.%c.%d" % (coords[1]+1, chr(coords[2]+65), coords[3]+1))

            return retval
        elif column == 1 and role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            coords = self.positionToCoordinates(row)

            edit = True if role == QtCore.Qt.EditRole else False

            if coords[0] == 'E':
                retval = QtCore.QVariant(
                        converter.itemsToText(
                                self.item.scenario.items[coords[1]].events[coords[2]].title,
                                edit
                        )
                )
            else:
                step = self.item.scenario.items[coords[1]].events[coords[2]].scenario.items[coords[3]]

                retval = QtCore.QVariant(converter.itemsToText(step.items, edit))

            return retval

        return QtCore.QVariant()

    def flags(self, index):
        flags = super(QtCore.QAbstractTableModel, self).flags(index)

        if index.column() == 1:
            flags |= QtCore.Qt.ItemIsEditable#|QtCore.Qt.ItemIsSelectable

        return flags

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole:
            #if value.toString().isEmpty():
            #   return False;

            row = index.row()

            value = unicode(value.toString().toUtf8(), 'utf-8')


            try:
                new = converter.textToItems(self.afefuc['project'], value, (self.item_orginal, self.item))
            except ValueError:
                validation.errorMessage(None, "Invalid reference")
                new = [model.TextItem(value)]

            counter = 0;

            for i, item in enumerate(self.item.scenario.items):
                if len(item.events) > 0:
                    for j, event in enumerate(item.events):
                        if counter == row:
                            self.item.scenario.items[i].events[j].title = new
                            #self.endInsertRows()

                            return True
                        elif counter + len(event.scenario.items) < row:
                            counter += len(event.scenario.items) + 1
                        else:
                            counter += 1

                            for k, s in enumerate(event.scenario.items):

                                if counter == row:
                                    self.item.scenario.items[i].events[j].scenario.items[k].items = new
                                    #self.endInsertRows()

                                    return True

                                counter += 1

        return False

    def insertEvent(self, position):
        event = model.Event()
        step = model.Step()

        event.setParent(self.item.scenario.items[position])
        step.setParent(event)

        event.scenario.items.append(step)

        self.item.scenario.items[position].events.append(event)

        self.reset()

    def insertStep(self, position):
        coords = self.positionToCoordinates(position)

        if coords[0] == 'E':
            self.item.scenario.items[coords[1]].events[coords[2]].scenario.items.insert(0, model.Step())
        else:
            self.item.scenario.items[coords[1]].events[coords[2]].scenario.items.insert(coords[3], model.Step())

        self.reset()

    def removeItem(self, position):
        coords = self.positionToCoordinates(position)

        end = position

        if coords[0] == 'E':
            end = position+len(self.item.scenario.items[coords[1]].events[coords[2]].scenario.items)

        self.beginRemoveRows(QtCore.QModelIndex(), position, end)

        if coords[0] == 'E':
            del(self.item.scenario.items[coords[1]].events[coords[2]])
        else:
            del(self.item.scenario.items[coords[1]].events[coords[2]].scenario.items[coords[3]])

        self.endRemoveRows()

        return True

    def movePositionUp(self, position):
        if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
            return

        coords = self.positionToCoordinates(position)

        if coords[0] == 'E' or coords[3] == 0:
            return

        t, i, j, k1 = coords

        k2 = k1 -1

        (
                self.item.scenario.items[i].events[j].scenario.items[k1],\
                self.item.scenario.items[i].events[j].scenario.items[k2] \
        ) = (
                self.item.scenario.items[i].events[j].scenario.items[k2],\
                self.item.scenario.items[i].events[j].scenario.items[k1] \
        )

        self.reset()

    def movePositionDown(self, position):
        if position < 0 or position == self.rowCount(QtCore.QModelIndex()) - 1:
            return

        coords = self.positionToCoordinates(position)

        if coords[0] == 'E':
            return

        t, i, j, k1 = coords

        if k1 == len(self.item.scenario.items[i].events[j].scenario.items) - 1:
            return

        k2 = k1 + 1

        (
                self.item.scenario.items[i].events[j].scenario.items[k1],\
                self.item.scenario.items[i].events[j].scenario.items[k2] \
        ) = (
                self.item.scenario.items[i].events[j].scenario.items[k2],\
                self.item.scenario.items[i].events[j].scenario.items[k1] \
        )

        self.reset()

#   def optButtons(self, index):
#       if index.column() == 2:
#           self.removeItem(index.row())

class ConditionsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, afefuc, items, conditions):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.afefuc = afefuc
        self.conditions = conditions
        self.item = items[1]
        self.item_orginal = items[0]
        self.parent = parent

    def rowCount(self, parent):
        return len(self.conditions)

    def columnCount(self, parent):
        return 2 #3

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        row = index.row()

        if column == 0 and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(row + 1)
        elif column == 1 and role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            return QtCore.QVariant(converter.itemsToText(self.conditions[row].items, role == QtCore.Qt.EditRole))

        return QtCore.QVariant()

    def flags(self, index):
        flags = super(QtCore.QAbstractTableModel, self).flags(index)

        if index.column() == 1:
            flags |= QtCore.Qt.ItemIsEditable#|QtCore.Qt.ItemIsSelectable

        return flags

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole:
            value = unicode(value.toString().toUtf8(), 'utf-8')

            try:
                items = converter.textToItems(self.afefuc['project'], value, (self.item_orginal, self.item))
                self.conditions[index.row()].items = items
            except ValueError:
                validation.errorMessage(self.dialog, "Invalid reference")

            self.conditions[index.row()].items = [format.model.TextItem(value)]

            return True

        return False

    def insertItem(self, item, position = None):
        if position is None:
            first = self.rowCount(QtCore.QModelIndex())
            last = self.rowCount(QtCore.QModelIndex())
        else:
            first = position
            last = position

        self.beginInsertRows(QtCore.QModelIndex(), first, last)

        if position is None:
            self.conditions.append(item)
        else:
            self.conditions.insert(position, item)

        self.endInsertRows()

    def removeItem(self, position):
        hasEvents = False

        self.beginRemoveRows(QtCore.QModelIndex(), position, position)

        del(self.conditions[position])

        self.endRemoveRows()

        return True

    def movePositionUp(self, position):
        if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
            return

        pos1 = position
        pos2 = position - 1

        (
                self.conditions[pos1],\
                self.conditions[pos2] \
        ) = (\
                self.conditions[pos2],\
                self.conditions[pos1] \
        )

        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                self.createIndex(min(pos1, pos2), 0, None),
                self.createIndex(max(pos1, pos2), 1, None)
        )

    def movePositionDown(self, position):
        self.movePositionUp(position + 1)

class UseCaseFormWrapper():
    def __init__(self, parent, afefuc, item = None):
        self.parent = parent
        self.dialog = QtGui.QDialog()
        self.form = Ui_UseCaseForm()
        self.afefuc = afefuc
        self.item = item[1]
        self.item_original = item[0]
        self.actors = afefuc['project'].actors

    def load(self):
        self.form.titleEdit.setText(_fromUtf8(converter.itemsToText(self.item.title, edit = True)))
        self.form.idEdit.setText(_fromUtf8(self.item.identifier))
        self.form.summaryTextEdit.setPlainText(_fromUtf8(converter.itemsToText(self.item.summary, edit = True)))
        self.form.remarksTextEdit.setPlainText(_fromUtf8(converter.itemsToText(self.item.remarks, edit = True)))


        if self.item.priority:
            index = self.form.priorityComboBox.findText(_fromUtf8(self.item.priority.item.name))
            if index != -1:
                self.form.priorityComboBox.setCurrentIndex(index)

        if self.item.goal_level:
            index = self.form.goalLevelComboBox.findText(_fromUtf8(self.item.goal_level.item.name))
            if index != -1:
                self.form.goalLevelComboBox.setCurrentIndex(index)

        mainactorlist = []        
        otheractorlist = []
    
        mainActorlayout = QtGui.QVBoxLayout()
        for act in self.actors:
            chekMain = QtGui.QCheckBox(act.name)
            if len(self.item.main_actors) != 0:
                if act.name in self.item.main_actors:
                    chekMain.setChecked(True)
                else:
                    chekMain.setEnabled(False)
            chekMain.setObjectName(act.name)
            mainActorlayout.addWidget(chekMain)
            mainactorlist.append(chekMain)    
            if len(self.item.main_actors) != 0:                           
                QtCore.QObject.connect(chekMain, QtCore.SIGNAL("stateChanged(int)"), lambda: self.setEditEnableAndDisableMainActorList(otheractorlist,mainactorlist))
            else:
                QtCore.QObject.connect(chekMain, QtCore.SIGNAL("stateChanged(int)"), lambda: self.setEnableAndDisableMainActorList(otheractorlist,mainactorlist))
        self.form.mainActorTab.setLayout(mainActorlayout)
        
       
        otherActorslayout = QtGui.QVBoxLayout()
        for othact in self.actors:
            chekOther = QtGui.QCheckBox(othact.name)
            if len(self.item.other_actors) != 0:
                if othact.name in self.item.other_actors:
                    chekOther.setChecked(True)
                else:
                    chekOther.setEnabled(False)
                    chekOther.setChecked(False)

            chekOther.setObjectName(othact.name)
            otherActorslayout.addWidget(chekOther)
            otheractorlist.append(chekOther)
            
            if len(self.item.other_actors) != 0:
                QtCore.QObject.connect(chekOther, QtCore.SIGNAL("stateChanged(int)"), lambda: self.setEditEnableAndDisableOtherAcotrList(otheractorlist,mainactorlist))
            else:
                QtCore.QObject.connect(chekOther, QtCore.SIGNAL("stateChanged(int)"), lambda: self.setEnableAndDisableOtherAcotrList(otheractorlist,mainactorlist))    
        self.form.otherActorsTab.setLayout(otherActorslayout)

        if len(self.item.main_actors) != 0 and len(self.item.other_actors) != 0 : 
            for i in range(len(mainactorlist)):
                if mainactorlist[i].checkState() == 0 and otheractorlist[i].checkState() == 0:
                    mainactorlist[i].setEnabled(True)
                    otheractorlist[i].setEnabled(True)     
        elif len(self.item.main_actors) != 0 and len(self.item.other_actors) == 0:             
            for i in range(len(mainactorlist)):
                if mainactorlist[i].checkState() == 2:
                    otheractorlist[i].setEnabled(False)
        elif  len(self.item.main_actors) == 0 and len(self.item.other_actors) != 0:             
            for i in range(len(mainactorlist)):
                if otheractorlist[i].checkState() == 2 :
                    mainactorlist[i].setEnabled(False)     
                    
        
    def show(self):
        
        self.form.setupUi(self.dialog)

        for p in self.afefuc['project'].ucspec.priorities:
            self.form.priorityComboBox.addItem(p.name, p)

        for p in self.afefuc['project'].ucspec.goal_levels:
            self.form.goalLevelComboBox.addItem(p.name, p)

        self.modelEV = EventsTableModel(self.form.eventsView, self.afefuc, (self.item_original, self.item))
        self.form.eventsView.setModel(self.modelEV)
        #self.form.eventsView.setItemDelegateForColumn(2, PushButtonDelegate(self.form.eventsView, "X"))
        self.form.eventsView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.form.eventsView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        #self.form.eventsView.setColumnWidth(2, 20)
        self.form.eventsView.horizontalHeader().hide()
        self.form.eventsView.verticalHeader().hide()
        self.form.eventsView.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
        self.form.eventsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.form.eventsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.modelMS = MainScenarioTableModel(self.form.mainScenarioView, self.afefuc, (self.item_original, self.item), self.modelEV)
        self.form.mainScenarioView.setModel(self.modelMS)
        #self.form.mainScenarioView.setItemDelegateForColumn(2, PushButtonDelegate(self.form.mainScenarioView, "E"))
        #self.form.mainScenarioView.setItemDelegateForColumn(3, PushButtonDelegate(self.form.mainScenarioView, "X"))
        self.form.mainScenarioView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.form.mainScenarioView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.form.mainScenarioView.setColumnWidth(2, 20)
        self.form.mainScenarioView.setColumnWidth(3, 20)
        self.form.mainScenarioView.horizontalHeader().hide()
        self.form.mainScenarioView.verticalHeader().hide()
        self.form.mainScenarioView.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
        self.form.mainScenarioView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.form.mainScenarioView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        conditions = [
            (self.form.triView, self.item.triggers),
            (self.form.prcView, self.item.preconditions),
            (self.form.pocView, self.item.postconditions),
        ]

        for v, c in conditions:
            m = ConditionsTableModel(v, self.afefuc, (self.item_original, self.item), c)
            v.setModel(m)
            v.horizontalHeader().hide()
            v.verticalHeader().hide()
            v.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            v.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            v.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
            v.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            v.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        
        QtCore.QObject.connect(self.form.insertStepMSButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertStepMSButton)
        QtCore.QObject.connect(self.form.addEventMSButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedAddEventMSButton)
        QtCore.QObject.connect(self.form.deleteMSButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteMSButton)
        QtCore.QObject.connect(self.form.moveUpMSButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpMSButton)
        QtCore.QObject.connect(self.form.moveDownMSButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownMSButton)
        QtCore.QObject.connect(self.form.insertStepEvButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertStepEvButton)
        QtCore.QObject.connect(self.form.deleteEvButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteEvButton)
        QtCore.QObject.connect(self.form.moveUpEvButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpEvButton)
        QtCore.QObject.connect(self.form.moveDownEvButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownEvButton)
        QtCore.QObject.connect(self.form.propertiesEvButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedPropertiesEvButton)
        QtCore.QObject.connect(self.form.titleEdit, QtCore.SIGNAL(_fromUtf8("editingFinished()")), self.editingFinishedTitleEdit)
        QtCore.QObject.connect(self.form.idEdit, QtCore.SIGNAL(_fromUtf8("editingFinished()")), self.editingFinishedIdEdit)
        QtCore.QObject.connect(self.form.insertTriButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertTriButton)
        QtCore.QObject.connect(self.form.deleteTriButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteTriButton)
        QtCore.QObject.connect(self.form.moveUpTriButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpTriButton)
        QtCore.QObject.connect(self.form.moveDownTriButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownTriButton)
        QtCore.QObject.connect(self.form.insertPrCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertPrCButton)
        QtCore.QObject.connect(self.form.deletePrCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeletePrCButton)
        QtCore.QObject.connect(self.form.moveUpPrCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpPrCButton)
        QtCore.QObject.connect(self.form.moveDownPrCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownPrCButton)
        QtCore.QObject.connect(self.form.insertPoCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertPoCButton)
        QtCore.QObject.connect(self.form.deletePoCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeletePoCButton)
        QtCore.QObject.connect(self.form.moveUpPoCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpPoCButton)
        QtCore.QObject.connect(self.form.moveDownPoCButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownPoCButton)
        QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
        QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

        #self.form.tabWidget.removeTab(2)

        self.load()

        self.dialog.exec_()

    def setEnableAndDisableMainActorList(self,otheractorlists,mainactorlists):
        for mainactorlist in mainactorlists:
            if mainactorlist.checkState()== 2:
                oindex = mainactorlists.index(mainactorlist)
                otheractorlists[oindex].setEnabled(False)
                if str(mainactorlist.objectName()).split("_")[0] not in self.item.main_actors:
                    self.item.main_actors.append(str(mainactorlist.objectName()).split("_")[0])

            if mainactorlist.checkState()== 0:    
                oindex = mainactorlists.index(mainactorlist)
                otheractorlists[oindex].setEnabled(True)
                # self.item.main_actors.remove("A2")
 
    def setEnableAndDisableOtherAcotrList(self,otheractorlists,mainactorlists):
        for otheractorlist in otheractorlists:
            if otheractorlist.checkState()== 2:
                oindex = otheractorlists.index(otheractorlist)
                mainactorlists[oindex].setEnabled(False)
                if str(otheractorlist.objectName()).split("_")[0] not in self.item.other_actors:
                    self.item.other_actors.append(str(otheractorlist.objectName()).split("_")[0])
            if otheractorlist.checkState()== 0:
                oindex = otheractorlists.index(otheractorlist)
                mainactorlists[oindex].setEnabled(True)
                # self.item.other_actors.remove(str(otheractorlist.objectName()).split("_")[0])

    def setEditEnableAndDisableMainActorList(self,otheractorlists,mainactorlists):
        self.item.main_actors=[]  
        for mainactorlist in mainactorlists:
            if mainactorlist.checkState()== 2:
                
                oindex = mainactorlists.index(mainactorlist)
                otheractorlists[oindex].setEnabled(False)
                if str(mainactorlist.objectName()).split("_")[0] not in self.item.main_actors:
                    self.item.main_actors.append(str(mainactorlist.objectName()).split("_")[0])
                
            if mainactorlist.checkState()== 0:    
                oindex = mainactorlists.index(mainactorlist)
                otheractorlists[oindex].setEnabled(True)
                
  

    def setEditEnableAndDisableOtherAcotrList(self,otheractorlists,mainactorlists):
        self.item.other_actors=[]
        for otheractorlist in otheractorlists:
            if otheractorlist.checkState()== 2:
                oindex = otheractorlists.index(otheractorlist)
                mainactorlists[oindex].setEnabled(False)
                if str(otheractorlist.objectName()).split("_")[0] not in self.item.other_actors:
                    self.item.other_actors.append(str(otheractorlist.objectName()).split("_")[0])
            if otheractorlist.checkState()== 0:
                oindex = otheractorlists.index(otheractorlist)
                mainactorlists[oindex].setEnabled(True)
            

    def clickedCancelButton(self):
        self.dialog.close()

    def clickedOKButton(self):
#       index = self.form.priorityComboBox.currentIndex()
#       priority = self.form.priorityComboBox.itemData(index).toPyObject()
#
#       try:
#           self.item.priority = priority.get_ref()
#       except:
#           validation.errorMessage(self.dialog, "Priority must be specified")
#           return

#       index = self.form.goalLevelComboBox.currentIndex()
#       priority = self.form.goalLevelComboBox.itemData(index).toPyObject()
#
#       try:
#           self.item.goal_level = priority.get_ref()
#       except:
#           validation.errorMessage(self.dialog, "Goal level must be specified")
#           return

#       try:
#           self.item.remarks = converter.textToItems(
#               self.afefuc['project'],
#               unicode(self.form.remarksTextEdit.toPlainText().toUtf8(), "utf-8")
#           )
#       except:
#           validation.errorMessage(self.dialog, "Invalid reference in remarks")
#           return
#
#       try:
#           self.item.summary = converter.textToItems(
#               self.afefuc['project'],
#               unicode(self.form.summaryTextEdit.toPlainText().toUtf8(), "utf-8")
#           )
#       except:
#           validation.errorMessage(self.dialog, "Invalid reference in summary")
#           return

        # validate

        errors = validation.usecase(self.afefuc['project'], self.item, self.item_original is None, self.form)

        if errors:
            validation._show(self.dialog, errors)
            return
        if self.item_original:
            self.parent.model.updateItem((self.item_original, self.item))
        else:
            self.parent.model.insertItem((self.item_original, self.item))

        self.dialog.close()
   
    def clickedInsertStepMSButton(self):
        print "!!!"

        step = model.Step()
        step.setParent(self.item)

        print self.form.mainScenarioView.selectedIndexes()

        if len(self.form.mainScenarioView.selectedIndexes()) != 0:
            position = self.form.mainScenarioView.selectedIndexes()[0].row()

            self.modelMS.insertItem(step, position + 1)
        else:
            self.modelMS.insertItem(step)

    def clickedAddEventMSButton(self):
        if len(self.form.mainScenarioView.selectedIndexes()) == 2:
            position = self.form.mainScenarioView.selectedIndexes()[0].row()

            self.modelEV.insertEvent(position)

    def clickedDeleteMSButton(self):
        if len(self.form.mainScenarioView.selectedIndexes()) == 2:
            position = self.form.mainScenarioView.selectedIndexes()[0].row()

            self.modelMS.removeItem(position)

    def clickedMoveUpMSButton(self):
        if len(self.form.mainScenarioView.selectedIndexes()) == 2:
            position = self.form.mainScenarioView.selectedIndexes()[0].row()

            self.modelMS.movePositionUp(position)

    def clickedMoveDownMSButton(self):
        if len(self.form.mainScenarioView.selectedIndexes()) == 2:
            position = self.form.mainScenarioView.selectedIndexes()[0].row()

            self.modelMS.movePositionDown(position)

    def clickedInsertStepEvButton(self):
        if len(self.form.eventsView.selectedIndexes()) == 2:
            position = self.form.eventsView.selectedIndexes()[0].row()

            self.modelEV.insertStep(position)

    def clickedDeleteEvButton(self):
        if len(self.form.eventsView.selectedIndexes()) == 2:
            position = self.form.eventsView.selectedIndexes()[0].row()

            self.modelEV.removeItem(position)

    def clickedPropertiesEvButton(self):
        if len(self.form.eventsView.selectedIndexes()) == 2:
            position = self.form.eventsView.selectedIndexes()[0].row()

            EventPropertiesFormWrapper(
                    self,
                    self.afefuc['project'],
                    position
            ).show()

    def clickedMoveUpEvButton(self):
        if len(self.form.eventsView.selectedIndexes()) == 2:
            position = self.form.eventsView.selectedIndexes()[0].row()

            self.modelEV.movePositionUp(position)

    def clickedMoveDownEvButton(self):
        if len(self.form.eventsView.selectedIndexes()) == 2:
            position = self.form.eventsView.selectedIndexes()[0].row()

            self.modelEV.movePositionDown(position)

    def editingFinishedTitleEdit(self):
        try:
            self.item.title = converter.textToItems(
                self.afefuc['project'],
                unicode(
                        self.form.titleEdit.text().toUtf8(),
                        'utf-8'
                ),
                (
                        self.item_original,
                        self.item
                )
            )
        except ValueError:
            validation.errorMessage(None, "Invalid reference in title")
            return

        self.modelEV.reset()
        self.modelMS.reset()

    def editingFinishedIdEdit(self):
        self.item.identifier = unicode(self.form.idEdit.text().toUtf8(), 'utf-8')

        self.modelEV.reset()
        self.modelMS.reset()

    def clickedInsertTriButton(self):
        condition = model.Trigger()

        if len(self.form.triView.selectedIndexes()) != 0:
            position = self.form.triView.selectedIndexes()[0].row()

            self.form.triView.model().insertItem(condition, position)
        else:
            self.form.triView.model().insertItem(condition)

    def clickedDeleteTriButton(self):
        if len(self.form.triView.selectedIndexes()) == 2:
            position = self.form.triView.selectedIndexes()[0].row()

            self.form.triView.model().removeItem(position)

    def clickedMoveUpTriButton(self):
        if len(self.form.triView.selectedIndexes()) == 2:
            position = self.form.triView.selectedIndexes()[0].row()

            self.form.triView.model().movePositionUp(position)

    def clickedMoveDownTriButton(self):
        if len(self.form.triView.selectedIndexes()) == 2:
            position = self.form.triView.selectedIndexes()[0].row()

            self.form.triView.model().movePositionDown(position)

    def clickedInsertPrCButton(self):
        condition = model.PreCondition()

        if len(self.form.prcView.selectedIndexes()) != 0:
            position = self.form.prcView.selectedIndexes()[0].row()

            self.form.prcView.model().insertItem(condition, position)
        else:
            self.form.prcView.model().insertItem(condition)

    def clickedDeletePrCButton(self):
        if len(self.form.prcView.selectedIndexes()) == 2:
            position = self.form.prcView.selectedIndexes()[0].row()

            self.form.prcView.model().removeItem(position)

    def clickedMoveUpPrCButton(self):
        if len(self.form.prcView.selectedIndexes()) == 2:
            position = self.form.prcView.selectedIndexes()[0].row()

            self.form.prcView.model().movePositionUp(position)

    def clickedMoveDownPrCButton(self):
        if len(self.form.prcView.selectedIndexes()) == 2:
            position = self.form.prcView.selectedIndexes()[0].row()

            self.form.prcView.model().movePositionDown(position)

    def clickedInsertPoCButton(self):
        condition = model.PostCondition()

        if len(self.form.pocView.selectedIndexes()) != 0:
            position = self.form.pocView.selectedIndexes()[0].row()

            self.form.pocView.model().insertItem(condition, position)
        else:
            self.form.pocView.model().insertItem(condition)

    def clickedDeletePoCButton(self):
        if len(self.form.pocView.selectedIndexes()) == 2:
            position = self.form.pocView.selectedIndexes()[0].row()

            self.form.pocView.model().removeItem(position)

    def clickedMoveUpPoCButton(self):
        if len(self.form.pocView.selectedIndexes()) == 2:
            position = self.form.pocView.selectedIndexes()[0].row()

            self.form.pocView.model().movePositionUp(position)

    def clickedMoveDownPoCButton(self):
        if len(self.form.pocView.selectedIndexes()) == 2:
            position = self.form.pocView.selectedIndexes()[0].row()
            self.form.pocView.model().movePositionDown(position)



