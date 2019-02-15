#!/usr/bin/python3
'''
@file fractal_qt5_opengl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with OpenGl
@dependencies python-pillow, python-opengl, qt5, python-pyqt5
'''

import sys
from fractal_qt5_opengl_lib import GLWidget
# PyQt4 Imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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
    # Save Screenshot
    #
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path = unicode(QFileDialog.getSaveFileName(self,
                        'Save file', '',
                        file_choices))
        if path:
            return 0

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
        re_min = float(self.textbox_re_min.text())
        im_min = float(self.textbox_im_min.text())
        delta = float(self.textbox_delta.text())
        max_iter = int(self.textbox_max_iter.text())

        # Pass values to GLWidget
        self.glWidget.setCoord(re_min, im_min, delta)
        self.glWidget.setIter(max_iter)
        self.glWidget.repaint()
        self.glWidget.setFocus()

        return 0

    #
    # Key Press Event for redraw
    #
    def keyPressEvent(self, event):
        # Repaint with Enter and Return
        if event.key() == Qt.Key_Enter or event.key()==Qt.Key_Return:
            self.on_draw()

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
        self.textbox_max_iter_text = QLabel("Max Iter.: ")
        self.textbox_max_iter.setMinimumWidth(55)

        self.draw_button = QPushButton("Calculate && Draw")
        self.draw_button.clicked.connect(self.on_draw)

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
        grid.addWidget(self.draw_button , 5,0,1,2)
        grid.addWidget(QLabel(""), 6,0,2,2)

        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)

        # Set initial Foucus on glWidget
        self.glWidget.setFocus()

    #
    # Initialize statusbar
    #
    def create_status_bar(self):
        self.status_text = QLabel("Ready")
        self.coord_text = QLabel("Re(c): % 7f, Im(c) % 7f" % (0, 0))

        self.statusBar().addWidget(self.status_text, 1)
        self.statusBar().addWidget(self.coord_text, -1)

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

        save_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot,
            tip="Save the plot")

        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")
        self.add_actions(self.file_menu,
            (save_file_action, None, quit_action))

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
            action.triggered.connect(slot)
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
