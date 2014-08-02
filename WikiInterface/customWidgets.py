from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
import csv

PROJBASE = '/homes/wm613/individual-project/WikiInterface/'

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
        with open(PROJBASE + 'wikiScraper/langs.csv','r') as langs:
            lread = csv.reader(langs, delimiter='\t')
            for l in lread:
                self.addItem(l[0])


class DictionaryCompleter(QtGui.QCompleter):
    def __init__(self, parent=None):
        words = []
        try:
            f = open("/usr/share/dict/words","r")
            for word in f:
                words.append(word.strip())
            f.close()
        except IOError:
            print "dictionary not in anticipated location"
        QtGui.QCompleter.__init__(self, words, parent)

class WikiCompleter(QtGui.QCompleter):
    def __init__(self, parent=None):
        words = []
        try:
            f = open("/usr/share/dict/words","r")
            for word in f:
                words.append(word.strip())
            f.close()
        except IOError:
            print "dictionary not in anticipated location"
        QtGui.QCompleter.__init__(self, words, parent)
        
class titleLineEdit(QtGui.QLineEdit):
    firstfocus = False

    # def __init__(self, parent=None):
    #     super(titleLineEdit,self).__init__(parent)
    #     self.settings()
    #     self.parent = parent    

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

    def __init__(self, parent=None):
        super(titleLineEdit, self).__init__(parent)
        self.settings()
        self.completer = None
        self.parent = parent
        # self.moveCursor(QtGui.QTextCursor.End)
        self.setCompleter(DictionaryCompleter())
        self.show()
    
    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return
        
        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseSensitive)
        self.completer = completer
        self.connect(self.completer,
                     QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.text()
        extra = (completion.length() -
                 self.completer.completionPrefix().length())
        tc.append(completion.right(extra))
        self.setText(tc)
        
    def textUnderCursor(self):
        return self.text()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtGui.QLineEdit.focusInEvent(self, event)

    # def updateCompletion:    

    def keyPressEvent(self, event):
        # if len(self.text()) > 3:
        #     self.updateCompletion()
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-E been pressed??
        isShortcut = (event.modifiers() == Qt.ControlModifier and
                      event.key() == Qt.Key_E)
        if (not self.completer or not isShortcut):
            QtGui.QLineEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (Qt.ControlModifier ,
                                            Qt.ShiftModifier)
        if ctrlOrShift and event.text().isEmpty():
            # ctrl or shift key on it's own
            return

        eow = QtCore.QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and
                       not ctrlOrShift)

        completionPrefix = self.textUnderCursor()

        if (not isShortcut and (hasModifier or event.text().isEmpty() or
                                completionPrefix.length() < 3 or
                                eow.contains(event.text().right(1)))):
            self.completer.popup().hide()
            return

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(
                self.completer.completionModel().index(0,0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## popup it up!

    def sendToParent(self):
        self.parent.search(self.text())
