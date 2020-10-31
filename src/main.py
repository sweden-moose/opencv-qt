import cv2
import sys
import os
import subprocess
import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import *

start_path = os.getcwd()
cascPath = os.getcwd() + "/main.xml"
faceCascade = cv2.CascadeClassifier(cascPath)


class Lyceum(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.mode = False
        self.wid = 45
        self.heig = 35

    def initUI(self):
        self.setFixedSize(500, 500)
        self.setWindowIcon(QIcon('ico.ico'))
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Face crop: ultimate edition')
        self.btn = QPushButton('Указать папку', self)
        self.btn.resize(100, 40)
        self.btn.move(50, 450)
        self.btn.clicked.connect(self.get_path)
        self.btn1 = QPushButton('Начать', self)
        self.btn1.setEnabled(False)
        self.btn1.resize(100, 40)
        self.btn1.move(350, 450)
        self.btn1.clicked.connect(self.start)
        self.pixmap = QPixmap().scaled(100, 100)
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setPixmap(self.pixmap)
        self.image.resize(100, 100)
        self.image.move(200, 80)
        self.radio_button_1 = QRadioButton('Квадрат', self)
        self.radio_button_1.setChecked(True)
        self.radio_button_1.move(170, 455)
        self.radio_button_2 = QRadioButton('Паспорт', self)
        self.radio_button_2.move(170, 470)
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.radio_button_1)
        self.button_group.addButton(self.radio_button_2)
        self.button_group.buttonClicked.connect(self.change_mode)

    def get_path(self):
        self.path_in = QFileDialog.getExistingDirectoryUrl(self, 'Path to folder').toString().lstrip('file:///')
        if self.path_in != '':
            self.btn1.setEnabled(True)

    def change_mode(self):
        if self.radio_button_1.isChecked():
            self.mode = False
        else:
            self.mode = True

    def start(self):
        path_out = self.path_in + '/rtu/'
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        files = os.listdir(self.path_in)
        self.radio_button_1.setEnabled(False)
        self.radio_button_2.setEnabled(False)
        self.btn1.setEnabled(False)
        self.btn.setEnabled(False)
        deli = int(self.wid) / int(self.heig)
        log = []
        for i in files:
            try:
                os.chdir(self.path_in)
                img = cv2.imread(i)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            except:
                log.append(f'File {i}: format is not supporting')
                continue
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            try:
                x, y, w, h = faces[0]
            except:
                log.append(f'File {i}: No faces')
                continue
            x, y, w, h = faces[0]
            minus = 0
            plus = 0
            left = 0
            up = 0
            if self.mode:
                while w * deli >= h:
                    w += 1
                    h += 2
                    if x - left >= 1:
                        left += 1
                    else:
                        w += 1
                    if y - up >= 2:
                        up += 2
                    else:
                        h += 2
                crop_img = img[y - up:y + h, x - left:x + w]
                cv2.imwrite(path_out + i, crop_img)
                self.update_image_pass(path_out + i)
            else:
                crop_img = img[y - h // 6:y + h // 6 + h, x - w // 6:x + w // 6 + w]
                cv2.imwrite(path_out + i, crop_img)
                self.update_image_square(path_out + i)
        pathdir = path_out.replace('/', '\\')
        os.chdir(start_path)
        if log:
            if not os.path.isdir(os.getcwd() + '/logs/'):
                os.makedirs(os.getcwd() + '/logs/')
            os.chdir(os.getcwd() + '/logs/')
            time = str(datetime.datetime.now())
            time = time[:time.index('.')]
            f = open(f'log-{time.replace(" ", "_").replace(":", "-")}.txt', 'w')
            f.write('\n'.join(log))
            f.close()
        subprocess.Popen(r'explorer /select, "' + pathdir + '"')
        self.btn1.setEnabled(True)
        self.btn.setEnabled(True)
        self.radio_button_1.setEnabled(True)
        self.radio_button_2.setEnabled(True)
        log.clear()

    def update_image_square(self, path):
        pixmap = QPixmap(path).scaled(300, 300)
        self.image.setPixmap(pixmap)
        self.image.resize(300, 300)
        self.image.move(100, 80)
        self.repaint()

    def update_image_pass(self, path):
        pixmap = QPixmap(path).scaled(250, 360)
        self.image.setPixmap(pixmap)
        self.image.resize(250, 360)
        self.image.move(125, 50)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Lyceum()
    ex.show()
    sys.exit(app.exec())
