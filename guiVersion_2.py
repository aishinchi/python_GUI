# ！/usr/bin/python35
# -*- coding:utf-8 -*-

import sys,os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction,qApp, QTextEdit, QLabel, QWidget,QPushButton,\
    QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QFileDialog, QComboBox, QDesktopWidget, QProgressBar
from PyQt5.QtGui import QIcon, QFont
from runGCCNMF import *
from gccNMFFunctions import *
from PyQt5.QtCore import pyqtSignal,QUrl, QBasicTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from numpy import column_stack, loadtxt, mean, array
# from scipy.io import wavfile
from gccNMF.wavfile import wavread, wavwrite

class OriginalWindows(QMainWindow):

    processStatus = 0
    stopGCCNMF = pyqtSignal()   #GCCNMF运行完毕的信号

    def __init__(self):
        super().__init__()

        #系统窗口总体设计
        self.setGeometry(100,100,1600,900)
        self.setWindowTitle("基于麦克风阵列的语音分离系统")
        self.setWindowIcon(QIcon('F:\Python\gcc-nmf-master\gccNMF\img\microphone.png'))
        self.center()

        #状态栏
        self.statusBar()
        # self.newPreprocess = PreProcess()
        # 菜单栏设计:3种算法
        gccNMF = QAction(QIcon(r'F:\Python\gcc-nmf-master\gccNMF\img\nmf.png'), "GCC-NMF", self)
        gccNMF.setStatusTip("选择GCC-NMF算法")
        gccNMF.triggered.connect(self.showMainWindow)
        beamForming = QAction(QIcon(r'F:\Python\gcc-nmf-master\gccNMF\img\beamforming.png'),"波束形成",self)
        beamForming.setStatusTip("选择波束形成算法")
        deepLearning = QAction(QIcon(r'F:\Python\gcc-nmf-master\gccNMF\img\machine.png'), '深度学习', self)
        deepLearning.setStatusTip("选择深度学习算法")

        menuBar = self.menuBar()
        algorithmBar = menuBar.addMenu("算法选择")
        algorithmBar.addAction(gccNMF)
        algorithmBar.addAction(beamForming)
        algorithmBar.addAction(deepLearning)

        self.mainGround = QWidget()
        self.setCentralWidget(self.mainGround)

        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        # 部件声明
        #打开原始txt文件
        self.buttonWriteSD = QPushButton("磁盘数据写入")
        self.buttonWriteSD.setFont(QFont("宋体", 11))
        self.buttonOpenFile = QPushButton("打开原始数据文件")
        self.buttonOpenFile.setFont(QFont("宋体", 11))
        self.buttonOpenFile.setStatusTip("打开原始数据文件")
        self.fileName = QLineEdit()
        self.fileName.setFont(QFont("Roman times",10))
        self.fileName.setFixedSize(250,25)

        # 初始参数设计
        self.chooseChannel = QLabel("  选择双通道： ")
        self.chooseChannel.setFont(QFont("宋体", 11))
        self.combos = QComboBox()
        self.combos.setFont(QFont("Roman times",10))
        self.combos.addItem("1 2")
        self.combos.addItem("1 3")
        self.combos.addItem("1 4")
        self.combos.addItem("1 5")
        self.combos.addItem("1 6")
        self.combos.addItem("2 3")
        self.combos.addItem("2 4")
        self.combos.addItem("2 5")
        self.combos.addItem("2 6")
        self.combos.addItem("3 4")
        self.combos.addItem("3 5")
        self.combos.addItem("3 6")
        self.combos.addItem("4 5")
        self.combos.addItem("4 6")
        self.combos.addItem("5 6")
        self.combos.activated[str].connect(self.getChooseNum)

        #选择采样率
        self.sample = QLabel("选择采样率(Hz):")
        self.sample.setFont(QFont("宋体", 11))
        self.sampleRate = QComboBox()
        self.sampleRate.setFont(QFont("Roman times",10))
        self.sampleRate.addItem("16000")
        self.sampleRate.addItem("24000")
        self.sampleRate.addItem("48000")
        self.sampleRate.addItem("96000")
        self.sampleRate.activated[str].connect(self.getSampleRate)

        #获取麦克风距离和源信号个数
        self.microphone = QLabel("       麦克风距离(m):")
        self.microphone.setFont(QFont("宋体", 11))
        self.microphoneSeparationInMetres1 = QLabel("     ")
        self.microphoneSeparationInMetres1.setFont(QFont("Roman times",10,QFont.Bold))
        self.num = QLabel(" 源个数：  ")
        self.num.setFont(QFont("宋体", 11))
        self.numSources1 = QComboBox()
        self.numSources1.setFont(QFont("Roman times",10))
        self.numSources1.addItem('1')
        self.numSources1.addItem('2')
        self.numSources1.addItem('3')
        self.numSources1.addItem('4')
        self.numSources1.addItem('5')
        self.numSources1.addItem('6')
        self.numSources1.activated[str].connect(self.getNumSources)

        #开始处理语音
        self.buttonStart = QPushButton("开始处理语音")
        self.buttonStart.setFont(QFont("宋体", 11))
        self.buttonStart.setStatusTip("开始处理语音")
        self.processShow = QProgressBar()
        self.processShow.setFixedSize(300,25)
        self.showTip = QLabel("             ")
        self.count = 0
        self.sim1 = QPushButton("未知源信号")
        self.sim1.setFont(QFont("宋体", 11))
        self.sim2 = QPushButton("未知源信号")
        self.sim2.setFont(QFont("宋体", 11))
        self.sim3 = QPushButton("未知源信号")
        self.sim3.setFont(QFont("宋体", 11))
        self.sim4 = QPushButton("未知源信号")
        self.sim4.setFont(QFont("宋体", 11))
        self.sim5 = QPushButton("未知源信号")
        self.sim5.setFont(QFont("宋体", 11))
        self.sim6 = QPushButton("未知源信号")
        self.sim6.setFont(QFont("宋体", 11))

        self.player = QMediaPlayer()

        self.grid.addWidget(self.buttonWriteSD,1,0)
        self.grid.addWidget(self.buttonOpenFile,1,2)
        self.grid.addWidget(self.fileName, 1, 3)
        self.grid.addWidget(self.sample,1,4)
        self.grid.addWidget(self.sampleRate,1,5)
        self.grid.addWidget(self.chooseChannel,2, 0)
        self.grid.addWidget(self.combos,2,1)
        self.grid.addWidget(self.microphone, 2, 2)
        self.grid.addWidget(self.microphoneSeparationInMetres1,2,3)
        self.grid.addWidget(self.num,2,4)
        self.grid.addWidget(self.numSources1,2,5)
        self.grid.addWidget(self.buttonStart,3,0)
        self.grid.addWidget(self.processShow,3,1)
        self.grid.addWidget(self.showTip,3,2)
        self.grid.addWidget(self.sim1, 4, 0)
        self.grid.addWidget(self.sim2, 4, 1)
        self.grid.addWidget(self.sim3, 4, 2)
        self.grid.addWidget(self.sim4, 4, 3)
        self.grid.addWidget(self.sim5, 4, 4)
        self.grid.addWidget(self.sim6, 4, 5)



        # 信号与槽相应
        self.buttonWriteSD.clicked.connect(self.writeSD)
        self.buttonOpenFile.clicked.connect(self.openFile)
        self.buttonStart.clicked.connect(self.startGCCNMF)
        self.stopGCCNMF.connect(self.simWav)
        self.sim1.clicked.connect(self.simPlay1)
        self.sim2.clicked.connect(self.simPlay2)
        self.sim3.clicked.connect(self.simPlay3)
        self.sim4.clicked.connect(self.simPlay4)
    #调用exe写SD卡
    def writeSD(self):
        os.system(r"F:\Python\gcc-nmf-master\data\ReadDisk.exe")

    #窗口居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    #选择算法后显示窗口
    def showMainWindow(self):
        self.mainGround.setLayout(self.grid)

    # 获得采样率
    def getSampleRate(self, text):
        self.samplingRate = text
        print(self.samplingRate)
        print(type(self.samplingRate))

    #获得选择双通道的数据
    def getChooseNum(self,text):
        self.channelNumber = text
        if self.channelNumber == '1 4' or self.channelNumber == '2 5' or self.channelNumber == '3 6':
            self.microphoneSeparationInMetres1.setText('0.040000')
            self.microphoneSeparationInMetres = 0.04
        elif self.channelNumber == '1 3' or self.channelNumber == '2 4' or self.channelNumber == '3 5' \
            or self.channelNumber == '4 6' or self.channelNumber == '5 1' or self.channelNumber == '6 2':
            self.microphoneSeparationInMetres1.setText('0.034641')
            self.microphoneSeparationInMetres = 0.034641
        else:
            self.microphoneSeparationInMetres1.setText('0.020000')
            self.microphoneSeparationInMetres = 0.02
        self.channelNumber = self.channelNumber.replace(" ", '')
        print(self.channelNumber)
        print(type(self.channelNumber))

    #获得声源个数
    def getNumSources(self, text):
        self.numofSource =text
        print(self.numofSource)
        print(type(self.numofSource))

    def openFile(self):
        self.fileName1 = QFileDialog.getOpenFileName(self, '打开文件', 'F:\Python\gcc-nmf-master\data','原始音频文件(*.txt)')
        self.fileName.setText(self.fileName1[0])

    def startGCCNMF(self):
        self.showTip.setText("语音处理中,请耐心等候...")
        self.setStatusTip("处理语音中，请耐心等候")
        self.count = 1
        self.processShow.setValue(self.count)
        #先导入txt文件
        filePath = self.fileName.text()
        allMatrix = loadtxt(filePath)
        print(filePath)
        #取两列数据
        sampleRates = int(self.samplingRate)
        num0 = self.channelNumber
        num = int(num0)
        self.processShow.setValue(self.count*10)
        num1 = int(num / 10 - 1)
        num2 = num % 10 - 1
        print(num1)
        print(num2)
        mixMatrix1 = allMatrix[:, num1]
        mixMatrix2 = allMatrix[:, num2]
        mixMatrix1 = mixMatrix1 / 65536 * 20
        self.count = 3
        self.processShow.setValue(self.count * 10)
        mixMatrix2 = mixMatrix2 / 65536 * 20
        mixMatrix1 = mixMatrix1 - mean(mixMatrix1)
        mixMatrix2 = mixMatrix2 - mean(mixMatrix2)
        print("here")
        mixMatrix3 = column_stack((mixMatrix1, mixMatrix2))
        print(mixMatrix3.shape)
        mixMatrix = mixMatrix3.T
        [row, col] = mixMatrix.shape
        times = int(col / 240000)
        print(times)
        mixedName = filePath.rstrip('.txt')
        self.processShow.setValue(self.count * 10)
        #GCC-NMF参数
        windowSize = 1024
        fftSize = windowSize
        hopSize = 128
        windowFunction = hanning

        # TDOA params
        numTDOAs = 128

        # NMF params
        dictionarySize = 128
        numIterations = 100
        sparsityAlpha = 0

        self.count = 5
        self.processShow.setValue(self.count * 10)
        microphoneSeparationInMetres = self.microphoneSeparationInMetres
        print(microphoneSeparationInMetres)
        midSim = []
        numSources = int(self.numofSource)
        for i in range(times):
            midMatrix = mixMatrix[:, i * 240000 : (i+1) * 240000]
            mixFileName = mixedName + '_' + num0 + '_' +str(i+1) + '_mix' + '.wav'
            print(mixFileName)
            wavwrite(midMatrix, mixFileName, sampleRates)
            mixtureFileNamePrefix = mixFileName.rstrip('_mix.wav')
            mid = runGCCNMF(mixtureFileNamePrefix, windowSize, hopSize, numTDOAs,
                            microphoneSeparationInMetres, numSources, windowFunction )
            self.processStatus += 1
            midSim.append(list(mid))
        simFileName1 = mixedName.rstrip('_mix')
        self.count = 8
        self.processShow.setValue(self.count * 10)
        print(simFileName1)
        # midSimWav = array(midSim)
        if numSources == 2:
            mid = [[[],[]],[[],[]]]
        elif numSources == 3:
            mid = [[[],[]],[[],[]],[[],[]]]
        elif numSources == 4:
            mid = [[[],[]],[[],[]],[[],[]],[[],[]]]
        for i in range(numSources):
            for j in range(2):
                for k in range(times):
                    mid[i][j].extend(midSim[k][i][j])
            midSimWav = array(mid[i])
            print(midSimWav.shape)
            simFileName = simFileName1 + '_' + num0 + '_sim_'+ str(i+1) + '.wav'
            print(simFileName)
            wavwrite(midSimWav, simFileName, sampleRates)
        print('Finish')
        self.count = 10
        self.processShow.setValue(self.count * 10)
        self.showTip.setText("语音处理完毕！")
        self.stopGCCNMF.emit()

    def simWav(self):
        num = int(self.numofSource)

        self.setStatusTip("语音信号处理完毕")
        if num == 2:
            self.sim1.setText("源信号1")
            self.sim2.setText("源信号2")
        elif num == 3:
            self.sim1.setText("源信号1")
            self.sim2.setText("源信号2")
            self.sim3.setText("源信号3")
        elif num == 4:
            self.sim1.setText("源信号1")
            self.sim2.setText("源信号2")
            self.sim3.setText("源信号3")
            self.sim4.setText("源信号4")

    def playMusic(self):
        self.player.setVolume(100)
        self.player.play()

    def simPlay1(self):
        mixturename1 = self.fileName.text()
        mixtureFileName1 = mixturename1.rstrip('.txt')
        simname1 = mixtureFileName1+'_'+self.channelNumber+'_sim_'+'1'+'.wav'
        print(simname1)
        sound1 = QMediaContent(QUrl.fromLocalFile(simname1))
        self.player.setMedia(sound1)
        self.playMusic()

    def simPlay2(self):
        mixturename2 = self.fileName.text()
        mixtureFileName2 = mixturename2.rstrip('.txt')
        simname2 = mixtureFileName2+'_'+self.channelNumber+'_sim_'+'2'+'.wav'
        print(simname2)
        sound2 = QMediaContent(QUrl.fromLocalFile(simname2))
        self.player.setMedia(sound2)
        self.playMusic()

    def simPlay3(self):
        mixturename3 = self.fileName.text()
        mixtureFileName3 = mixturename3.rstrip('.txt')
        simname3 = mixtureFileName3+'_'+self.channelNumber+'_sim_'+'3'+'.wav'
        sound3 = QMediaContent(QUrl.fromLocalFile(simname3))
        self.player.setMedia(sound3)
        self.playMusic()

    def simPlay4(self):
        mixturename4 = self.fileName.text()
        mixtureFileName4 = mixturename4.rstrip('.txt')
        simname4 = mixtureFileName4+'_'+self.channelNumber+'_sim_'+'4'+'.wav'
        sound4 = QMediaContent(QUrl.fromLocalFile(simname4))
        self.player.setMedia(sound4)
        self.playMusic()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    original = OriginalWindows()
    original.show()
    sys.exit(app.exec_())