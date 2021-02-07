from PySide2.QtWidgets import QApplication, QPushButton, QLabel, QListWidget, QProgressBar
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPixmap, QIcon
from threading import Thread, Lock
from PIL import Image
import requests
import re


class MyWindow:
    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        self.listwidgets = []
        type_list = ['全部', '想看', '在看', '看完']
        for i in range(4):
            listwidget = QListWidget(self.ui)
            self.ui.tabWidget.addTab(listwidget, type_list[i])
            self.listwidgets.append(listwidget)
        self.ui.setWindowTitle("获取b站追番列表")
        appIcon = QIcon("icon.png")
        self.ui.setWindowIcon(appIcon)
        self.Side_view = QLabel(self.ui)
        pic = QPixmap('2233.png')
        self.Side_view.setPixmap(pic)
        im = Image.open('2233.png')
        pic_x, pic_y, ratio = im.size[0], im.size[1], 2.8
        self.Side_view.resize(pic_x/ratio, pic_y/ratio)
        self.Side_view.move(520, 44)
        self.Side_view.setScaledContents(True)
        self.ui.pushButton.clicked.connect(self.gettingAni)
        self.ui.lineEdit.returnPressed.connect(self.gettingAni)
        self.probar = QProgressBar(self.ui)
        self.probar.resize(-200, 20)

    def gettingAni(self):
        uid = self.ui.lineEdit.text()
        self.probar.move(556, 760)
        self.probar.resize(200, 20)
        self.probar.setRange(0, 0)
        thread_Ani = Thread(target=self.Ani, args=(uid,))
        thread_Ani.start()

    def Ani(self, uid):
        Anis = getANIMES(uid)
        for i in range(4):
            for Ani in Anis[i]:
                self.listwidgets[i].addItem(Ani)
        self.probar.resize(-200, 20)


Animes_0, Animes_1, Animes_2, Animes_3 = [], [], [], []
ANIMES = [Animes_0, Animes_1, Animes_2, Animes_3]

ANILock = Lock()


def getAnis(uid, progress_bar, follow_status):
    page = 1
    Animes = []
    while(True):
        url = 'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status={}&pn={}&ps=15&vmid={}&ts=1611454168274'.format(
            follow_status, page, uid)
        r = requests.get(url)
        string = r.text
        if len(string) < 100:  # 假如爬取到空页面，所获得的信息的长度大约在77左右，而且还会由于某些因素变动
            break
        pattern = r'"(?:番剧|国创)","title":"(.*?)".*?"season_type_name":'
        repl = r'\1|'
        string = re.sub(pattern, repl, string)
        pattern = r'"(?:番剧|国创)","title":"(.*?)".*'
        repl = r'\1'
        string = re.sub(pattern, repl, string)
        pattern = r'.*"season_type_name":'
        repl = r''
        string = re.sub(pattern, repl, string)
        Anime = string.split('|')
        ANILock.acquire()
        [ANIMES[follow_status].append(x) for x in Anime]
        ANILock.release()
        # if progress_bar:
        #     print('完成第{}页'.format(page))
        page += 1


def getANIMES(uid):
    threads = []
    for i in range(4):
        thread = Thread(target=getAnis, args=(uid, False, i))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return ANIMES


app = QApplication([])
mywindow = MyWindow()
mywindow.ui.show()
app.exec_()
