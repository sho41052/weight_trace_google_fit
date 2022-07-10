import logging
import sys

from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QStackedWidget, QMenu, QActionGroup

from scripts.weight_fat_graph import weight_fat_graph
from scripts.weight_fat_input import weight_fat_input

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # set title
        self.setWindowTitle('Google fit weight / fat')

        # MenuBar
        menubar = self.menuBar()

        # File Menu
        fileMenu = menubar.addMenu('File')
        # Save pic in File
        savePicAction = QAction('Save picture', self)
        savePicAction.triggered.connect(self.save_picture)
        fileMenu.addAction(savePicAction)
        # Update graph data
        updateGraphData = QAction('Update graph', self)
        updateGraphData.triggered.connect(self.update_graph_data)
        fileMenu.addAction(updateGraphData)
        # Exit in File
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        # Mode Menu
        '''
        https://stackoverflow.com/questions/48447053/one-qaction-checkable-at-time-in-qmenu
        '''
        modeType = QMenu('Mode', self)
        group = QActionGroup(modeType)
        texts = ['graph', 'insert']
        for text in texts:
            action = QAction(text, modeType, checkable=True, checked=(text == texts[0]))
            modeType.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        group.triggered.connect(self.mode_change)
        menubar.addMenu(modeType)

        # Modes in Mode
        self.widget_weight_fat = weight_fat_graph()
        self.widget_weight_input = weight_fat_input()

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.widget_weight_input)
        self.Stack.addWidget(self.widget_weight_fat)
        self.Stack.setCurrentIndex(1)
        self.resize(1000, 600)
        self.setCentralWidget(self.Stack)

        self.show()

    def mode_change(self, mode):
        if mode.text() == 'insert':
            self.Stack.setCurrentIndex(0)
            self.resize(100, 100)
        elif mode.text() == 'graph':
            self.Stack.setCurrentIndex(1)
            self.resize(1000, 600)
        else:
            '''
            New feature
            '''

    def save_picture(self):
        file_name = str(datetime.now().date()) + '_' + str(datetime.now().time())
        self.widget_weight_fat.save_picture(file_name)
        print(file_name)

    def update_graph_data(self):
        self.widget_weight_fat.update_graph_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
