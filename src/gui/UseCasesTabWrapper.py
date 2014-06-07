'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.ItemsTab import Ui_ItemsTab
from gui.UseCaseFormWrapper import UseCaseFormWrapper
from format import model
from utils import converter
from utils import clone
from utils import update

try:
        _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
        _fromUtf8 = lambda s: s

class UseCasesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, afefuc):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.afefuc = afefuc
        self.parent = parent

    def rowCount(self, index):
        return len(self.afefuc['project'].ucspec.usecases)

    def columnCount(self, parent):
        return 2

    def index(self, row, column, parent):
        if not parent.isValid():
            return self.createIndex(row, column, None)

    def data(self, index, role):
        column = index.column()

        if column == 0 and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.afefuc['project'].ucspec.usecases[index.row()].identifier)
        elif column == 1 and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(converter.itemsToText(self.afefuc['project'].ucspec.usecases[index.row()].title))

    def parent(self, index):
        return QtCore.QModelIndex()

    def removeItem(self, position):
        self.beginRemoveRows(QtCore.QModelIndex(), position, position);

        del(self.afefuc['project'].ucspec.usecases[position])

        self.endRemoveRows();

        return True;

    def insertItem(self, usecase):
        self.beginInsertRows(
                QtCore.QModelIndex(),
                self.rowCount(QtCore.QModelIndex()),
                self.rowCount(QtCore.QModelIndex())
        )

        self.afefuc['project'].ucspec.usecases.append(usecase[1])

        self.endInsertRows()

    def updateItem(self, usecase):
        counter = 0

        for i, uc in enumerate(self.afefuc['project'].ucspec.usecases):
            if uc is usecase[0]:
                counter = i
                update.usecase(self.afefuc['project'].ucspec.usecases[i], usecase[1])

                break

        self.emit(QtCore.SIGNAL("dataChanged(index, index)"),
                self.createIndex(counter, 0, None),
                self.createIndex(counter, 1, None)
        )

    def movePositionUp(self, position):
        if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
            return

        pos1 = position
        pos2 = position - 1

        (
                self.afefuc['project'].ucspec.usecases[pos1],
                self.afefuc['project'].ucspec.usecases[pos2]
        ) = (
                self.afefuc['project'].ucspec.usecases[pos2],
                self.afefuc['project'].ucspec.usecases[pos1]
        )

        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                self.createIndex(min(pos1, pos2), 0, None),
                self.createIndex(max(pos1, pos2), 1, None)
        )

class UseCasesTabWrapper():
    def __init__(self, parent, afefuc):
        self.parent = parent

        self.can = QtGui.QWidget(self.parent)
        self.tab = Ui_ItemsTab()
       
        self.afefuc = afefuc

    def show(self):

        self.tab.setupUi(self.can)
        self.model = UseCasesTableModel(self.tab.itemsView, self.afefuc)
        self.tab.itemsView.setModel(self.model)
        self.tab.itemsView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.tab.itemsView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.tab.itemsView.horizontalHeader().hide()
        self.tab.itemsView.verticalHeader().hide()
        self.tab.itemsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tab.itemsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        QtCore.QObject.connect(self.tab.addButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedAddButton)
        QtCore.QObject.connect(self.tab.deleteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteButton)
        QtCore.QObject.connect(self.tab.editButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedEditButton)
        QtCore.QObject.connect(self.tab.moveUpButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpButton)
        QtCore.QObject.connect(self.tab.moveDownButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownButton)

        self.parent.mainWindow.tabWidget.addTab(self.can, _fromUtf8("Use Cases"))

    def load(self):
        self.model.reset()
        

    def clickedAddButton(self):
        uc = model.UseCase()
        uc.setParent(self.afefuc['project'])

        UseCaseFormWrapper(self, self.afefuc, (None, uc)).show()

    def clickedDeleteButton(self):
        if len(self.tab.itemsView.selectedIndexes()) == 2:
            position = self.tab.itemsView.selectedIndexes()[0].row()

            self.model.removeItem(position)

    def clickedEditButton(self):
        if len(self.tab.itemsView.selectedIndexes()) == 2:
            position = self.tab.itemsView.selectedIndexes()[0].row()

            original = self.afefuc['project'].ucspec.usecases[position]

            uc = clone.usecase(original, self.afefuc['project'])
            uc.setParent(original.parent)

            UseCaseFormWrapper(self, self.afefuc, item = (original, uc)).show()

    def clickedMoveUpButton(self):
        if len(self.tab.itemsView.selectedIndexes()) == 2:
            position = self.tab.itemsView.selectedIndexes()[0].row()

            self.model.movePositionUp(position)
            self.tab.itemsView.selectRow(position - 1)

    def clickedMoveDownButton(self):
        if len(self.tab.itemsView.selectedIndexes()) == 2:
            position = self.tab.itemsView.selectedIndexes()[0].row()

            self.model.movePositionUp(position + 1)
            self.tab.itemsView.selectRow(position + 1)
