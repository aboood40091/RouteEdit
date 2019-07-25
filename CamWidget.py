import struct

from PyQt5 import QtWidgets, QtGui

class CamEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.camEntries = []
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.scrollArea = QtWidgets.QScrollArea()
        self.camEntriesTable = CamEntryTable()

        # Default Widgets to disabled
        self.scrollArea.setDisabled(True)

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.camEntriesTable)

        self.layout.addWidget(self.scrollArea)

    def loadData(self, camData):
        self.camEntries = [camData[i:i+21] for i in range(0, len(camData), 21)]

        self.scrollArea.setDisabled(False)
        self.camEntriesTable.populateTable(self.camEntries)

    def closeData(self):
        self.camEntries = []
        self.camEntriesTable.clearTable()
        self.scrollArea.setDisabled(True)

    def saveEntryData(self):
       return self.camEntriesTable.save()


class CamEntryTable(QtWidgets.QTableWidget):
    def __init__(self):
        QtWidgets.QTableWidget.__init__(self)

        # Setup Table Properties
        self.setColumnCount(5)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Setup Header Bar
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Node'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('X Offset'))
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Y Offset'))
        self.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('Z Offset'))
        self.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem('Unkown'))

        # Hide Row Numbers
        self.verticalHeader().setVisible(False)

    def populateTable(self, camEntries):
        s = struct.Struct('<5s f f f I')

        for i in range(len(camEntries)):
            entryStruct = s.unpack(camEntries[i])

            self.insertRow(i)

            self.setCellWidget(i, 0, NameEditor(str(entryStruct[0], 'utf-8')))  # Node
            self.setCellWidget(i, 1, FloatEditor(float(entryStruct[1])))        # X Offset
            self.setCellWidget(i, 2, FloatEditor(float(entryStruct[2])))        # Y Offset
            self.setCellWidget(i, 3, FloatEditor(float(entryStruct[3])))        # Z Offset
            self.setCellWidget(i, 4, UnkEditor(int(entryStruct[4])))            # Unknown

    def clearTable(self):
        while self.rowCount() > 0:
            self.removeRow(0)

    def save(self):
        s = struct.Struct('<5s f f f I')
        entries = b''

        for i in range(self.rowCount()):
            entry = []
            entry.append(bytes(self.cellWidget(i, 0).text(), 'utf-8'))
            entry.append(self.cellWidget(i, 1).value())
            entry.append(self.cellWidget(i, 2).value())
            entry.append(self.cellWidget(i, 3).value())
            entry.append(self.cellWidget(i, 4).value())

            entries = entries + s.pack(*entry)

        return entries

class NameEditor(QtWidgets.QLineEdit):
    def __init__(self, val, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent=parent)

        self.setMaxLength(4)
        self.setText(val)

class FloatEditor(QtWidgets.QDoubleSpinBox):
    def __init__(self, val, parent=None):
        QtWidgets.QDoubleSpinBox.__init__(self, parent=parent)

        self.setRange(-1000000, 1000000)
        self.setDecimals(7)
        self.setValue(val)

class UnkEditor(QtWidgets.QSpinBox):
    def __init__(self, val, parent=None):
        QtWidgets.QSpinBox.__init__(self, parent=parent)

        self.setRange(0, 0x7FFFFFFF)
        self.setValue(val)
