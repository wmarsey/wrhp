import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from automaton import WikiInterface as wk
from wikipedia import search
from customWidgets import *

IMGBASE = '/homes/wm613/individual-project/WikiInterface/img/'

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
    def __init__(self, parent):
        super(mainWidget, self).__init__(parent)
        self.parent = parent
        self.interface = projectInterface()

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
        title = str(text)
        domain = str(self.langslist.currentText())
        self.parent.status("Searching for article")
        self.interface.config(title=title, domain=domain, check=True)
        self.connect( self.interface, QtCore.SIGNAL("resultsreturn"), self.testrespond)
        self.interface.start()
        
    def testrespond(self,results):
        print results
        check = results
        self.parent.status("Page found." if check else "Page not found.")
        if check:
            self.parent.status("Fetching and analysing article")
            self.interface.config(check=False)
            self.connect( self.interface, QtCore.SIGNAL("resultsreturn"), self.analysisrespond)
            self.interface.start()

    def analysisrespond(self,results):
        print results

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

class projectInterface(QtCore.QThread):
    wk = None
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.params = {'scrape_limit': -1,
                       'depth_limit': -1,
                       'page_titles': 'random',
                       'revids': 0,
                       'userids': 0,
                       'domain':None,
                       'weights':{'maths':0,
                                  'headings':0,
                                  'quotes':0,
                                  'files/images':0,
                                  'links':0,
                                  'citations':0,
                                  'normal':0}}
        self.flags = {'scrape': False,
                      'fetch': False,
                      'analyse': False,
                      'offline': False,
                      'weightsdefault' : True,
                      'plotshow': False}
        self.params['page_titles'] = "" 
        self.params['domain'] = ""
        self.check = None

    def __del__(self):
        self.wait()

    def config(self, title=None, domain=None, check=False):
        if self.wk:
            del self.wk
        if title:
            self.params['page_titles']=title
        if domain:
            self.params['domain']=domain
        self.wk = wk(self.params, self.flags)
        self.check = check
        
    def run(self):
        if self.check:
            self.emit(QtCore.SIGNAL("resultsreturn"), self.wk.checktitle())
            del self.wk
        else:
            self.emit(QtCore.SIGNAL("resultsreturn"), self.wk.analyse())
            del self.wk
        
    def autocomplete(self, word):
        results = self.wk.search(word)
        results[0] + results[1]
        return results[0] + results[1]

def main():  
    app = QtGui.QApplication(sys.argv)
    ex = wikiDistance()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()   
