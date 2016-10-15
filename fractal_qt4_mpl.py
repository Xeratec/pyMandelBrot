#!/usr/bin/python
'''
@file fractal_qt4_mpl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with PyQt4 and Matplotlip
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import log10

from matplotlib.pyplot import *
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from fractal_func import mandelbrot_v2 as mandelbrot

### Static Config ####
re_min = 0.385
re_max = 0.395
im_min = 0.135
im_max = 0.145

max_betr = 2
max_iter = 100
res = 400
cont = True
######################

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Mandelbrot Set')
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        #
        # Initialize textbox values
        #
        self.textbox_re_min.setText(str(re_min))
        self.textbox_re_max.setText(str(re_max))
        self.textbox_im_min.setText(str(im_min))
        self.textbox_im_max.setText(str(im_max))
        self.textbox_max_iter.setText(str(max_iter))
        
        #
        # Render mandelbrot set
        #
        self.draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self,
                        'Save file', '',
                        file_choices))
        if path:
            self.canvas.print_figure(path)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    #
    # Display infos about application
    #
    def on_about(self):
        msg = """ Mandelbrot Set Generator with PyQt4 and Matplotlib:
        
         * Click left mouse button and drag to zoom
         * Enter new values for Mandelbrot set
         * Show or hide the grid
         * Save the plot to a file using the File menu
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    #
    # Calculates mandelbrot set and updates mpl plot
    #
    def draw(self):
        """ Redraws the figure
        """
        # Grap values from textboxes
        re_min = float(unicode(self.textbox_re_min.text()))
        re_max = float(unicode(self.textbox_re_max.text()))
        im_min = float(unicode(self.textbox_im_min.text()))
        im_max = float(unicode(self.textbox_im_max.text()))
        max_iter = int(unicode(self.textbox_max_iter.text()))
        
        # Calculate mandelbrot set
        (img, calc_t) = mandelbrot(re_min, re_max, im_min, im_max, max_betr, max_iter, res, cont) 
        
        # Show calculation time in statusbar
        self.status_text.setText("Calculation Time: %0.3fs" % calc_t)
    
        # Load data to mpl plot
        self.axes.imshow(img.T, origin="lower left", cmap='jet', extent=[re_min, re_max, im_min, im_max])
        self.axes.set_xlabel("Re(c)")
        self.axes.set_ylabel("Im(c)")
        
        # Show/hide grid
        self.axes.grid(self.grid_cb.isChecked())
        if self.grid_cb.isChecked():
            self.axes.grid(linewidth=1, linestyle='-')
        # Align layout and redraw plot   
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def line_select_callback(self, eclick, erelease):
        # eclick and erelease are the press and release events
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Only zoom with right mouse click
        if eclick.button == 1:
            # Check for valid coordinates            
            if (x1!=None and y2!=None and x1 != None and y1!= None):
                self.xmin = min(x1, x2)
                self.xmax = max(x1, x2)
                self.ymin = min(y1, y2)
                self.ymax = max(y1, y2)
                # Save array with relative values
                self.xy = [self.xmax - self.xmin, self.ymax - self.ymin]
                
                # Calculate precision in decimal digits
                for v in self.xy:
                    if v <= 1:
                        self.decimals = round(log10(1 / v)) + 2
                
                # Round values with calculated precision
                re_min = round(self.xmin, int(self.decimals))
                re_max = round(self.xmax, int(self.decimals))
                im_min = round(self.ymin, int(self.decimals))
                im_max = round(self.ymax, int(self.decimals))
            
                # Update textbos values
                self.textbox_re_min.setText(str(re_min))
                self.textbox_re_max.setText(str(re_max))
                self.textbox_im_min.setText(str(im_min))
                self.textbox_im_max.setText(str(im_max))
                
                # Calculate and draw new mandelbrot set
                self.draw()
            
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Add sublot to figure
        self.axes = self.fig.add_subplot(111)
        
        # Create zoom event handler
        self.RS = RectangleSelector(self.axes, self.line_select_callback,
                           drawtype='box', useblit=True,
                           button=[1, 3],  # don't use middle button
                           spancoords='data')                
        
        # Other GUI controls
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.draw)
        
        self.textbox_re_min = QLineEdit()
        self.textbox_re_min.setMinimumWidth(55)
        
        self.textbox_re_max = QLineEdit()
        self.textbox_re_max.setMinimumWidth(55)
        
        self.textbox_im_min = QLineEdit()
        self.textbox_im_min.setMinimumWidth(55)
        
        self.textbox_im_max = QLineEdit()
        self.textbox_im_max.setMinimumWidth(55)
        
        self.textbox_max_iter = QLineEdit()
        self.textbox_max_iter.setMinimumWidth(55)
        
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        for w in [  self.textbox_re_min, self.textbox_re_max, self.textbox_im_min, self.textbox_im_max, self.textbox_max_iter,
                    self.draw_button, self.grid_cb]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        
        vbox.addLayout(hbox) 
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)      
    
    def create_status_bar(self):
        self.status_text = QLabel("Ready")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self): 
        # -- Menu Structure --
        # File
        #     Save plot (Ctrl+S)
        #     Quit (Ctrl+Q)
        # Help
        #    About (F1)
        #  
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
            tip='About the application')
        
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
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
