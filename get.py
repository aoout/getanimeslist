from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit,QMessageBox,QTableWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from threading import Thread, Lock
from PyQt5 import QtCore, uic
import requests,json,time,sys


with open('Style.css', encoding='utf-8') as f:
    Style = f.read()


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("get.ui", self)
        self.setWindowTitle('获取/对比追番列表')
        self.setWindowIcon(QIcon("icon.png"))

        self.label.setPixmap(QPixmap('2233.png'))
        self.label.setScaledContents(True)
        self.tablewidgets  = [self.tableWidget, self.tableWidget_2,self.tableWidget_3, self.tableWidget_4]
        self.setStyleSheet(Style)
        self.show()
       
        self.button_get.clicked.connect(self.getAni)
        self.button_contrast.clicked.connect(self.contrastAni)
        self.lineedit_get.returnPressed.connect(self.getAni)
        self.lineedit_contrast_2.returnPressed.connect(self.contrastAni)
        
        self.get_thread = getAni_thread()
        self.get_thread.get_signal.connect(self.geted)
        self.get_thread.Invisible_get_signal.connect(self.ungeted)
        self.contrast_thread = contrastAni_thread()
        self.contrast_thread.contrast_signal.connect(self.contrasted)
        self.contrast_thread.Invisible_contrast_signal.connect(self.uncontrasted)

        self.speed='acceletate'
        self.action.triggered.connect(self.get)
        self.action_2.triggered.connect(self.contrast)
        self.action_5.triggered.connect(self.accelerate)
        self.action_8.triggered.connect(self.slowdown)
        self.action_9.triggered.connect(self.why)

    def get(self):

        if self.stack.currentIndex()!=0:
            self.cleartable()
            self.statusbar.clearMessage()
            self.stack.setCurrentIndex(0)
            
    def contrast(self):

        if self.stack.currentIndex()!=1:
            self.cleartable()
            self.statusbar.clearMessage()
            self.stack.setCurrentIndex(1)

    def accelerate(self):
        if self.speed!='acceletate':
            self.speed=='acceletate'
            self.statusbar.showMessage('已成功切换为加速模式', 5000)

    def slowdown(self):
        if self.speed!='slowdown':
            self.speed='slowdown'
            self.statusbar.showMessage('已成功切换为减速模式', 5000)

    def why(self):
        QMessageBox.information(self,'解释','如果使用减速模式，能够保证追番列表中“全部”这一栏的顺序与b站页面完全一致。反之则不能。')


    def getAni(self):
        self.starttime=time.time()
        self.cleartable()
        uid = self.lineedit_get.text()
        self.get_thread.getuid(uid)
        self.get_thread.getspeed(self.speed)
        self.get_thread.start()
        self.statusbar.showMessage('正在努力查询中...', 0)

    def geted(self, animes):
        
        for i in range(4):
            for Ani in animes[i][::-1]:

                self.tablewidgets[i].insertRow(0)
                item=QTableWidgetItem(Ani[0])
                self.tablewidgets[i].setItem(0,0,item)
                item=QTableWidgetItem(Ani[1])
                self.tablewidgets[i].setItem(0,1,item)

        animes_num = len(animes[0])
        self.endtime = time.time()
        dtime=self.endtime-self.starttime
        self.statusbar.showMessage(f'一共查询到{animes_num}条追番记录！本次查询一共花费了{dtime:.4}秒', 5000)

    def ungeted(self):
        QMessageBox.critical(self,'错误','该用户隐私设置未公开！')
        self.statusbar.clearMessage()

    def uncontrasted(self,num):
        QMessageBox.critical(self,'错误',f'第{num}用户隐私设置未公开！')
        self.statusbar.clearMessage()

    def contrastAni(self):
        self.starttime=time.time()
        self.cleartable()
        uid_1 = self.lineedit_contrast_1.text()
        uid_2 = self.lineedit_contrast_2.text()
        self.contrast_thread.getuid(uid_1, uid_2)
        self.contrast_thread.getspeed(self.speed)
        self.contrast_thread.start()
        self.statusbar.showMessage('正在努力查询对比中...', 0)

    def contrasted(self, animes_1, animes_2):
        for i in range(4):
            for Ani in set(animes_1[i]).intersection(set(animes_2[i]))[::-1]:

                self.tablewidgets[i].insertRow(0)
                item=QTableWidgetItem(Ani[0])
                self.tablewidgets[i].setItem(0,0,item)
                item=QTableWidgetItem(Ani[1])
                self.tablewidgets[i].setItem(0,1,item)
        animes_num_1 = len(animes_1[0])
        animes_num_2 = len(animes_2[0])
        animes_num_com = len(set(animes_1[0]).intersection(set(animes_2[0])))
        self.endtime = time.time()
        dtime=self.endtime-self.starttime
        self.statusbar.showMessage(
            f'分别查询到{animes_num_1}和{animes_num_2}条追番记录！其中有{animes_num_com}条相同！本次对比一共花费了{dtime:.4}秒', 5000)
        
    def paintEvent(self,event):
       self.label.resize(self.widget.size())
       width=self.tablewidgets[self.tabWidget.currentIndex()].width()
       for table in self.tablewidgets:
          table.setColumnWidth(0,int(width*0.65)-1); 
          table.setColumnWidth(1,int(width*0.35)); 

    def cleartable(self):

        for table in self.tablewidgets:
            for i in range(table.rowCount()-1,-1,-1):
                table.removeRow(i)


class getAni_thread(QThread):
    get_signal = pyqtSignal(list)
    Invisible_get_signal=pyqtSignal()

    def __init__(self):
        super().__init__()

    def getuid(self, uid):
        self.uid = uid
    def getspeed(self,speed):
        self.speed=speed

    def run(self):
        animes = getANIMES(self.uid,self.speed)
        if animes==False:
            self.Invisible_get_signal.emit()
        else:
            self.get_signal.emit(animes)


class contrastAni_thread(QThread):
    contrast_signal = pyqtSignal(list, list)
    Invisible_contrast_signal=pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def getuid(self, uid_1, uid_2):
        self.uid_1 = uid_1
        self.uid_2 = uid_2
    def getspeed(self,speed):
        self.speed=speed

    def run(self):
        animes_1 = getANIMES(self.uid_1,self.speed)
        
        if animes_1==False:
            self.Invisible_contrast_signal.emit(1)
        animes_2 = getANIMES(self.uid_2,self.speed)
        if animes_2==False:
            self.Invisible_contrast_signal.emit(2)
        else:
            self.contrast_signal.emit(animes_1, animes_2)


def getANIMES(uid,speed):
    ANIMES = [[] for _ in range(4)]
    ANILock = Lock()

    def visibilitycheck():
        url = f'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status=1&pn=1&ps=15&vmid={uid}&ts=1611454168274'
        r = requests.get(url)
        js = json.loads(r.text)
        if js['message'] == '用户隐私设置未公开':
            return False
        else:
            return True

    def threadfun(follow_status):
        nonlocal ANIMES
        page = 1
        while(('pages_max' not in vars()) or (page < pages_max)):
            url = f'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status={follow_status}&pn={page}&ps=15&vmid={uid}&ts=1611454168274'
            r = requests.get(url)
            js = json.loads(r.text)
            data = js['data']
            animes_num = data['total']
            pages_max = animes_num//15+1
            # Animes = [item['title'] for item in data['list']]
            Animes = [(item['title'],item['season_type_name']) for item in data['list']]
            ANILock.acquire()
            [ANIMES[follow_status].append(x) for x in Animes]
            ANILock.release()
            page += 1

    if not visibilitycheck():
        return False
    if speed=='acceletate':
        for i in range(1,4):
            thread = Thread(target=threadfun, args=(i,))
            thread.start()
            thread.join()
            ANIMES[0]=ANIMES[1]+ANIMES[2]+ANIMES[3]
    else:
        for i in range(4):
            thread = Thread(target=threadfun, args=(i,))
            thread.start()
            thread.join()
    return ANIMES


if __name__ == '__main__':
    app = QApplication([])
    mywindow = MyWindow()
    sys.exit(app.exec_())