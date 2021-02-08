from PyQt5.QtWidgets import QApplication, QMainWindow,QProgressBar,QLineEdit
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5 import QtCore,uic
from threading import Thread, Lock
import requests
import re

class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("get.ui", self)
        self.setWindowTitle('获取/对比追番列表')
        appIcon = QIcon("icon.png")
        self.setWindowIcon(appIcon)
        pic=QPixmap('2233.png')
        self.label.setPixmap(pic)
        self.label.setScaledContents(True)  
        self.show()
        self.resizeEvent('初始化')
        self.listwidgets=[]
        for x in [self.listWidget,self.listWidget_2,self.listWidget_3,self.listWidget_4]:
            self.listwidgets.append(x)
        self.pushButton.clicked.connect(self.gettingAni)
        self.action.triggered.connect(self.get)
        self.action_2.triggered.connect(self.contrast)
        self.status='get'

    def get(self):
        if self.status=='get':
            pass
        else:
            self.status='get'
            for x in self.listwidgets:
                x.clear()
            self.lineEdit_2.deleteLater()
            del self.lineEdit_2
            self.pushButton.clicked.disconnect(self.contrasttingAni)
            self.pushButton.clicked.connect(self.gettingAni)

    def contrast(self):
        if self.status=='contrast':
            pass
        else:
            self.status='contrast'
            for x in self.listwidgets:
                x.clear()
            self.lineEdit_2=QLineEdit(self.widget_3,alignment=QtCore.Qt.AlignHCenter)
            self.lineEdit_2.show()
            self.resizeEvent('初始化')
            self.pushButton.clicked.disconnect(self.gettingAni)
            self.pushButton.clicked.connect(self.contrasttingAni)

    def gettingAni(self):
        uid = self.lineEdit.text()
        self.probar=QProgressBar(self.widget_2,alignment=QtCore.Qt.AlignHCenter)
        self.probar.setRange(0, 0)
        self.probar.show()
        self.resizeEvent('初始化')
        thread_Ani = Thread(target=self.Ani, args=(uid,))
        thread_Ani.start()

    def Ani(self, uid):
        Anis = getANIMES(uid)
        for i in range(4):
            for Ani in Anis[i]:
                self.listwidgets[i].addItem(Ani)
        self.probar.deleteLater()
        del self.probar

    def contrastAni(self,uid,uid_2):
        Anis=getANIMES(uid)
        Anis_2=getANIMES(uid_2)
        for i in range(4):
            Anisset=set(Anis[i])
            Anisset_2=set(Anis_2[i])
            Anisset_con=Anisset.intersection(Anisset_2)
            print(Anisset_con)
            for Ani in Anisset_con:
                self.listwidgets[i].addItem(Ani)
        self.probar.deleteLater()
        del self.probar


    def contrasttingAni(self):
        uid = self.lineEdit.text()
        uid_2 = self.lineEdit_2.text()
        self.probar=QProgressBar(self.widget_2,alignment=QtCore.Qt.AlignHCenter)
        self.probar.setRange(0, 0)
        self.probar.show()
        self.resizeEvent('初始化')
        thread_contrastAni = Thread(target=self.contrastAni, args=(uid,uid_2))
        thread_contrastAni.start()


    def resizeEvent(self,event):
        self.label.resize(self.widget.size())
        if hasattr(self,'probar'):
            self.probar.resize(self.widget_2.width(),self.probar.height())
        if hasattr(self,'lineEdit_2'):
            self.lineEdit_2.resize(self.widget_3.width(),self.lineEdit.height())


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
    temps_0,temps_1,temps_2,temps_3=Animes_0[:], Animes_1[:], Animes_2[:], Animes_3[:]
    TEMPS = [temps_0, temps_1,temps_2, temps_3]
    for x in ANIMES:
        x.clear()
    return TEMPS
    

if __name__ == '__main__':
    app = QApplication([])
    mywindow = MyWindow()
    app.exec_()