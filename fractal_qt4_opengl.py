#!/usr/bin/python
'''
@file fractal_opengl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with OpenGl
'''
import sys

from fractal_opengl import GLWidget

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import log10


######  Config #######
re_min = 0.385
re_max = 0.395
im_min = 0.135
im_max = 0.145

max_betr = 2
max_iter = 100      
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
    def on_draw(self):
         # Grap values from textboxes
        re_min = float(unicode(self.textbox_re_min.text()))
        re_max = float(unicode(self.textbox_re_max.text()))
        im_min = float(unicode(self.textbox_im_min.text()))
        im_max = float(unicode(self.textbox_im_max.text()))
        max_iter = int(unicode(self.textbox_max_iter.text()))
         
        self.glWidget.real = re_min
        self.glWidget.w = re_max-re_min
        self.glWidget.imag = im_min
        self.glWidget.h = im_max-im_min
        self.glWidget.repaint()
        return 0   
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        self.main_frame.setMinimumHeight(280)
        
        self.glWidget = GLWidget()
        self.glWidget.real = re_min
        self.glWidget.w = re_max-re_min
        self.glWidget.imag = im_min
        self.glWidget.h = im_max-im_min          
        
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
        
        self.grid_cb = QCheckBox("Show Grid")
        self.grid_cb.setChecked(False)
        
        self.cont_cb = QCheckBox("Continuous Coloring")
        self.cont_cb.setChecked(True)
        
        self.norm_cb = QCheckBox("Normalize Values")
        self.norm_cb.setChecked(True)
        
        self.draw_button = QPushButton("Calculate && Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        grid = QGridLayout()
        hbox.addWidget(self.glWidget, 3)
        hbox.addLayout(grid,1)
        grid.setRowStretch(1,1)
 
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
        grid.addWidget(self.grid_cb , 6,0,1,2)
        grid.addWidget(self.cont_cb , 7,0,1,2)
        grid.addWidget(self.norm_cb , 8,0,1,2)
        
        grid.addWidget(self.draw_button , 9,0,1,2)
        grid.addWidget(QLabel(""), 10,0,2,2)
        
        
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)  
        
    def create_status_bar(self):
        self.status_text = QLabel("Ready")
        self.coord_text = QLabel("Re(c): % 7f, Im(c) % 7f" % (0, 0))
        
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
        
        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, (None, quit_action))
        
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
