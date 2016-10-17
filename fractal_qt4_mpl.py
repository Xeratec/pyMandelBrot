#!/usr/bin/python
'''
@file fractal_qt4_mpl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with PyQt4 and Matplotlip
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import *
from matplotlib.widgets import RectangleSelector
from numpy import log10

from fractal_func import mandelbrot
from gtk._gtk import Alignment


### Static Config ####
re_min = 0.385
re_max = 0.395
im_min = 0.135
im_max = 0.145

max_betr = 2
max_iter = 100      
res = 400  # X Resolution
cont = True  # Show continual color
norm = True  # Normalize Values
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
        self.setMinimumWidth(620)
        self.resize(620, 460)
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
        msg = """Mandelbrot Set Generator:
        
    ### Features ###
     * Click left mouse button and drag to zoom
     * Enter custom values for ReMin, ReMin, ImMin and ImMax 
     * Show or hide the grid
     * Save the plot to a file using the File menu
     * De-/activate continuous color spectrum
     * De-/activate normalized values
     
     ### Used Libraries ###
     * PyQt4
     * Matplotlib
     
     ### Author ###
     Made by Philip Wiese
     info@maketec.ch
     16. Oktober 2016
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    #
    #
    #
    def statusbar_coord(self, event):
        # Show coordinates time in statusbar
        if (event.xdata is not None and event.ydata is not None):
            self.coord_text.setText("Re(c): % 7f, Im(c) % 7f" % (event.xdata, event.ydata))
    
    #
    # Calculates mandelbrot set and updates mpl plot
    #
    def draw(self):
        """ Redraws the figure
        """
        
        print self.size()
        # Grap values from textboxes
        re_min = float(unicode(self.textbox_re_min.text()))
        re_max = float(unicode(self.textbox_re_max.text()))
        im_min = float(unicode(self.textbox_im_min.text()))
        im_max = float(unicode(self.textbox_im_max.text()))
        max_iter = int(unicode(self.textbox_max_iter.text()))
        
        # Calculate mandelbrot set
        fractal = mandelbrot(re_min, re_max, im_min, im_max, max_betr, max_iter, res, cont) 
        
        # 
        if norm:
            fractal.data[fractal.data > 0] -= fractal.min
        
        # Show calculation time in statusbar
        self.status_text.setText("Calculation Time: %0.3fs" % fractal.calc_time)
    
        # Load data to mpl plot
        self.axes.imshow(fractal.data.T, origin="lower left", cmap='jet', extent=[re_min, re_max, im_min, im_max])
        self.axes.set_xlabel("Re(c)", labelpad=20)
        self.axes.set_ylabel("Im(c)")
        
        # Show/hide grid
        self.axes.grid(self.grid_cb.isChecked())
        if self.grid_cb.isChecked():
            self.axes.grid(linewidth=1, linestyle='-')
        # Align layout and redraw plot   
        self.canvas.draw_idle()
        #self.fig.tight_layout()

    def line_select_callback(self, eclick, erelease):
        # eclick and erelease are the press and release events
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Zoom with left mouse click
        if eclick.button == 1:
            # Check for valid coordinates            
            if (x1 != None and y2 != None and x1 != None and y1 != None):
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
        
        # Zoom with right mouse click        
        if eclick.button == 3:
            # Grap values from textboxes
            re_min = float(unicode(self.textbox_re_min.text()))
            re_max = float(unicode(self.textbox_re_max.text()))
            im_min = float(unicode(self.textbox_im_min.text()))
            im_max = float(unicode(self.textbox_im_max.text()))
                
            self.xy = [ re_max - re_min, im_max - im_min]

            # Calculate new values
            re_min = re_min - self.xy[0] / 2
            re_max = re_max + self.xy[0] / 2
            im_min = im_min - self.xy[1] / 2
            im_max = im_max + self.xy[1] / 2
            
            # Calculate precision in decimal digits
            for v in self.xy:
                if v <= 1:
                    self.decimals = round(log10(1 / v)) + 2
            
            # Round values with calculated precision
            re_min = round(re_min, int(self.decimals))
            re_max = round(re_max, int(self.decimals))
            im_min = round(im_min, int(self.decimals))
            im_max = round(im_max, int(self.decimals))
        
            # Update textbos values
            self.textbox_re_min.setText(str(re_min))
            self.textbox_re_max.setText(str(re_max))
            self.textbox_im_min.setText(str(im_min))
            self.textbox_im_max.setText(str(im_max))
            
            # Calculate and draw new mandelbrot set
            self.draw()
            
    def create_main_frame(self):
        self.main_frame = QWidget()
        self.main_frame.setMinimumHeight(460)
        
        
        # Create the Figure and FigCanvas objects
        self.fig = Figure((5,10), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Add sublot to figure do formatting
        self.axes = self.fig.add_subplot(111)
        self.axes.ticklabel_format(style='sci', scilimits=(0,0), axis='both')
        
        # Create zoom event handler
        self.RS = RectangleSelector(self.axes, self.line_select_callback,
                           drawtype='box', useblit=True,
                           button=[1, 3],  # don't use middle button
                           spancoords='data')                
        
        # Other GUI controls      
        self.textbox_re_min = QLineEdit()
        self.textbox_re_min_text = QLabel("ReMin: ")
        self.textbox_re_min.setMinimumWidth(55)
        
        self.textbox_re_max = QLineEdit()
        self.textbox_re_max_text = QLabel("ReMax: ")
        self.textbox_re_max.setMinimumWidth(55)
        
        self.textbox_im_min = QLineEdit()
        self.textbox_im_min_text = QLabel("ImMin: ")
        self.textbox_im_min.setMinimumWidth(55)
        
        self.textbox_im_max = QLineEdit()
        self.textbox_im_max_text = QLabel("ImMax: ")
        self.textbox_im_max.setMinimumWidth(55)
        
        self.textbox_max_iter = QLineEdit()
        self.textbox_max_iter_text = QLabel("Max Iterration: ")
        self.textbox_max_iter.setMinimumWidth(55)
        
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.draw)
        
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        grid = QGridLayout()
     
        hbox.addWidget(self.canvas, 3)
        hbox.addLayout(grid,1)

        
        grid.addWidget(self.textbox_re_min , 0,1)
        grid.addWidget(self.textbox_re_min_text , 0,0)
        grid.addWidget(self.textbox_re_max  , 1,1)
        grid.addWidget(self.textbox_re_max_text  , 1,0)
        grid.addWidget(self.textbox_im_min , 2,1)
        grid.addWidget(self.textbox_im_min_text , 2,0)
        grid.addWidget(self.textbox_im_max  , 3,1)
        grid.addWidget(self.textbox_im_max_text , 3,0)
        grid.addWidget(self.textbox_max_iter , 5,1)
        grid.addWidget(self.textbox_max_iter_text , 5,0)
        
        grid.addWidget(self.draw_button , 7,0)
        grid.addWidget(self.grid_cb , 6,0)
        
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)  
        
    def create_status_bar(self):
        self.status_text = QLabel("Ready")
        self.coord_text = QLabel("Re(c): % 7f, Im(c) % 7f" % (0, 0))
        
        self.canvas.mpl_connect("motion_notify_event", self.statusbar_coord)

        self.statusBar().addWidget(self.status_text, 1)
        self.statusBar().addWidget(self.coord_text, -1)
        
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
