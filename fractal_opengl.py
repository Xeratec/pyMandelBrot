#!/usr/bin/python
'''
@file fractal_opengl.py
@author Philip Wiese
@date 12 Okt 2016
@brief Displays Mandelbrot Set with OpenGl
'''
import sys
# PyQt4 imports
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
# Numpy imports
import numpy as np

# Vertex shader
VS = """
#version 120
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
#version 120
varying float xpos;
varying float ypos;
varying float zpos;
void main (void)
{
    float iter = 0.0;
    float max_square = 3.0;
    float square = 0.0;
    float r = 0.0;
    float i = 0.0;
    float rt = 0.0;
    float it = 0.0;
    while(iter < 1.0 && square < max_square)
    {
        rt = (r*r) - (i*i) + xpos;
        it = (2.0 * r * i) + ypos;
        r = rt;
        i = it;
        square = (r*r)+(i*i);
        iter += 0.005;
    }
    gl_FragColor = vec4 (iter, iter, sin(iter*2.00), 1.0);
    //gl_FragColor = texture1D(tex, (i == iter ? 0.0 : float(i)) / 100.0);
}
"""

class Shader(object):
    shaderProgram = None
    VAO = None
    """Wrapper to create opengl 2.0 shader programms"""
    def __init__(self, vertex_source, fragment_source):

        self.vertexShader = self.compile_vertex_shader(vertex_source)
        self.fragmentShader = self.compile_fragment_shader(fragment_source)
        self.shaderProgram = self.link_shader_program(self.vertexShader, self.fragmentShader)
    
    def set_uniform_f(self, name, value):
        location = gl.glGetUniformLocation(self.shaderProgram, name)
        gl.glUniform1f(location, value)

    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        else:
            raise TypeError("Only floats are supported so far")
        
    def compile_vertex_shader(self, source):
        """Compile a vertex shader from source."""
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, source)
        gl.glCompileShader(vertex_shader)
        # check compilation error
        result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetShaderInfoLog(vertex_shader))
        return vertex_shader
    
    def compile_fragment_shader(self, source):
        """Compile a fragment shader from source."""
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, source)
        gl.glCompileShader(fragment_shader)
        # check compilation error
        result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetShaderInfoLog(fragment_shader))
        return fragment_shader
    
    def link_shader_program(self, vertex_shader, fragment_shader):
        """Create a shader program with from compiled shaders."""
        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)
        # check linking error
        result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        if not(result):
            raise RuntimeError(gl.glGetProgramInfoLog(program))
        return program

class GLWidget(QGLWidget):
    # default window size
    width, height = 600, 600
    def __init__(self, parent=None):
        QGLWidget.__init__(self)
        self.real = -2.0
        self.w = 2.5
        self.imag = -1.25
        self.h = 2.5
        self.setMouseTracking(True)
        self.parent = parent
        
    def initializeGL(self):
        self.show_fps = False
        
        """Initialize OpenGL, VBOs, upload data on the GPU, etc."""
        # background color
        gl.glClearColor(0.5,0.5,0.5,0.5)
        # compile the shaders
        self.shader = Shader(vertex_source=VS, fragment_source=FS)
        self.shaders_program = self.shader.shaderProgram

    def paintGL(self):
        """Paint the scene."""
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # bind the VBO
        
        gl.glLoadIdentity()
        gl.glUseProgram(self.shaders_program)
        
        self.shader["real"] = self.real
        self.shader["w"] = self.w
        self.shader["imag"] = self.imag
        self.shader["h"] = self.h
        
        gl.glBegin(gl.GL_QUADS)
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

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport."""
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        
    #
    # Calcualtes precision in digital digits
    #
    def setCoord(self, re_min, im_min, w, h):
        # Calculate precision in decimal digits
        decimals = 3
        for v in (w, h):
            if abs(v) <= 1:
                decimals = round(np.log10(1 / abs(v))) + 2
        
        # Round values with calculated precision
        self.real = round(re_min, int(decimals))
        self.imag = round(im_min, int(decimals))
        self.w = round(w, int(decimals))
        self.h = round(h, int(decimals))
        
        if self.parent is not None:
            # Update textbos values
            self.parent.textbox_re_min.setText(str(self.real))
            self.parent.textbox_re_max.setText(str(self.real + self.w))
            self.parent.textbox_im_min.setText(str(self.imag))
            self.parent.textbox_im_max.setText(str(self.imag + self.h))
    
    def zoom(self, factor):
        if factor >0:
            re_min = self.real+factor/4.0 * self.w
            im_min = self.imag+factor/4.0 * self.h
            w = self.w/(2.0*factor)
            h = self.h/(2.0*factor)
        if factor <0:
            re_min = self.real-abs(factor)/2.0 * self.w
            im_min = self.imag-abs(factor)/2.0 * self.h
            w = self.w*2.0*abs(factor)
            h = self.h*2.0*abs(factor)
        
        self.setCoord(re_min, im_min, w, h)
                
    def mousePressEvent(self, event):
        pos = event.pos()
        self.buffer = (pos.x(), pos.y())
        
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:
            return 0
        elif event.buttons() == Qt.LeftButton:
            pos = event.pos()
            d = [self.buffer[0]-pos.x(), self.buffer[1]-pos.y()]
            d[0] = self.w/self.width *d[0]
            d[1] = self.h/self.height * d[1]
            
            self.setCoord(self.real+d[0], self.imag-d[1], self.w, self.h)
            self.buffer = (pos.x(), pos.y())            
            self.repaint()
            
if __name__ == '__main__':
    data = np.zeros((10000, 2), dtype=np.float32)
    data[:,0] = np.linspace(-1., 1., len(data))
    
    print "[Debug] fractal_opengl"
    app = QApplication(sys.argv)
    form = QMainWindow()
    form.setWindowTitle('Mandelbrot Set')
    form.main_frame = GLWidget()
    form.main_frame.data = data
    form.setCentralWidget(form.main_frame)  
    form.show()
    app.exec_()