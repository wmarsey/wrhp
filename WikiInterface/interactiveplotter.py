from __future__ import division
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from operator import itemgetter
import copy

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

SLIDERS = ['Maths',
           'Citations',
           'Files / Images',
           'Links',
           'Structure',
           'Normal',
           'Gradient']
VIEWS = ['Trajectory',
         'Edit rewards by user',
         'Edit reqards by revision']

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.getdata()

        # self.textbox.setText('1 2 3 4')
        self.on_draw()
                     
    def getdata(self):
        self.data = [
            {'revid':343,
             'Maths':23,
             'Citations':34,
             'Files / Images':1,
             'Links':344,
             'Structure':45,
             'Normal':45,
             'Gradient':20,
             'user':'user1',
             'trajectory':50,
             'timestamp':100},
            {'revid':54677,
             'Maths':22,
             'Citations':30,
             'Files / Images':43,
             'Links':23,
             'Structure':45,
             'Normal':56,
             'Gradient':1,
             'user':'user2',
             'trajectory':100,
             'timestamp':2},
            {'revid':52677,
             'Maths':23,
             'Citations':34,
             'Files / Images':1,
             'Links':344,
             'Structure':45,
             'Normal':45,
             'Gradient':90,
             'user':'user2',
             'trajectory':0,
             'timestamp':200}
            ]

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
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        QMessageBox.information(self, "Click!", msg)
    
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
            return zip(*data)
        elif selection == 2: #by revid
            for d in self.data:

                dsum = 0
                for w,v in weights.iteritems(): ##sums normal weights
                    if w != 'Gradient':
                        dsum += (d[w] * v)

                for ld in data: ##appends to existing
                    if ld[0] == d['revid']:
                        ld[1] += dsum
                        ld[2].append(d['user'])
                        break
                else:
                    data.append([d['revid'], dsum, d['user']])

                    
            data = [[x[0],
                     x[1],
                     x[2]] for x in data]
            total = sum([x[1] for x in data])
            print "total", total
            data = [[x[0],
                     x[1] / total,
                     x[2]] for x in data]   

            return zip(*data)
        else:
            pass

        #reorder

        #

    def on_draw(self):
        """ 
        Redraws the figure
        """
        # weights = {'Maths':1,
        #            'Citations':1,
        #            'Files / Images':1,
        #            'Links':1,
        #            'Structure':1,
        #            'Normal':1,
        #            'Gradient':1,}

        weights = {}

        for i in range(0,len(self.sliders),2):
            print self.sliders[i].text(), self.sliders[i+1].value()
            weights.update({str(self.sliders[i].text()):self.sliders[i+1].value()})
            
        print weights

        selection = 0 
        for i,r in enumerate(self.radios):
            if r.isChecked():
                selection = i
                break
        
        if selection == 0:
            labels, heights, timestamps = self.recalculate(weights, selection)
            print labels, "|", heights, "|", timestamps
        else:
            labels, heights, revids = self.recalculate(weights, selection)
            print labels, "|", heights, "|", revids

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        #self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.bar(
            left=xrange(len(heights)), 
            height=heights, 
            #width=self.sliders[1].value() / 100.0, ##grab slider values!!
            align='center', 
            alpha=0.44,
            picker=5)
        self.axes.set_xticks(np.arange(len(self.data)))
        self.axes.set_xticklabels(labels)
        if selection:
            self.axes.set_ylim(bottom=0,top=1)

        # barheights = [1,2,3,4,5,6]
        # barlabels = ["hello","f","g","t","y","u"]
        # h = self.axes.bar(xrange(len(barheights)), 
        #                   barheights, 
        #                   label=barlabels, 
        #                   width=self.sliders[1].value() / 100.0) ##grab slider values!!)
        # xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
        # self.axes.get_yaxis().get_major_formatter().set_scientific(False)
        # plt.xlabel('xaxisname')
        # plt.ylabel('yaxisname')
        # plt.title('title')
        # plt.xticks(xticks_pos, 
        #            barlabels, 
        #            rotation=90, 
        #            ha='center')
        
        self.canvas.draw()
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi, tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # # Other GUI controls
        # # 
        # self.textbox = QLineEdit()
        # self.textbox.setMinimumWidth(200)
        # self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)

        self.radios = []
        for v in VIEWS:
            theradio = QRadioButton(v)
            theradio.toggled.connect(self.on_draw)
            self.radios.append(theradio)
        self.radios[0].setChecked(True)
        
        ##SHOULD BE UNNECCESSARY
        # self.draw_button = QPushButton("&Draw")
        # self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        ##TICK BUTTON SHOW GRID
        # self.grid_cb = QCheckBox("Show &Grid")
        # self.grid_cb.setChecked(False)
        # self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.sliders = []
        for s in SLIDERS:
            thelabel = QLabel(s)
            theslider = QSlider(Qt.Horizontal)
            theslider.setRange(1, 100)
            theslider.setValue(20)
            theslider.setTracking(True)
            theslider.setTickPosition(QSlider.TicksBothSides)
            self.connect(theslider, SIGNAL('valueChanged(int)'), self.on_draw)
            self.sliders.append(thelabel)
            self.sliders.append(theslider)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in self.radios + self.sliders:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
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


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
