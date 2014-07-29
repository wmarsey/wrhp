import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from automaton import WikiInterface as wk
import csv

IMGBASE = 'img/'

class wikiDistance(QtGui.QMainWindow):
   
    def __init__(self):
        super(wikiDistance, self).__init__()
        self.dsktp = QtGui.QDesktopWidget()
        self.mainwidget = mainWidget(self) 
        self.setCentralWidget(self.mainwidget)
        self.initUI()
        
    def initUI(self):
        self.status('Ready')
        self.menu()
        self.toolbar()
        self.mainwidget.layout(search=True,
                               title="WikiDistance",
                               blurb="Begin by looking searching for a wikipedia page below:")

        self.style()

        self.setGeometry(*[e*0.75 for e in self.getScreensize()])
        self.center()
        
        self.setWindowTitle('Wikidistance')
        self.setWindowIcon(QtGui.QIcon('img/drawing.png'))        
        
        self.show()

    def status(self, message):
        self.statusBar().showMessage(message)

    def menu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.exitAction(True))

    def toolbar(self):
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.setMovable(False)
        self.toolbar.addAction(self.exitAction())

    def style(self):
        with open('styles/main.css','r') as cs:
            self.setStyleSheet(cs.read())
     
    # BUTTON ACTIONS
    def exitAction(self, short=False):
        exitAction = QtGui.QAction(QtGui.QIcon(IMGBASE + 'stop32.png'), '&Exit', self)        
        if short:
            exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        return exitAction

    # POSITIONING
    def getScreensize(self):
        rect = self.dsktp.availableGeometry()
        return rect.getRect()

    def center(self):
        qr = self.frameGeometry()
        cp = self.dsktp.availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class mainWidget(QtGui.QWidget):
    interface = None
    
    def __init__(self, parent):
        super(mainWidget, self).__init__(parent)
        self.parent = parent
        self.interface = wk()

    def layout(self,search=False,title=None,subtitle=None,blurb=None):
        # self.txtwdg = QtGui.QWidget(self) ##subwidget
        with open('styles/text.css','r') as cs:
            self.setStyleSheet(cs.read())
        
        grid = QtGui.QGridLayout()
        textLabels = []

        if title:
            qtitle = QtGui.QLabel(title)
            qtitle.setProperty('class','h1')
            qtitle.setObjectName('masthead')
            textLabels.append(qtitle)
        if subtitle:
            qsubt = QtGui.QLabel(subtitle)
            qsubt.setProperty('class','h2')
            textLabels.append(qsubt)
        if blurb:
            qblurb = QtGui.QLabel(blurb)
            qblurb.setProperty('class','p')
            textLabels.append(qblurb)
        
        r = 0            
        for l in textLabels:
            grid.addWidget(l, r, 1)
            grid.setRowMinimumHeight(r,5)
            grid.setRowStretch(r,0)
            r += 1
        
        grid.addWidget(self.formpart(search),3,1)
        grid.setRowMinimumHeight(3,5)
        grid.setRowStretch(3,0)

        grid.setColumnMinimumWidth(0,300)
        grid.setColumnMinimumWidth(2,300)
        grid.setAlignment(Qt.AlignTop)
        
        self.setLayout(grid) 

    def search(self, text):
        print text
        
        self.parent.status("Searching for article")
        self.interface.config(params={'page_titles': str(text),
                                      'domain':str(self.langslist.currentText())})
        result = self.interface.checktitle()
        self.parent.status("Page found." if result else "Page not found.")

    def formpart(self,search):
        textEditPairs = []
        self.frmwdg = QtGui.QWidget(self)
        with open('styles/form.css','r') as cs:
            self.frmwdg.setStyleSheet(cs.read())
        grid = QtGui.QGridLayout()

        qtext = None
        qlist = None

        if search:
            self.querytext = titleLineEdit(self)
            self.langslist = langsComboBox(self)
            
        grid.addWidget(self.querytext,0,0)
        grid.addWidget(self.langslist,0,1) 

        grid.setSpacing(0)
        grid.setAlignment(Qt.AlignTop)
        self.frmwdg.setLayout(grid)
        return self.frmwdg

class langsComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(langsComboBox,self).__init__(parent)
        self.settings()
        self.getitems()
        self.parent = parent

    def settings(self):
        delegate = QtGui.QStyledItemDelegate(self);
        self.setMaximumHeight(40)
        self.setItemDelegate(delegate)
        self.setCurrentIndex(0)

    def getitems(self):
        with open('wikiScraper/langs.csv','r') as langs:
            lread = csv.reader(langs, delimiter='\t')
            for l in lread:
                self.addItem(l[0])
                           
class titleLineEdit(QtGui.QLineEdit):
    firstfocus = False

    def __init__(self, parent=None):
        super(titleLineEdit,self).__init__(parent)
        self.settings()
        self.parent = parent    

    def settings(self):
        self.setText('Search for a title here')
        self.setAlignment(Qt.AlignCenter)
        self.setMaximumHeight(40)
        self.selectAll()
        
    def mousePressEvent(self, event):
        if self.firstfocus:
            return
        else:
            self.setText('')
            self.setAlignment(Qt.AlignCenter)
            self.firstfocus = True
            self.returnPressed.connect(self.sendToParent)

    def sendToParent(self):
        self.parent.search(self.text())
    
# class projectInterface:
    
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = wikiDistance()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()   
