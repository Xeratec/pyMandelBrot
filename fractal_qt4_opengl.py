#!/usr/bin/python
'''
@file fractal_opengl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with OpenGl
'''

import sys
from fractal_opengl import GLWidget
# PyQt4 Imports
from PyQt4.QtCore import *
from PyQt4.QtGui import *

###  Start Config ####
re_min = 0.385
im_min = 0.135
delta = 0.01

max_betr = 2
max_iter = 200      
######################
        
class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self.setWindowTitle('Mandelbrot Set')
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        # Initialize textbox values
        self.textbox_re_min.setText(str(re_min))
        self.textbox_im_min.setText(str(im_min))
        self.textbox_delta.setText(str(delta))
        self.textbox_max_iter.setText(str(max_iter))
        
        # Render mandelbrot set
        self.setMinimumWidth(620)
        self.resize(620, 460)   
        
        self.on_draw()     

    #
    # Display infos about application
    #
    def on_about(self):
        msg = """Mandelbrot Set Generator:
        
     ### Features ###
     * Zoom in our out by clicking +/- Button
     * Drag with the mouse to move the viewport
     
     ### Used Libraries ###
     * PyQt4
     * PyOpenGL
     * Numpy
     
     ### Author ###
     Made by Philip Wiese
     info@maketec.ch
     20. Oktober 2016
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    #
    # Calculates mandelbrot set and updates mpl plot
    #    
    def on_draw(self):
        # Grap values from textboxes
        re_min = float(unicode(self.textbox_re_min.text()))
        im_min = float(unicode(self.textbox_im_min.text()))
        delta = float(unicode(self.textbox_delta.text()))
        max_iter = int(unicode(self.textbox_max_iter.text()))
        
        # Pass values to GLWidget
        self.glWidget.setCoord(re_min, im_min, delta)
        self.glWidget.setIter(max_iter)
        self.glWidget.repaint()
        self.glWidget.setFocus()
        
        return 0 
    
    #
    # Key Press Event for zooming and drawing
    #
    def keyPressEvent(self, event):
        # Repaint with Enter and Return
        if event.key() == Qt.Key_Enter or event.key()==Qt.Key_Return: 
            self.on_draw()
        # Zoom out with minus
        elif event.key() == Qt.Key_Minus:
            self.glWidget.zoom(-1)
            self.glWidget.repaint()
        # Zoom out with plus
        elif event.key() == Qt.Key_Plus:
            self.glWidget.zoom(1)
            self.glWidget.repaint()
    
    #
    # Create main_frame; initialize Objects and create Layout
    #  
    def create_main_frame(self):
        self.main_frame = QWidget()
        self.main_frame.setMinimumHeight(280)
        
        # OpenGL Widget
        self.glWidget = GLWidget(self)         
        
        # Other GUI controls      
        self.textbox_re_min = QLineEdit()
        self.textbox_re_min_text = QLabel("ReMin: ")
        self.textbox_re_min.setMinimumWidth(55)
        
        self.textbox_im_min = QLineEdit()
        self.textbox_im_min_text = QLabel("ImMin: ")
        self.textbox_im_min.setMinimumWidth(55)
        
        self.textbox_delta = QLineEdit()
        self.textbox_delta_text = QLabel("Delta: ")
        self.textbox_delta.setMinimumWidth(55)
        
        self.textbox_max_iter = QLineEdit()
        self.textbox_max_iter_text = QLabel("Max Iterration: ")
        self.textbox_max_iter.setMinimumWidth(55)
        
        self.cont_cb = QCheckBox("Continuous Coloring")
        self.cont_cb.setChecked(True)
        
        self.norm_cb = QCheckBox("Normalize Values")
        self.norm_cb.setChecked(True)
        
        self.draw_button = QPushButton("Calculate && Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        # Layout with box sizers
        hbox = QHBoxLayout()
        grid = QGridLayout()
        hbox.addWidget(self.glWidget, 3)
        hbox.addLayout(grid,1)
        grid.setRowStretch(1,1)
 
        grid.addWidget(self.textbox_re_min , 0,1)
        grid.addWidget(self.textbox_re_min_text , 0,0)
        grid.addWidget(self.textbox_im_min , 1,1)
        grid.addWidget(self.textbox_im_min_text , 1,0)
        grid.addWidget(self.textbox_delta , 2,1)
        grid.addWidget(self.textbox_delta_text , 2,0)
        grid.addWidget(self.textbox_max_iter , 3,1)
        grid.addWidget(self.textbox_max_iter_text , 3,0)   
        grid.addWidget(self.cont_cb , 4,0,1,2)
        grid.addWidget(self.norm_cb , 5,0,1,2)
        grid.addWidget(self.draw_button , 6,0,1,2)
        grid.addWidget(QLabel(""), 7,0,2,2)
        
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)  
        
        # Set initial Foucus on glWidget
        self.glWidget.setFocus()
    
    #
    # Initialize statusbar
    # Todo: Time to calculate, Coordinates under mouse pointer
    #    
    def create_status_bar(self):
        self.status_text = QLabel("Ready")
        self.statusBar().addWidget(self.status_text, 1)
    
    #
    # Create main menu
    # Todo: Save Screenshot
    #   
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
    
    #
    # Add Action to menubar
    #
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    #
    # Create new action
    #
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

#
# Main Function
#    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
