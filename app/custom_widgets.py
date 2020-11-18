from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLineEdit, QPushButton


class Droppable_button(QPushButton):
    """A QPushButton that can have files dropped on it
    """
    files_dropped=Signal(str)
    
    def __init__(self, title=None, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        text=e.mimeData().text().replace('file:///','').strip().replace('\n',';')
        self.files_dropped.emit(text)
        # self.setText(e.mimeData().text())



class Droppable_lineEdit(QLineEdit):
    """A QPushButton that can have files dropped on it
    """
    files_dropped=Signal(str)
    
    def __init__(self, title=None, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        text=e.mimeData().text().replace('file:///','').strip().replace('\n',';')
        self.files_dropped.emit(text)
        # self.setText(e.mimeData().text())