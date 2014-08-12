from __future__ import division
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import webbrowser

from operator import itemgetter
import copy

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from markdown import markdown
#from textile import textile
import webbrowser
import database as db

BASE = '/homes/wm613/individual-project/WikiInterface/'

SLIDERS = ['Maths',
           'Citations',
           'Files / Images',
           'Links',
           'Structure',
           'Normal',
           'Gradient']
VIEWS = ['Trajectory',
         'Edit rewards by user',
         'Edit rewards by revision']

class RevisionPreview(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('Revision preview')
        self.layout = QVBoxLayout()
        self.view = QWebView()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

    def loadHTML(self):
        dtb = db.Database()
        pageid, domain = dtb.getrandom()
        revid = dtb.getyoungestrev(pageid)

        url = 'http://' + domain + '.wikipedia.org/w/index.php?oldid=' + revid

        # content = dtb.getrevcontent(revid[0][0], domain)
        # html = markdown(content.decode('utf-8'), 
        #                 extensions=['footnotes',
        #                             'abbr',
        #                             'attr_list',
        #                             'tables',
        #                             'codehilite',
        #                             'smart_strong',
        #                             'meta',
        #                             'nl2br',
        #                             'sane_lists',
        #                             'toc',
        #                             'wikilinks',
        #                             'headerid']
        #                 )

        # print html
        # self.view.setHtml(html)
        self.show()

class Plotter(QMainWindow):
    def __init__(self, parent=None, data=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.graphselection = -1

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.data = data

        self.on_draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ AOUT MESSAGE
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_pick(self, event):        
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        #
        
        num = event.artist.get_x()

        if self.graphselection == 0:
            pass
        elif self.graphselection == 1:
            pass 
        elif self.graphselection == 2:
            pass
        
        box_points = event.artist.get_bbox().get_points()
        box_label = event.artist.get_label()
        height = event.artist.get_height()
        msg = "You've clicked on a bar with important bit:\n %s" % num
        QMessageBox.information(self, "Click!", msg)
        
        # dtb = db.Database()
        # pageid, domain = dtb.getrandom()
        # revid = dtb.getyoungestrev(pageid)
        # url = 'http://' + domain + '.wikipedia.org/w/index.php?oldid=' + str(revid[0][0])
        # webbrowser.open(url)
    
    def recalculate(self, weights, selection):
        #group into list of tuples
        data = []
        if selection == 0: #trajectory
            for d in self.data:
                data.append((d['revid'],d['trajectory'],d['timestamp']))
            data = sorted(data, key=itemgetter(2))
            return zip(*data)
        elif selection == 1: #by user
            for d in self.data:
                dsum = 0
                
                for w,v in weights.iteritems(): ##sums normal weights
                    if w != 'Gradient': 
                        dsum += (d[w] * v)
                
                for ld in data: ##appends to existing
                    if ld[0] == d['user']:
                        ld[1] += dsum
                        ld[2].append(d['revid'])
                        break
                else:
                    data.append([d['user'], dsum, [d['revid']]])

            total = sum([x[1] for x in data])
            data = [[x[0],
                     x[1] / total,
                     x[2]] for x in data]   

            data = sorted(data, key=itemgetter(1))
            
            return zip(*data)
        elif selection == 2: #by revid
            for d in self.data:
                dsum = 0
                for w,v in weights.iteritems(): ##sums normal weights
                    if w != 'Gradient':
                        dsum += (d[w] * v)
                dsum += (d['Gradient'] * weights['Gradient'] * 100)
                data.append([d['revid'], dsum, d['user']])
                    
            data = [[x[0],
                     x[1],
                     x[2]] for x in data]
            total = sum([x[1] for x in data])
            data = [[x[0],
                     x[1] / total,
                     x[2]] for x in data]   

            data = sorted(data, key=itemgetter(1))

            return zip(*data)
        else:
            pass

    def on_draw(self):
        """ 
        Redraws the figure
        """
        weights = {}

        oldselection = self.graphselection

        self.graphselection = 0
        for i,r in enumerate(self.radios):
            if r.isChecked():
                self.graphselection = i
                break
        if oldselection and self.graphselection == 0:
            self.slidercontrol(-1)
        elif oldselection == 0 and self.graphselection:
            self.slidercontrol(1)

        for i in range(0,len(self.sliders),2):
            weights.update({str(self.sliders[i].text()):self.sliders[i+1].value()})
                    
        if self.graphselection == 0:
            labels, heights, timestamps = self.recalculate(weights, 
                                                           self.graphselection)
        else:
            labels, heights, revids = self.recalculate(weights, 
                                                       self.graphselection)
        if self.graphselection == 1:
            labels = [l.decode('utf-8') for l in labels]

        # clear the axes and redraw the plot anew
        #       
        
        self.axes.clear() 
        self.axes.bar(
            left=xrange(len(heights)), 
            height=heights,
            align='center', 
            alpha=0.44,
            picker=5)
        self.axes.set_xticks(np.arange(len(self.data)))
        self.axes.set_xticklabels(labels,
                                  rotation=90,
                                  ha='center')
        
        if self.graphselection:
            self.axes.set_ylim(bottom=0,top=1)
        self.axes.set_xlim(left=0, right=len(heights))

        self.canvas.draw()
    
    def slidercontrol(self, direction):
        for i in range(1,len(self.sliders),2):
            if direction < 0:
                self.sliders[i].setEnabled(False)
            else:
                self.sliders[i].setEnabled(True)

    def create_main_frame(self):
        self.main_frame = QWidget()

        with open(BASE + 'styles/main.css','r') as cs:
            self.setStyleSheet(cs.read())

        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi, tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes = self.fig.add_subplot(111)
        
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        self.radios = []
        for v in VIEWS:
            theradio = QRadioButton(v)
            theradio.toggled.connect(self.on_draw)
            self.radios.append(theradio)
        self.radios[0].setChecked(True)
        
        
        self.sliders = []
        style = ""
        with open(BASE + 'styles/slider.css','r') as cs:
            style = cs.read()
        for s in SLIDERS:
            thelabel = QLabel(s)
            theslider = QSlider(Qt.Horizontal)
            theslider.setRange(1, 100)
            theslider.setValue(20)
            theslider.setTracking(True)
            theslider.setTickPosition(QSlider.TicksBothSides)
            theslider.setEnabled(False)
            theslider.valueChanged.connect(self.on_draw)
            theslider.setStyleSheet(style)
            self.sliders.append(thelabel)
            self.sliders.append(theslider)
                
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in self.radios + self.sliders:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
            
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        #vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        #self.status_text = QLabel("This is a demo")
        #self.statusBar().addWidget(self.status_text, 1)
        pass
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, 
                      icon=None, tip=None, checkable=False, 
                      signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

def IPlot(data):
    app = QApplication(sys.argv)
    form = Plotter(data=data)
    form.show()
    app.exec_()

def main():
    app = QApplication(sys.argv)
    form = Plotter()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
