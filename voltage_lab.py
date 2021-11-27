import os
import sys

import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtCore

import qtmodern.styles
import qtmodern.windows
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QMessageBox, QPushButton, QSlider, \
    QVBoxLayout, QWidget, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class App(QWidget):

    def __init__(self):
        super().__init__()
        # Window
        self.setWindowTitle("Voltage Lab")

        self.width, self.height = 900, 600
        self.setMinimumSize(self.width, self.height)

        # Plot
        plt.tight_layout()

        # Canvas and Toolbar
        self.canvas = FigureCanvas(plt.figure(constrained_layout=True))
        self.canvas.axes = self.canvas.figure.add_subplot(111, projection='3d')

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()

        # Buttons
        file_button = QPushButton("Load CSV")
        file_button.clicked.connect(self.loadFile)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.setEnabled(False)
        self.plot_button.clicked.connect(self.plotData)

        self.quiver_button = QPushButton("Plot Vectors")
        self.quiver_button.setEnabled(False)
        self.quiver_button.clicked.connect(self.plotQuiver)

        file_button.setMinimumSize(100, 50)
        self.plot_button.setMinimumSize(100, 50)
        self.quiver_button.setMinimumSize(100, 50)

        # Vector Size Slider
        self.vector_slider = QSlider()
        self.vector_slider.setEnabled(False)
        self.vector_slider.setOrientation(QtCore.Qt.Horizontal)
        self.vector_slider.setMinimum(1)
        self.vector_slider.setMaximum(5)
        self.vector_slider.setValue(1)
        self.vector_slider.setTickPosition(QSlider.TicksBelow)
        self.vector_slider.valueChanged.connect(self.changeValue)

        # Layout
        main_layout = QHBoxLayout()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        settings_layout = QVBoxLayout()
        settings_layout.addWidget(file_button)
        settings_layout.addWidget(self.plot_button)
        settings_layout.addWidget(self.quiver_button)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.vector_slider)

        slider_group = QGroupBox("Vector Size")
        slider_group.setMaximumSize(300, 100)
        slider_group.setLayout(slider_layout)

        settings_layout.addWidget(slider_group)

        main_layout.addLayout(settings_layout)
        main_layout.addLayout(plot_layout)

        self.setLayout(main_layout)

        self.show()

    def loadFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)")

        msg = QMessageBox()

        try:
            self.z = np.loadtxt(open(file_name, "rb"), delimiter=",", skiprows=1)

            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully loaded {}.".format(os.path.basename(file_name)))
            msg.setWindowTitle("Success!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.canvas.axes.clear()
            self.plot_button.setEnabled(True)
        except:
            self.plot_button.setEnabled(False)
            self.contour_button.setEnabled(False)
            self.vector_slider.setEnabled(False)

            msg.setIcon(QMessageBox.Critical)
            if file_name == "":
                msg.setText("No file selected! Try Again.")
            else:
                msg.setText("Could not load {}.".format(os.path.basename(file_name)))

            msg.setWindowTitle("Error!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def plotData(self):
        x = np.arange(0, self.z.shape[1])
        y = np.arange(0, self.z.shape[0])
        self.X, self.Y = np.meshgrid(x, y)

        self.canvas.axes.plot_surface(self.X, self.Y, self.z, cmap='viridis')

        self.canvas.axes.set_xlim(self.canvas.axes.get_xlim())
        self.canvas.axes.set_ylim(self.canvas.axes.get_ylim())

        self.quiver_button.setEnabled(True)

        self.canvas.draw()

    def plotQuiver(self):
        self.dx, self.dy = np.negative(np.gradient(self.z))

        self.quiver = self.canvas.axes.quiver3D(self.X, self.Y, np.zeros(self.X.shape), self.dx, self.dy,
                                                np.zeros(self.dx.shape))

        self.vector_slider.setEnabled(True)

        self.canvas.draw()

    def changeValue(self, value):
        self.quiver.remove()

        self.quiver = self.canvas.axes.quiver3D(self.X, self.Y, np.zeros(self.X.shape), self.dx, self.dy,
                                                np.zeros(self.dx.shape), length=value)

        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    main = App()

    sys.exit(app.exec_())
