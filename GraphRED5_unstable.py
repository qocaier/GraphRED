import sqlite3
import sys

from PIL import Image, ImageDraw, ImageFilter
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import Qt, QPoint, QEvent
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QWidget, QTabWidget, \
    QLineEdit, QLabel, QDoubleSpinBox, QFormLayout, QColorDialog, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, \
    QScrollArea, QTabBar
from PyQt5.uic.properties import QtCore, QtWidgets, QtGui


class EditableTabBar(QTabBar):
    def __init__(self, parent):
        QTabBar.__init__(self, parent)
        self._editor = QLineEdit(self)
        self._editor.setWindowFlags(Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        if ((event.type() == QEvent.MouseButtonPress and not self._editor.geometry().contains(event.globalPos())) or
                (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape)):
            self._editor.hide()
            return True
        return QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.ot = self.tabText(index)
        self._editor.setText(self.ot)
        if not self._editor.isVisible():
            self._editor.show()

    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self._editor.hide()
            nt = self._editor.text()
            self.setTabText(index, nt)

            con = sqlite3.connect('example.sqlite')
            cur = con.cursor()
            cur.execute(f"""UPDATE layers SET name = (?) WHERE idx = (?) AND de = 0""", (nt, index))
            con.commit()
            con.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('graphred3.ui', self)  # Загружаем дизайн
        # self.pushButton.clicked.connect(self.run)
        # Обратите внимание: имя элемента такое же как в QTDesigner
        # self.tab2 = self.scrollArea
        # self.scrollArea.setWidget(self.graphicsView)
        # flay = QFormLayout(self.graphicsView)
        # self.tab2.setWidgetResizable(True)
        self.ais = []

        self.indexes = []
        self.labels = []
        # self.curr = self.tabWidget.currentIndex()
        # all images sizes

        self.tabWidget.setTabBar(EditableTabBar(self))
        # self.chTheme()
        self.nL()
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.cltab)
        # self.tabWidget.tabMoved.connect(self.tm)
        self.add_layer.clicked.connect(self.nL)

        self.visual.clicked.connect(self.chCol)
        self.rubber.clicked.connect(self.tur)
        self.alphaImBtn.clicked.connect(self.TPI)
        self.anaBtn.clicked.connect(self.makeanagliph)
        self.ahromBtn.clicked.connect(self.ahrom)
        self.negBtn.clicked.connect(self.neg)
        # self.clear.clicked.connect(self.Nlay)
        self.curvBtn.clicked.connect(self.blur)

        self.RGB.textChanged.connect(self.chCol1)
        self.sclSlider.sliderMoved.connect(self.mast)
        self.doubleSpinBox.valueChanged.connect(self.brs)
        self.sclBx.valueChanged.connect(self.mast1)
        self.alphaBr.valueChanged.connect(self.TPB)

        self.action_5.triggered.connect(self.openImage)
        self.action_3.triggered.connect(self.close)
        self.imp.triggered.connect(self.opDb)
        self.create.triggered.connect(self.close)
        # self.actionOn.triggered.connect(self.drawingOn)
        # self.actionOff.triggered.connect(self.drawingOff)

        self.drawing = False
        self.colPrev.setStyleSheet("background-color: {}".format('#000000'))
        self.brushColor = QColor('#000000')
        self.lastPoint = QPoint()

        self.palette = QPalette()

        self.const_id = 0

        self.readSettings()

        # self.cosm = True
        self.pentur = True
        self.imop = False

        # print(self.tabWidget.currentIndex())
        self.tabWidget.tabBarClicked.connect(self.handle_tabbar_clicked)

    # def tm(self):
    #     con = sqlite3.connect('example.sqlite')
    #     cur = con.cursor()
    #     # cur.execute(f"""UPDATE layers SET idx = {self.tabWidget.currentIndex()} WHERE idx=(SELECT idx FROM layers WHERE
    #     #  const=(SELECT const FROM layers WHERE )) AND de = 0""")
    #     con.commit()
    #     con.close()

    def handle_tabbar_clicked(self, index):
        # print(index)
        # Задать, чтобы выбирался нужный label и рисовалось именно на нем, а сохранения записывать в бд только для
        # этого слоя
        pass

    def readSettings(self):
        f = open('settings.txt', 'r')
        f1 = f.readlines()
        f.close()

        self.doubleSpinBox.setValue(float(f1[0]))
        self.brs()

        self.alphaBr.setValue(int(f1[1]))
        self.TPB()

        self.RGB.setText(f1[2])
        self.chCol1()

        self.sclSlider.setValue(int(f1[3]))
        self.mast()

        self.bTheme()
        # self.bTheme()
        # if f1[4] == 'w':

    def opDb(self):
        self.imagePath = QFileDialog.getOpenFileName(self, 'Выбрать проект', '',
                                                     'Проект (*.sqlite);;Все файлы (*)')[0]

    def TPB(self):
        self.transpb = 255 - self.alphaBr.value()
        self.brushColor.setAlpha(self.transpb)

    def TPI(self):
        if self.alphaImChk.isChecked():
            print('checked')
        else:
            print('huh')

    def cltab(self, i):
        if self.tabWidget.count() > 1:
            con = sqlite3.connect('example.sqlite')
            cur = con.cursor()
            cur.execute(f"""UPDATE layers SET de = 1 WHERE idx = {i} AND de = 0""")
            con.commit()
            # con.close()

            # con = sqlite3.connect('example.sqlite')
            cur = con.cursor()
            cur.execute(f"""UPDATE layers SET idx = idx - 1 WHERE idx > {i} AND de = 0""")
            con.commit()
            con.close()

            # self.indexes.remove(int(self.tabWidget.tabText(i)[2:]))
            self.tabWidget.removeTab(i)

            self.scrollArea.removeWidget(self.labels[self.tabWidget.currentIndex])
        # print(self.indexes)

    def tur(self):
        self.pentur = not self.pentur
        if self.pentur:
            self.rubber.setText('Кисть')
        else:
            self.rubber.setText('Ластик')

    def nL(self):
        num = 1
        print(self.indexes)
        while num in self.indexes:
            num += 1
        self.tabWidget.addTab(QWidget(self.tabWidget), f"NL{num}")
        self.indexes.append(num)
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

        con = sqlite3.connect('example.sqlite')
        cur = con.cursor()
        cur.execute("""INSERT INTO layers(idx,name,const,de) VALUES(?, ?, ?, ?)""",
                    (self.tabWidget.currentIndex(), self.tabWidget.tabText(self.tabWidget.currentIndex()), num, 0))
        con.commit()
        con.close()

        self.scrollArea.setWidgetResizable(True)

        self.labels.append(QLabel(self.scrollArea))
        self.labels[self.tabWidget.currentIndex()].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # print(self.tabWidget.currentWidget())
        # print(self.labels)
        self.uniq()
        # self.const_id += 1

        self.img = Image.new('RGBA', (2000, 2000), (255, 0, 0, 0))
        # draw = ImageDraw.Draw(self.img)
        # draw.ellipse((25, 25, 75, 75), fill=(255, 0, 0))
        self.img.save('test.png', 'PNG')
        self.img = QPixmap('test.png')
        self.scrollArea.resize(self.img.width(), self.img.height())
        self.labels[self.tabWidget.currentIndex()].resize(self.img.width(), self.img.height())
        self.labels[self.tabWidget.currentIndex()].setPixmap(self.img)

        zw = self.scrollArea.width()
        zh = self.scrollArea.height()
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.resize(zw, zh)

    def wTheme(self):
        app.setPalette(self.palette)

    def bTheme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.black)
        self.tabWidget.setStyleSheet('QTabBar::tab {background-color: black;}')
        app.setPalette(palette)

    def chCol(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colPrev.setStyleSheet("background-color: {}".format(color.name()))
            self.brushColor = QColor(color.name())
            self.RGB.setText(color.name()[1:])
            self.brushColor.setAlpha(self.transpb)

    def chCol1(self):
        color = self.RGB.text()
        if len(color) == 6 and (i in '1234567890ABCDEF' for i in color):
            self.colPrev.setStyleSheet("background-color: {}".format('#' + color))
            self.brushColor = QColor('#' + color)
            self.brushColor.setAlpha(self.transpb)

    def brs(self):
        self.brushSize_st = self.doubleSpinBox.value()
        self.brushSize = self.doubleSpinBox.value() * self.sclSlider.value() / 100
        # self.cosm = True

    def mast(self):
        # self.cosm = False
        d = self.sclSlider.value()
        self.sclBx.setValue(d)

        self.scrollArea.setWidgetResizable(True)
        # self.image = QPixmap(self.imagePath).scaled(d * self.ais[0][0] // 100,
        #                                             d * self.ais[0][1] // 100,
        #                                             Qt.KeepAspectRatio)
        # self.label_7.resize(self.image.width(), self.image.height())
        # self.label_7.setPixmap(self.image)

        # self.img = QPixmap('test.png').scaled(d * self.ais[0][0] // 100,
        #                                       d * self.ais[0][1] // 100,
        #                                       Qt.KeepAspectRatio)
        self.img = QPixmap('test.png').scaled(d * self.width() // 100,
                                              d * self.height() // 100,
                                              Qt.KeepAspectRatio)
        self.label_8.resize(self.img.width(), self.img.height())
        self.label_8.setPixmap(self.img)

        self.brushSize = self.brushSize_st * d / 100

        zw = self.scrollArea.width()
        zh = self.scrollArea.height()
        # self.scrollArea.resize(self.image.width(), self.image.height())
        self.scrollArea.resize(self.img.width(), self.img.height())
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.resize(zw, zh)

    def mast1(self):
        # self.cosm = False
        d = self.sclBx.value()
        self.sclSlider.setValue(d)

        self.scrollArea.setWidgetResizable(True)
        self.image = QPixmap(self.imagePath).scaled(d * self.ais[0][0] // 100, d * self.ais[0][1] // 100,
                                                    Qt.KeepAspectRatio)
        self.label_7.resize(self.image.width(), self.image.height())
        self.label_7.setPixmap(self.image)

        self.img = QPixmap('test.png').scaled(d * self.ais[0][0] // 100, d * self.ais[0][1] // 100, Qt.KeepAspectRatio)
        self.label_8.resize(self.img.width(), self.img.height())
        self.label_8.setPixmap(self.img)

        self.brushSize = self.brushSize_st * d / 100
        zw = self.scrollArea.width()
        zh = self.scrollArea.height()
        self.scrollArea.resize(self.image.width(), self.image.height())
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.resize(zw, zh)

    def openImage(self):
        # pixmap = QPixmap("file_name.png")
        # painter.drawPixmap(self.rect(), pixmap)
        # painter.setPen((QPen(QColor("green"))))

        # painter = QPainter(self)

        self.scrollArea.setWidgetResizable(True)
        self.imagePath = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                                     'Картинка (*.jpg);;Картинка (*.png);;Картинка (*.gif);;Картинка '
                                                     '(*.bmp);;Картинка (*.tiff);;Картинка (*.jp2);;Все файлы (*)')[0]
        # self.graphicsView.mapFromScene(imagePath)
        self.image = QPixmap(self.imagePath)
        self.szImX.setValue(self.image.width())
        self.szImY.setValue(self.image.height())
        # self.lopa()

        # img_pixmap = self.image.scaled(50, 50, Qt.KeepAspectRatio)
        # self.ais.append((self.image.width(), self.image.height()))
        # self.label_7.resize(self.image.width(), self.image.height())
        # self.label_7.setPixmap(self.image)

        for i in self.labels:
            i.resize(self.image.width(), self.image.height())
        self.labels[self.tabWidget.currentIndex()].setPixmap(self.image)

        # painter.drawPixmap(self.rect(), self.label_7)
        # painter.setPen((QPen(QColor("green"))))
        # painter.drawEllipse(100, 100, 30, 30)

        # self.resize(10000, 200)
        zw = self.scrollArea.width()
        zh = self.scrollArea.height()
        self.scrollArea.resize(self.image.width(), self.image.height())
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.resize(zw, zh)
        # print(self.label_7.size())
        # self.label_7.adjustSize()
        # self.label_7.resize(image.size())
        # УРА, Я СМОГ !!!
        self.imop = True
        # self.action_5.setEnabled(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            painter = QPainter(self.img)
            self.pen = QPen(self.brushColor, self.brushSize,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            # self.pen.setCosmetic(self.cosm)
            # Это не работает, и пиксели все равно неправильного размера. Надо будет найти решение проблемы
            painter.setPen(self.pen)
            painter.drawLine(self.labels[self.tabWidget.currentIndex()].mapFrom(self, self.lastPoint),
                             self.labels[self.tabWidget.currentIndex()].mapFrom(self, event.pos()))
            # print(self.label_8.mapFrom(self, self.lastPoint), self.label_8.mapFrom(self, event.pos()))
            self.lastPoint = event.pos()
            self.labels[self.tabWidget.currentIndex()].setPixmap(self.img)
        if self.imop:
            if 0 < event.x() < self.labels[self.tabWidget.currentIndex()].width() and 0 < event.y() < \
                    self.labels[self.tabWidget.currentIndex()].height():
                self.label_14.setText(f"Координаты: {event.x()}, {event.y()}")
            else:
                self.label_14.setText(f"Координаты: out")
        else:
            self.label_14.setText(f"Координаты: out")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.img.save('test.png', 'PNG')

    def makeanagliph(self):
        if self.alphaImChk.isChecked():
            print('checked')
        else:
            print('huh')

        im = Image.open('test.png')
        im = im.convert('RGBA')
        pixels = im.load()
        x, y = im.size
        d = self.anaBx.value()
        for i in range((x - 1), (d - 1), -1):
            for j in range(y):
                r, g, b, a = pixels[i, j]
                r1, g1, b1, a1 = pixels[(i - d), j]
                if r1 != 0:
                    pixels[i, j] = r1, g, b, a1
        for i in range(d):
            for j in range(y):
                r, g, b, a = pixels[i, j]
                if r != 0 and b != 0:
                    pixels[i, j] = 0, g, b, a
        im.save('test.png', 'PNG')

    def blur(self):
        if self.alphaImChk.isChecked():
            print('checked')
        else:
            print('huh')

        im = Image.open('test.png')
        im = im.convert('RGBA')
        im = im.filter(ImageFilter.GaussianBlur(radius=self.curvBx.value()))
        im.save('test.png', 'PNG')

    def ahrom(self):
        if self.alphaImChk.isChecked():
            print('checked')
        else:
            print('huh')

        im = Image.open('test.png')
        im = im.convert('RGBA')
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b, a = pixels[i, j]
                bw = (r + g + b) // 3
                pixels[i, j] = bw, bw, bw, a
        im.save('test.png', 'PNG')

    def neg(self):
        if self.alphaImChk.isChecked():
            print('checked')
        else:
            # for
            print('huh')

        im = Image.open('test.png')
        im = im.convert('RGBA')
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b, a = pixels[i, j]
                pixels[i, j] = 255 - r, 255 - g, 255 - b, a
        im.save('test.png', 'PNG')

    def outdate(self):
        # Удалять папки со старыми слоями или изображениями
        pass

    def uniq(self):
        con = sqlite3.connect('example.sqlite')
        cur = con.cursor()
        was = self.indexes
        now = cur.execute("""SELECT const FROM layers""").fetchall()
        self.indexes = []
        for i in now:
            self.indexes.append(i[0])
        b = cur.execute("""SELECT const FROM history""").fetchall()
        con.close()
        todel = []
        for i in b:
            if i not in self.indexes:
                self.indexes.append(i)
        for i in was:
            if i not in self.indexes:
                todel.append(i)
        # print(todel)
        # print(self.indexes)

    # def paintEvent(self, event):
    #     canvasPainter = QPainter(self)
    #     canvasPainter.drawPixmap(self.rect(), self.img, self.img.rect())

    # С закомментированным не работает

    # Это добавлено


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
