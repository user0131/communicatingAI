import sys
from PyQt5 import QtWidgets
import mainwindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(
        sys.argv
    )
    win = mainwindow.MainWindow()
    win.show()
    ret = app.exec()

    sys.exit(ret)
