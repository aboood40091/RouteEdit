import re
from PyQt5 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt


class RouteEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.fileSelector = QtWidgets.QComboBox()
        self.scrollArea = QtWidgets.QScrollArea()
        self.routeEntries = RouteEntryTable()
        self.addRowButton = QtWidgets.QPushButton('Insert Row')
        self.delRowButton = QtWidgets.QPushButton('Remove Row')
        self.importButton = QtWidgets.QPushButton('Import')
        self.exportButton = QtWidgets.QPushButton('Export')

        # Add Icons
        self.addRowButton.setIcon(QtGui.QIcon('RouteEditData/icons/plus.png'))
        self.delRowButton.setIcon(QtGui.QIcon('RouteEditData/icons/minus.png'))
        self.importButton.setIcon(QtGui.QIcon('RouteEditData/icons/import.png'))
        self.exportButton.setIcon(QtGui.QIcon('RouteEditData/icons/export.png'))

        # Default Widgets to disabled
        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.routeEntries)

        # Setup Signals
        self.fileSelector.currentIndexChanged.connect(self.fileIndexChanged)
        self.addRowButton.pressed.connect(self.addRow)
        self.delRowButton.pressed.connect(self.delRow)
        self.importButton.pressed.connect(self.importData)
        self.exportButton.pressed.connect(self.exportData)

        # add widgets to layout
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addWidget(self.fileSelector, 1, Qt.AlignVCenter)
        topLayout.addWidget(self.importButton, 0, Qt.AlignVCenter)
        topLayout.addWidget(self.exportButton, 0, Qt.AlignVCenter)

        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.addWidget(self.addRowButton, 1, Qt.AlignVCenter)
        bottomLayout.addWidget(self.delRowButton, 1, Qt.AlignVCenter)
        bottomLayout.insertStretch(2, 2)

        self.layout.addLayout(topLayout)
        self.layout.addWidget(self.scrollArea)
        self.layout.addLayout(bottomLayout)

    def loadData(self, archiveContents):
        self.archiveContents = archiveContents

        QtCore.QObject.blockSignals(self.fileSelector, True)

        # Add elements to file selector drop-down
        for file in self.archiveContents:
            self.fileSelector.addItem(str(file.name)[5:-4])

        QtCore.QObject.blockSignals(self.fileSelector, False)

        # Enable the Ui
        self.scrollArea.setDisabled(False)
        self.fileSelector.setDisabled(False)

        # load initial file
        self.fileIndexChanged()

    def closeData(self):
        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""

        self.routeEntries.clearTable()

        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        self.fileSelector.clear()

    def fileIndexChanged(self):
        # store the currently selected file's name
        self.selectedFile = "route" + self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.routeEntries.clearTable()
            self.loadSelectedFile()
        else:
            self.loadSelectedFile()

    def loadSelectedFile(self):

        dataArray = []

        # load the data for the file the user selected
        for file in self.archiveContents:
            if file.name == self.selectedFile:
                data = file.data
                data = data.decode('shiftjis')

                # split data by row
                rows = str(data).split()

                # split rows elements but don't break substrings
                for row in rows:
                    row = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', row)
                    dataArray.append(row)

                # create a route entry container
                self.routeEntries.populate(dataArray)

                self.fileLoaded = True
                self.currentLoadedFile = self.selectedFile

    def storeChanges(self):
        data = self.routeEntries.saveContents()
        data = data.encode('shiftjis')

        for file in self.archiveContents:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

    def getArchiveContents(self):
        self.storeChanges()
        return self.archiveContents

    def addRow(self):
        self.routeEntries.addRow()

    def delRow(self):
        self.routeEntries.delRow()

    def importData(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Import file', '', 'csv files (*.csv)')[0]

        if fileName == '':
            return

        with open(fileName, 'rb') as f:
            data = f.read()

        self.routeEntries.saveContents()

        for file in self.archiveContents:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

        self.routeEntries.clearTable()
        self.loadSelectedFile()

    def exportData(self):
        file = self.routeEntries.saveContents()
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Export file', '' +self.currentLoadedFile, 'csv files (*.csv)')[0]

        if path == '':
            return

        with open(path, 'wb+') as f:
            f.write(file.encode('shiftjis'))


class RouteEntryTable(QtWidgets.QTableWidget):
    def __init__(self):
        QtWidgets.QTableWidget.__init__(self)

        # Setup Table Properties
        self.setColumnCount(2)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Setup Header Bar
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Path"))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Type"))

        # Hide Row Numbers
        self.verticalHeader().setVisible(False)

    def populate(self, dataArray):
        i = 0
        # Iterate through each entry in the data array
        while i < len(dataArray):
            pos = self.rowCount()
            # Create a row for each entry in the array
            self.insertRow(pos)
            # Populate the new row with the contents of that entry in the array
            self.setItem(pos, 0, QtWidgets.QTableWidgetItem(dataArray[i][0]))  # Path
            self.setCellWidget(pos, 1, TypeEditor(dataArray[i][1]))          # Type
            i += 1

    def addRow(self):
        self.insertRow(self.currentRow()+1)

        # Initialise the row
        self.setItem(self.currentRow()+1, 0, QtWidgets.QTableWidgetItem())  # Path
        self.setCellWidget(self.currentRow()+1, 1, TypeEditor())          # Type

    def delRow(self):
        self.removeRow(self.currentRow())

    def saveContents(self):
        outData = []

        row = 0
        # Iterate through each row of the table
        while row < self.rowCount():
            rowData = []
            rowData.append(self.item(row, 0).text())
            rowData.append(self.cellWidget(row, 1).getValue())

            rowString = ','.join(rowData) + ','
            outData.append(rowString)
            row += 1

        outString = "\r\n".join(outData) + "\r\n"
        return outString

    def clearTable(self):
        while self.rowCount() > 0:
            self.removeRow(0)


class TypeEditor(QtWidgets.QComboBox):
    def __init__(self, data=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Create a dictionary to translate the types names from jp to english
        self.types = {}
        with open('RouteEditData/Types.txt', 'rt', encoding="utf-8-sig") as f:
            for line in f:
                (jp, eng) = line.split(':')
                eng = str(eng).strip('\n')
                self.types[jp] = eng

        # Add translated types names to the combobox
        for jp, eng in self.types.items():
            self.addItem(eng)

        if data is not None:
            self.getIndexByName(data)

    def getIndexByName(self, data):
        items = sorted(list(self.types.items()), key=lambda k: len(k[0]))
        for jp, eng in items:
            if jp == data:
                self.setCurrentIndex(self.findText(eng))
                break

        else:
            raise Exception("Unknown Type: %s" % data)

    def getValue(self):
        for jp, eng in self.types.items():
            if eng == self.currentText():
                return jp
