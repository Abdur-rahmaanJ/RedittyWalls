

import sys
import math

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QLabel, QStatusBar, QToolBar
from PyQt5.QtWidgets import QPushButton, QProgressBar
from PyQt5.QtWidgets import QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon, QPixmap

import sip

import socket
import os, os.path
import random
from collections import deque
import requests
import ctypes
import platform
import subprocess

sub_reddits = [
                'wallpaper', 'wallpapers', 'wallpaperdump', 'wallpaperengine',
                'ImaginaryLandscapes', 'EarthPorn', 'food', 'foodphotography',
                'LandscapePhotography', 'Minecraft', 'blender', 'skyporn'
           ]
SCRIPT = """/usr/bin/osascript<<END
tell application "Finder"
set desktop picture to POSIX file "%s"
end tell
END"""

def check_ext(img_url):
    for ext in img_exts:
        if img_url.endswith(ext):
            return True
    return False


def download_file(file_url, path):
    r = requests.get(file_url, allow_redirects=True)
    open(path, 'wb').write(r.content)


def get_ext(url):
    return url.split('.')[-1]


def num_files():
    DIR = 'pics/'
    return len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

def update_num_files():
        num = num_files()+1
        return num


def pic_files():
    DIR = 'pics/'
    return [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]


def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


def set_bg(pic_path):
    if os.uname()[1] == 'raspberrypi':
        os.system('pcmanfm --set-wallpaper {}'.format(pic_path))
    elif platform.system() == 'Windows':
        ctypes.windll.user32.SystemParametersInfoW(20, 0, pic_path , 0)
    elif platform.system() == "Darwin":
        subprocess.Popen(SCRIPT%pic_path, shell=True)

    
    
    
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('WallPaperChanger')
        self._createMenu()
        self._createToolBar()
        self._createStatusBar()

        try:
            os.mkdir('pics')
        except FileExistsError:
            pass

        self.layout = QGridLayout()
        self.window = QWidget()

        self.btn = QPushButton('Change Via Online Pics')
        self.btn.clicked.connect(self.fetch_online_wallpaper)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.c_status = QLabel('')
        self.connect_label = QLabel()
        has_internet = is_connected()
        if has_internet:
            self.pixmap = QPixmap('ctrl_icons/checked.png')
        else:
            self.pixmap = QPixmap('ctrl_icons/cancel.png')
        self.smaller_pixmap = self.pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.connect_label.setPixmap(self.smaller_pixmap)
        self.stats = QLabel('Internet On: {}<br>Offline Images: {}'.format(is_connected(), num_files()))

        self.prev_but = QPushButton()
        self.prev_but.clicked.connect(self.prev_pic)
        prev_but_icon = QPixmap("ctrl_icons/previous.png");
        self.prev_but.setIcon(QIcon(prev_but_icon))
        
        self.next_but = QPushButton()
        self.next_but.clicked.connect(self.next_pic)
        next_but_icon = QPixmap("ctrl_icons/next-1.png");
        self.next_but.setIcon(QIcon(next_but_icon))
        
        self.rand_but = QPushButton()
        self.rand_but.clicked.connect(self.choose_randpic)
        rand_but_icon = QPixmap("ctrl_icons/refresh-1.png");
        self.rand_but.setIcon(QIcon(rand_but_icon))

        self.delete_img_but = QPushButton()
        self.delete_img_but.clicked.connect(self.confirm_img_deletion)
        delete_img_but_icon = QPixmap("ctrl_icons/cancel.png");
        self.delete_img_but.setIcon(QIcon(delete_img_but_icon))
        
        self.showofflinepic_label = QLabel()
        self.showofflinepic_label.setAlignment(Qt.AlignCenter)
        self.showofflinepic_label.setFixedSize(300, 300)
        self.choose_randpic()
        
        self.chooseoffline_but = QPushButton('Change via Offline Pic')
        self.chooseoffline_but.clicked.connect(self.change_offline_pic)

        self.layout.addWidget(self.connect_label, 0, 2)
        self.layout.addWidget(self.stats, 0, 1)
        self.layout.addWidget(self.btn, 1, 1, 1, 2)
        self.layout.addWidget(self.progress_bar, 2, 1, 1, 2)
        self.layout.addWidget(self.c_status, 3, 1, 1, 2)
        self.layout.addWidget(self.prev_but, 4, 0)
        self.layout.addWidget(self.showofflinepic_label, 4, 1, 1, 2)
        self.layout.addWidget(self.next_but, 4, 3)
        self.layout.addWidget(self.rand_but, 5, 1, 1, 2)
        self.layout.addWidget(self.delete_img_but, 6, 1, 1, 2)
        self.layout.addWidget(self.chooseoffline_but, 7, 1, 1, 2)

        self.window.setLayout(self.layout)
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setCentralWidget(self.window)

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _createToolBar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction('Exit', self.close)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("")
        self.setStatusBar(status)

    def fetch_online_wallpaper(self):
        self.c_status.setText('starting ...')
        self.progress_bar.setValue(0)
        self.wallpaper_change()
        self.progress_bar.setValue(100)
        self.c_status.setText('completed!')

    def display_pic(self, pic_name):
        self.showofflinepic_pixmap = QPixmap('pics/{}'.format(pic_name))
        self.smaller_showofflinepic_pixmap = self.showofflinepic_pixmap.scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.showofflinepic_label.setPixmap(self.smaller_showofflinepic_pixmap)


    def choose_randpic(self):
        self.offline_pics = deque(pic_files())
        if self.offline_pics:
            self.chosen_offlinepic = random.choice(self.offline_pics)
            self.display_pic(self.chosen_offlinepic)
        

    def prev_pic(self):
        self.offline_pics.rotate(1)
        self.chosen_offlinepic = self.offline_pics[0]
        self.display_pic(self.chosen_offlinepic)

    def next_pic(self):
        self.offline_pics.rotate(-1)
        self.chosen_offlinepic = self.offline_pics[0]
        self.display_pic(self.chosen_offlinepic)

    def change_offline_pic(self):
        self.wallpaper_change(offline_pic=self.chosen_offlinepic)

    def set_step_status(self, text):
        self.c_status.setText(text)
        QApplication.processEvents()

    def confirm_img_deletion(self):
        buttonReply = QMessageBox.question(self, 'Delete confirmation', "Do you really want to delete this picture?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            # remove image
            os.remove('pics/{}'.format(self.chosen_offlinepic))
            # update display
            self.choose_randpic()
        else:
            print('No clicked.')

    def wallpaper_change(self, offline_pic=None):
        try:
            if offline_pic:
                Fpath = os.path.realpath(os.getcwd())
                pic_path = os.path.join(os.sep, Fpath, 'pics', '{}'.format(offline_pic))
                ctypes.windll.user32.SystemParametersInfoW(20, 0, pic_path, 0)
            else:
                img_urls = []

                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'TE': 'Trailers'
                }
                random.shuffle(sub_reddits)

                self.set_step_status('gathering images ...')
                for i,sub_reddit in enumerate(sub_reddits):
                    perc = ((i+1)/len(sub_reddits)) * 50
                    self.set_progress(math.ceil(perc))
                    self.set_step_status('passing over source: {}'.format(i+1))
                    req = requests.get('https://www.reddit.com/r/{}/.json'.format(sub_reddit), headers=headers)
                    jsondata = req.json()
                    # print(jsondata)
                    posts = jsondata['data']['children']
                    current_urls = [post['data']['url'] for post in posts if (post['data']['url']).split('.')[-1] in
                    ['jpg', 'jpeg', 'png'] and 'imgur' not in post['data']['url']]
                    img_urls += current_urls
                print('found', img_urls)
                chosen_img = random.choice(img_urls)
                self.progress_bar.setValue(50)
                self.set_step_status('choosing image ...')
                print('choose', chosen_img)
                chosen_img_name = '{}.{}'.format(chosen_img[::-8], get_ext(chosen_img))
                chosen_img_path = 'pics/{}'.format(chosen_img_name)

                self.set_progress(75)
                self.set_step_status('fetching image ...')
                download_file(chosen_img, chosen_img_path)

                Fpath = os.path.realpath(os.getcwd())
                pic_path = os.path.join(os.sep, Fpath, 'pics', chosen_img_name)
                self.chosen_offlinepic = chosen_img_name
                self.offline_pics.append(chosen_img_name)
                self.display_pic(self.chosen_offlinepic)
                self.set_progress(90)
                self.set_step_status('setting image ...')
                set_bg(pic_path)
                self.layout.removeWidget(self.stats)
                sip.delete(self.stats)
                self.stats = None
                self.stats = QLabel('Internet On: {}<br>Offline Images: {}'.format(is_connected(), update_num_files()))
                self.layout.addWidget(self.stats, 0, 1)
        except Exception as e:
            print('error', e)

    def set_progress(self, value):
        self.progress_bar.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
