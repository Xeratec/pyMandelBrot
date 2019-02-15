#!/usr/bin/python3
'''
@file fractal_qt4_opengl_lib.py
@author Philip Wiese
@date 12 Okt 2016
@brief PyQt4 QGLWidget to displays Mandelbrot Set with OpenGl
'''

import sys, time
# PyQt4 imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
# Numpy imports
import numpy as np
# PIL imports
from PIL.Image import open

# Vertex shader
VS = """
#version 130
uniform float real;
uniform float w;
uniform float imag;
uniform float h;

varying float xpos;
varying float ypos;

void main(void)
{
  xpos = clamp(gl_Vertex.x, 0.0,1.0)*w+real;
  ypos = clamp(gl_Vertex.y, 0.0,1.0)*h+imag;

  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

# Fragment shader
FS = """
#version 130
uniform sampler1D tex;
varying float xpos;
varying float ypos;
varying float zpos;
uniform float step;

void main (void)
{
    float max_square = 3.0;
    float square = 0.0;
    float r = 0.0;
    float i = 0.0;
    float rt = 0.0;
    float it = 0.0;
    float iter = 0.0;
    while(iter < 1.0 && square < max_square)
    {
        rt = (r*r) - (i*i) + xpos;
        it = (2.0 * r * i) + ypos;
        r = rt;
        i = it;
        square = (r*r)+(i*i);
        iter += step;
    }
    //gl_FragColor = vec4 (iter, iter, sin(iter*2.00), 1.0);
    gl_FragColor = texture1D(tex, iter);
}
"""

class Shader(object):
    shaderProgram = None
    #
    # Wrapper to create OpenGL shader programms
    #
    def __init__(self, vertex_source, fragment_source):

        self.vertexShader = self.compile_vertex_shader(vertex_source)
        self.fragmentShader = self.compile_fragment_shader(fragment_source)
        self.shaderProgram = self.link_shader_program(self.vertexShader, self.fragmentShader)

    def set_uniform_f(self, name, value):
        location = gl.glGetUniformLocation(self.shaderProgram, name)
        gl.glUniform1f(location, value)

    #
    # Pass a variable to the shader
    #
    def __setitem__(self, name, value):
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        else:
            raise TypeError("Only floats are supported so far")

    #
    # Compile a vertex shader from source
    #
    def compile_vertex_shader(self, source):
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, source)
        gl.glCompileShader(vertex_shader)
        # Check compilation error
        result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader))
        return vertex_shader

    #
    # Compile a fragment shader from source
    #
    def compile_fragment_shader(self, source):

        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, source)
        gl.glCompileShader(fragment_shader)
        # Check compilation error
        result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader))
        return fragment_shader

    #
    # Create a shader program from compiled shaders
    #
    def link_shader_program(self, vertex_shader, fragment_shader):
        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)
        # Check linking error
        result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetProgramInfoLog(program))
        return program

#
# PyQt4 Widget to display Mandelbrot set with OpenGL
#
class GLWidget(QGLWidget):
    #
    # Initialize GLWidget, init variables and set parent
    #
    def __init__(self, parent=None):
        self.height, self.width = 600, 600
        QGLWidget.__init__(self)
        self.real = -2.0
        self.w = 2.5
        self.imag = -1.25
        self.h = 2.5
        self.step = 0.005
        self.TtC_sum = 0
        self.TtC_count = 0
        self.TtC = 0
        # Activate Mousetracking for mouseMoveEvent
        self.setMouseTracking(True)
        self.parent = parent

    #
    # Initialize OpenGL
    #
    def initializeGL(self):
        # Set background color
        gl.glClearColor(0.5,0.5,0.5,0.5)
        # Compile the shader
        self.shader = Shader(vertex_source=VS, fragment_source=FS)
        self.shaders_program = self.shader.shaderProgram
        # Setup texture
        self.imageID = self.loadTex("texture.png")
        gl.glEnable(gl.GL_TEXTURE_1D)
        gl.glBindTexture(gl.GL_TEXTURE_1D, self.imageID)

    #
    # Paint the scene
    #
    def paintGL(self):
        # Setup timer
        self.timer = time.time()
        # Clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glLoadIdentity()
        gl.glUseProgram(self.shaders_program)
        # Set variables in Shader
        self.shader["real"] = self.real
        self.shader["w"] = self.w
        self.shader["imag"] = self.imag
        self.shader["h"] = self.h
        self.shader["step"] = self.step

        gl.glBegin(gl.GL_QUADS)
        # Draw a rect with vertexes and set texture coordinates
        gl.glTexCoord2f(0, 0)
        gl.glVertex2f(-1, -1)
        gl.glTexCoord2f(1, 0)
        gl.glVertex2f(1, -1)
        gl.glTexCoord2f(1, 1)
        gl.glVertex2f(1, 1)
        gl.glTexCoord2f(0, 1)
        gl.glVertex2f(-1, 1)
        gl.glEnd()
        gl.glUseProgram(0)

        self.timer = time.time() - self.timer
        self.getTtC(self.timer*1000, 5)
        if self.parent is not None:
            if self.TtC == 0:
                self.TtC = self.timer*1000
            text = "Time to calculate: %00.2f ms" % self.TtC
            self.parent.status_text.setText(text)

    #
    # Calculate TtC (Time to Calculate over a number of frames
    #
    def getTtC(self, elapsed, frames):
        self.TtC_sum += elapsed
        self.TtC_count += 1
        if self.TtC_count > frames:
            self.TtC = self.TtC_sum / self.TtC_count
            self.TtC_sum = 0
            self.TtC_count = 0

        return self.TtC

    #
    # Called upon window resizing: reinitialize the viewport.
    #
    def resizeGL(self, width, height):
        # Update the window size
        self.width, self.height = width, height
        # Paint within the whole window
        gl.glViewport(0, 0, width, height)
        # Recalculate Mandelbrot dimensions
        self.setCoord(self.real, self.imag, self.w)

    #
    # Load texture for OpenGL from file
    #
    def loadTex(self, image):
        im = open(image)
        ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGB")
        imdata = np.fromstring(image, np.uint8)
        # Create new texture ID for OpenGL
        ID = gl.glGenTextures(1)
        # Make 1D Texture
        gl.glBindTexture(gl.GL_TEXTURE_1D, ID)
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST);
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST);
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT);
        gl.glTexImage1D(
            gl.GL_TEXTURE_1D, 0, gl.GL_RGB8, 256, 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, imdata
        )
        return ID

    #
    # Calcualtes precision in digital digits
    #
    def setCoord(self, re_min, im_min,delta):
        # Calculate precision in decimal digits
        decimals = 3
        if abs(delta) <= 1:
            decimals = round(np.log10(1 / abs(delta))) + 2

        # Round values with calculated precision
        self.real = round(re_min, int(decimals))
        self.imag = round(im_min, int(decimals))
        self.w = round(delta, int(decimals+1))
        self.h = round(self.height*delta/self.width, int(decimals))

        if self.parent is not None:
            # Update textbos values
            self.parent.textbox_re_min.setText(str(self.real))
            self.parent.textbox_im_min.setText(str(self.imag))
            self.parent.textbox_delta.setText(str(self.w))

    def setIter(self, max_iter):
        self.step = 1.0/max_iter

    #
    # Zoom in or out by a given factor
    #
    def zoom(self, factor):
        # Zoom in
        if factor >0:
            re_min = self.real+factor/4.0 * self.w
            im_min = self.imag+factor/4.0 * self.h
            w = self.w/(2.0*factor)
        # Zoom out
        if factor <0:
            re_min = self.real-abs(factor)/2.0 * self.w
            im_min = self.imag-abs(factor)/2.0 * self.h
            w = self.w*2.0*abs(factor)
        self.setCoord(re_min, im_min, w)

    #
    # Move by factor of w or h
    #
    def move(self, direction, factor):
        re_min = self.real
        im_min = self.imag
        # Move Re(c)
        if direction==0:
            re_min = self.real+factor*self.w
        # Move Im(c)
        if direction==1:
            im_min = self.imag+factor*self.h
        self.setCoord(re_min, im_min, self.w)

    #
    # Mouse press event
    #
    def mousePressEvent(self, event):
        # Save mouse position to calculate relative movement
        pos = event.pos()
        self.buffer = (pos.x(), pos.y())

    #
    # Move viewport with left drag
    #
    def mouseMoveEvent(self, event):
        pos = event.pos()
        relPos = [self.w/self.width * pos.x()+self.real, -1*self.w/self.width * pos.y()-self.imag]
        # Update relative coordinates in Stautsbar
        if self.parent is not None:
            text = "Re(c): % .5f, Im(c) % .5f" % (relPos[0], relPos[1])
            self.parent.coord_text.setText(text)

        # Mouse drag
        if event.buttons() == Qt.RightButton:
            return 0
        elif event.buttons() == Qt.LeftButton:

            # Calculate relative movement
            d = [self.buffer[0]-pos.x(), self.buffer[1]-pos.y()]
            d[0] = self.w/self.width *d[0]
            d[1] = self.h/self.height * d[1]

            self.setCoord(self.real+d[0], self.imag-d[1], self.w)
            self.buffer = (pos.x(), pos.y())
            self.repaint()

    #
    # Key Press Event for zoom and move
    #
    def keyPressEvent(self, event):
        # Zoom out with minus
        if event.key() == Qt.Key_Minus:
            self.zoom(-1)
        # Zoom out with plus
        elif event.key() == Qt.Key_Plus:
            self.zoom(1)
        # Move viewport
        if event.key() == Qt.Key_Up:
            self.move(1,0.25)
        elif event.key() == Qt.Key_Down:
            self.move(1,-0.25)
        elif event.key() == Qt.Key_Left:
            self.move(0,-0.25)
        elif event.key() == Qt.Key_Right:
            self.move(0,0.25)

        self.repaint()

#
# Main function for debugging
#
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = QMainWindow()
    form.setWindowTitle('Mandelbrot Set')
    form.resize(500,500)
    form.main_frame = GLWidget()
    form.setCentralWidget(form.main_frame)
    form.show()
    app.exec_()
