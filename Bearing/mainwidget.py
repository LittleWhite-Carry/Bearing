import configparser
import os
import sys
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QWidget, QGroupBox, QComboBox, QVBoxLayout, QTabWidget, QLabel, QLineEdit, \
    QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QListWidget, QGridLayout
from PyQt5.QtCore import pyqtSignal, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication
from Bearing.handle_data import Handle_Data
from Bearing.read_thread import Read_Thread
from Bearing.bearing_serial import Bearing_Serial
from Bearing.motor import Motor
import cgitb


class Bearing(QMainWindow):
    ReadThreadStart_Singal = pyqtSignal(int)
    ManualControlExecute_Signal = pyqtSignal(object, object)
    ManualControlForward_Signal = pyqtSignal(object)
    ManualControlReveres_Signal = pyqtSignal(object)
    ManualControlReturnZeroPoint_Signal = pyqtSignal(object)
    AutoControlCommandExecute_Signal = pyqtSignal(object)

    def __init__(self):
        super(Bearing, self).__init__()

        self.save_path = sys.path[0]
        self._serial1_is_open = 0
        self._serial2_is_open = 0
        self._plot_times = 0
        self._plot_first_data = []
        self._plot_last_data = []
        self._experiment2_data_resistance = []
        self._experiment2_data_current = []

        self.initUi()
        self.set_attribute()
        self.set_layout()
        self.init_conf()

        self._serial_1 = Bearing_Serial(self._serial_information1_port_combox.currentText(),
                                       self._serial_information1_baudrate_combox.currentText(), 'modbus')
        self._serial_2 = Bearing_Serial(self._serial_information2_port_combox.currentText(),
                                       self._serial_information2_baudrate_combox.currentText(), 'serial')
        self._serial_3 = Bearing_Serial(self._serial_information3_port_combox.currentText(),
                                        115200, 'serial')
        self._handle_data = Handle_Data()
        self._read_thread = Read_Thread(self._serial_1, self._serial_2)
        self._motor = Motor(self._serial_3)

        self.signal_connect_slot()
        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Show Data')
        self.show()

    def initUi(self):
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage(' ')

        self._serial_information1_groupbox = QGroupBox('串口1')
        self._serial_information1_port_combox = QComboBox()
        self._serial_information1_baudrate_combox = QComboBox()
        self._serial_information1_pushbutton = QPushButton('连接')

        self._serial_information2_groupbox = QGroupBox('串口2')
        self._serial_information2_port_combox = QComboBox()
        self._serial_information2_baudrate_combox = QComboBox()
        self._serial_information2_pushbutton = QPushButton('连接')

        self._experiment1_groupbox = QGroupBox('实验一')
        self._experiment1_datasize_label = QLabel('数据采集量')
        self._experiment1_datasize_lineedit = QLineEdit('400')
        self._experiment1_start_pushbutton = QPushButton('开始')
        self._experiment1_stop_pushbutton = QPushButton('停止')
        self._experiment1_clear_pushbutton = QPushButton('清除')

        self._experiment2_groupbox = QGroupBox('实验二')
        self._experiment2_current_label = QLabel('电流大小')
        self._experiment2_current_lineedit = QLineEdit('0.0')
        self._experiment2_readresistance_pushbutton = QPushButton('获取阻值')
        self._experiment2_save_pushbutton = QPushButton('保存电流-电阻')

        self._plot_tabwidget = QTabWidget()
        self._plot_fr_widget = QWidget()
        self._plot_fd_widget = QWidget()
        self._plot_tabwidget.addTab(self._plot_fr_widget, 'F-R')
        self._plot_tabwidget.addTab(self._plot_fd_widget, 'F-L')

        self._control_serial_groupbox = QGroupBox('控制器串口')
        self._serial_information3_port_combox = QComboBox()
        self._serial_information3_pushbutton = QPushButton('连接')

        self._manualcontrol_groupbox = QGroupBox('手动控制')
        self._manualcontrol_step_label = QLabel('步 数')
        self._manualcontrol_step_lineedit = QLineEdit()
        self._manualcontrol_speed_label = QLabel('速 度')
        self._manualcontrol_speed_lineedit = QLineEdit()
        self._manualcontrol_execute_pushbutton = QPushButton('执行')
        self._manualcontrol_returnzeropoint_pushbutton = QPushButton('返回零点')
        self._manualcontrol_forward_pushbutton = QPushButton('正转')
        self._manualcontrol_reverse_pushbutton = QPushButton('反转')
        self._manualcontrol_pause_pushbutton = QPushButton('暂停')
        self._manualcontrol_stop_pushbutton = QPushButton('停止')

        self._autocontrol_groupbox = QGroupBox('自动控制')
        self._autocontrol_command_combox = QComboBox()
        self._autocontrol_command_lineedit = QLineEdit()
        self._autocontrol_command_add_pushbutton = QPushButton('添加')
        self._autocontrol_command_del_pushbutton = QPushButton('删除')
        self._autocontrol_command_execute_pushbutton = QPushButton('执行')
        self._autocontrol_pause_pushbutton = QPushButton('暂停')
        self._autocontrol_stop_pushbutton = QPushButton('停止')
        self._autocontrol_listwidget = QListWidget()

    def set_attribute(self):
        port = []
        baudrate = ['4800', '9600', '19200', '38400', '56000', '115200']
        command = ['速度', '步数', '暂停（秒）', '循环次数']
        left_width = 250
        right_width = 300
        for i in range(1, 9):
            port.append('COM%d' % i)
        self._serial_information1_port_combox.addItems(port)
        self._serial_information1_baudrate_combox.addItems(baudrate)
        self._serial_information2_port_combox.addItems(port)
        self._serial_information2_baudrate_combox.addItems(baudrate)
        self._serial_information1_groupbox.setMaximumWidth(left_width / 2)
        self._serial_information2_groupbox.setMaximumWidth(left_width / 2)
        self._serial_information1_groupbox.setMaximumHeight(left_width * 2 / 3)
        self._serial_information2_groupbox.setMaximumHeight(left_width * 2 / 3)
        self._experiment1_groupbox.setMaximumWidth(left_width)
        self._experiment2_groupbox.setMaximumWidth(left_width)

        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.ax1 = self.figure1.add_subplot(111)
        self.toolbar1 = NavigationToolbar(self.canvas1, self.widget)
        self.PlotBox1 = QVBoxLayout(self._plot_fr_widget)
        self.PlotBox1.addWidget(self.toolbar1)
        self.PlotBox1.addWidget(self.canvas1)
        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.add_subplot(111)
        self.toolbar2 = NavigationToolbar(self.canvas2, self.widget)
        self.PlotBox2 = QVBoxLayout(self._plot_fd_widget)
        self.PlotBox2.addWidget(self.toolbar2)
        self.PlotBox2.addWidget(self.canvas2)
        self.ax1.set_title('F-R')
        self.ax1.set_xlabel('F/N')
        self.ax1.set_ylabel('R/Ω')
        self.ax2.set_title('F-L')
        self.ax2.set_ylabel('F/N')
        self.ax2.set_xlabel('L/mm')
        self.canvas1.draw()
        self.canvas2.draw()

        self._serial_information3_port_combox.addItems(port)
        self._serial_information3_port_combox.setMaximumHeight(self._serial_information3_pushbutton.height())
        self._manualcontrol_step_label.setAlignment(Qt.AlignHCenter)
        self._manualcontrol_speed_label.setAlignment(Qt.AlignHCenter)
        self._manualcontrol_step_lineedit.setPlaceholderText('步数<2000')
        self._manualcontrol_speed_lineedit.setPlaceholderText('速度<300')
        self._manualcontrol_groupbox.setMaximumWidth(right_width)
        self._autocontrol_groupbox.setMaximumWidth(right_width)

        self._autocontrol_command_combox.addItems(command)

    def set_layout(self):
        self._serial1_layout = QVBoxLayout(self._serial_information1_groupbox)
        self._serial1_layout.addWidget(self._serial_information1_port_combox)
        self._serial1_layout.addWidget(self._serial_information1_baudrate_combox)
        self._serial1_layout.addWidget(self._serial_information1_pushbutton)

        self._serial2_layout = QVBoxLayout(self._serial_information2_groupbox)
        self._serial2_layout.addWidget(self._serial_information2_port_combox)
        self._serial2_layout.addWidget(self._serial_information2_baudrate_combox)
        self._serial2_layout.addWidget(self._serial_information2_pushbutton)

        self._experiment1_layout = QGridLayout(self._experiment1_groupbox)
        self._experiment1_layout.addWidget(self._experiment1_datasize_label)
        self._experiment1_layout.addWidget(self._experiment1_datasize_lineedit, 0, 1)
        self._experiment1_layout.addWidget(self._experiment1_start_pushbutton, 1, 0, 1, -1)
        self._experiment1_layout.addWidget(self._experiment1_stop_pushbutton, 2, 0, 1, -1)
        self._experiment1_layout.addWidget(self._experiment1_clear_pushbutton, 3, 0, 1, -1)

        self._experiment2_layout = QGridLayout(self._experiment2_groupbox)
        self._experiment2_layout.addWidget(self._experiment2_current_label)
        self._experiment2_layout.addWidget(self._experiment2_current_lineedit, 0, 1)
        self._experiment2_layout.addWidget(self._experiment2_readresistance_pushbutton, 1, 0, 1, -1)
        self._experiment2_layout.addWidget(self._experiment2_save_pushbutton, 2, 0, 1, -1)

        self._left_layout = QGridLayout()
        self._left_layout.addWidget(self._serial_information1_groupbox)
        self._left_layout.addWidget(self._serial_information2_groupbox, 0, 1)
        self._left_layout.addWidget(self._experiment1_groupbox, 1, 0, 1, -1)
        self._left_layout.addWidget(self._experiment2_groupbox, 2, 0, 1, -1)

        self._control_serial_layout = QHBoxLayout(self._control_serial_groupbox)
        self._control_serial_layout.addWidget(self._serial_information3_port_combox)
        self._control_serial_layout.addWidget(self._serial_information3_pushbutton)

        self._manualcontrol_layout = QGridLayout(self._manualcontrol_groupbox)
        self._manualcontrol_layout.addWidget(self._manualcontrol_step_label)
        self._manualcontrol_layout.addWidget(self._manualcontrol_step_lineedit, 0, 1)
        self._manualcontrol_layout.addWidget(self._manualcontrol_speed_label, 1, 0)
        self._manualcontrol_layout.addWidget(self._manualcontrol_speed_lineedit, 1, 1)
        self._manualcontrol_layout.addWidget(self._manualcontrol_execute_pushbutton, 2, 0)
        self._manualcontrol_layout.addWidget(self._manualcontrol_returnzeropoint_pushbutton, 2, 1)
        self._manualcontrol_layout.addWidget(self._manualcontrol_forward_pushbutton, 3, 0)
        self._manualcontrol_layout.addWidget(self._manualcontrol_reverse_pushbutton, 3, 1)
        self._manualcontrol_layout.addWidget(self._manualcontrol_pause_pushbutton, 4, 0)
        self._manualcontrol_layout.addWidget(self._manualcontrol_stop_pushbutton, 4, 1)

        self._autocontrol_layout = QGridLayout(self._autocontrol_groupbox)
        self._autocontrol_layout.addWidget(self._autocontrol_command_combox)
        self._autocontrol_layout.addWidget(self._autocontrol_command_lineedit, 0, 1)
        self._autocontrol_layout.addWidget(self._autocontrol_command_add_pushbutton, 1, 0)
        self._autocontrol_layout.addWidget(self._autocontrol_command_del_pushbutton, 1, 1)
        self._autocontrol_layout.addWidget(self._autocontrol_command_execute_pushbutton, 2, 0, 1, -1)
        self._autocontrol_layout.addWidget(self._autocontrol_pause_pushbutton, 3, 0)
        self._autocontrol_layout.addWidget(self._autocontrol_stop_pushbutton, 3, 1)
        self._autocontrol_layout.addWidget(self._autocontrol_listwidget, 4, 0, 1, -1)

        self._right_layout = QGridLayout()
        self._right_layout.addWidget(self._control_serial_groupbox, 0, 0, 1, -1)
        self._right_layout.addWidget(self._manualcontrol_groupbox, 1, 0, 1, -1)
        self._right_layout.addWidget(self._autocontrol_groupbox, 2, 0, 1, -1)

        self._main_layout = QGridLayout()
        self._main_layout.addLayout(self._left_layout, 0, 0)
        self._main_layout.addWidget(self._plot_tabwidget, 0, 1)
        self._main_layout.addLayout(self._right_layout, 0, 2)

        self.widget.setLayout(self._main_layout)

    def signal_connect_slot(self):
        self._serial_information1_pushbutton.clicked.connect(self.serial_information1_pushbutton_clicked)
        self._serial_information2_pushbutton.clicked.connect(self.serial_information2_pushbutton_clicked)
        self._serial_information3_pushbutton.clicked.connect(self.serial_information3_pushbutton_clicked)

        self._experiment1_stop_pushbutton.clicked.connect(self.experiment1_stop_pushbutton_clicked)
        self._experiment1_start_pushbutton.clicked.connect(self.experiment1_start_pushbutton_clicked)
        self._experiment1_clear_pushbutton.clicked.connect(self.experiment1_clear_pushbutton_clicked)

        self._experiment2_current_lineedit.returnPressed.connect(self.read_resistance)      # 行编辑框的回车事件处理
        self._experiment2_save_pushbutton.clicked.connect(self.experiment2_save_pushbutton_clicked)
        self._experiment2_readresistance_pushbutton.clicked.connect(self.read_resistance)

        self._manualcontrol_execute_pushbutton.clicked.connect(self.manualcontrol_execute_pushbutton_clicked)
        self._manualcontrol_returnzeropoint_pushbutton.clicked.connect(self.manualcontrol_returnzeropoint_pushbutton_clicked)
        self._manualcontrol_forward_pushbutton.clicked.connect(self.manualcontrol_forward_pushbutton_clicked)
        self._manualcontrol_reverse_pushbutton.clicked.connect(self.manualcontrol_reverse_pushbutton_clicked)
        self._manualcontrol_pause_pushbutton.clicked.connect(self.manualcontrol_pause_pushbutton_clicked)
        self._manualcontrol_stop_pushbutton.clicked.connect(self.manualcontrol_stop_pushbutton_clicked)

        self._autocontrol_command_combox.activated.connect(self.autocontrol_command_lineedit_setFocus)
        self._autocontrol_command_add_pushbutton.clicked.connect(self.autocontrol_command_add_pushbutton_clicked)
        self._autocontrol_command_del_pushbutton.clicked.connect(self.autocontrol_command_del_pushbutton_clicked)
        self._autocontrol_command_execute_pushbutton.clicked.connect(self.autocontrol_command_execute_pushbutton_clicked)
        self._autocontrol_pause_pushbutton.clicked.connect(self.autocontrol_pause_pushbutton_clicked)
        self._autocontrol_stop_pushbutton.clicked.connect(self.autocontrol_stop_pushbutton_clicked)

        self.ReadThreadStart_Singal.connect(self._read_thread.read_data, type=Qt.QueuedConnection)
        self.ManualControlExecute_Signal.connect(self._motor.manualcontrol_execute)
        self.ManualControlForward_Signal.connect(self._motor.manualcontrol_forward)
        self.ManualControlReveres_Signal.connect(self._motor.manualcontrol_reverse)
        self.ManualControlReturnZeroPoint_Signal.connect(self._motor.manualcontrol_returnzeropoint)
        self.AutoControlCommandExecute_Signal.connect(self._motor.autocontrol_command_execute)

        self._serial_1.Warning_Signal.connect(self.warning_message)
        self._serial_2.Warning_Signal.connect(self.warning_message)
        self._serial_3.Warning_Signal.connect(self.warning_message)
        self._read_thread.ReadComplete_Signal.connect(self._handle_data.handle, type=Qt.QueuedConnection)
        self._read_thread.SaveData_Signal.connect(self._handle_data.save_all_data, type=Qt.QueuedConnection)
        self._handle_data.HandleComplete_Signal.connect(self.plot, type=Qt.QueuedConnection)
        self._handle_data.TranData_Signal.connect(self.save_data, type=Qt.QueuedConnection)
        self._motor.Warning_Signal.connect(self.warning_message)

    def serial_information1_pushbutton_clicked(self):
        self._serial_1.set_setting(self._serial_information1_port_combox.currentText(),
                                       self._serial_information1_baudrate_combox.currentText(), 'modbus')
        if self._serial_1.open_serial():
            self._serial1_is_open = 1

    def serial_information2_pushbutton_clicked(self):
        self._serial_2.set_setting(self._serial_information2_port_combox.currentText(),
                                  self._serial_information2_baudrate_combox.currentText(), 'serial')
        if self._serial_2.open_serial():
            self._serial2_is_open = 1

    def serial_information3_pushbutton_clicked(self):
        self._serial_3.set_setting(self._serial_information3_port_combox.currentText(), 115200, 'serial')
        self._serial_3.open_serial()
        self._motor.set_serial(self._serial_3)
        self._motor._thread.start()

    def experiment1_start_pushbutton_clicked(self):
        self.ax1.clear()
        self.canvas1.draw()
        self.ax2.clear()
        self.canvas2.draw()
        self.ax1.set_title('F-R')
        self.ax1.set_xlabel('F/N')
        self.ax1.set_ylabel('R/Ω')
        self.ax2.set_title('F-L')
        self.ax2.set_ylabel('F/N')
        self.ax2.set_xlabel('L/mm')
        if (self._serial1_is_open == 0) | (self._serial2_is_open == 0):
            self.warning_message('串口未打开！')
            return 0
        QMessageBox().warning(self, 'Warning', u"请确保台式万用表处于Fast Print模式，\n并确保传感器段通电！",
                                    QMessageBox.Yes)
        self._plot_times = 0
        self._plot_first_data = []
        self._plot_last_data = []
        self._handle_data.clear_all_data()
        self._read_thread._thread.start()
        self._handle_data._thread.start()
        self._read_thread.set_serial(self._serial_1, self._serial_2)
        self.ReadThreadStart_Singal.emit(int(self._experiment1_datasize_lineedit.text()))

    def experiment1_stop_pushbutton_clicked(self):
        self._read_thread.stop_function()

    def experiment1_clear_pushbutton_clicked(self):
        self.ax1.clear()
        self.canvas1.draw()
        self.ax2.clear()
        self.canvas2.draw()
        self.ax1.set_title('F-R')
        self.ax1.set_xlabel('F/N')
        self.ax1.set_ylabel('R/Ω')
        self.ax2.set_title('F-L')
        self.ax2.set_ylabel('F/N')
        self.ax2.set_xlabel('L/mm')

    def experiment2_save_pushbutton_clicked(self):
        self.save_path = QFileDialog.getSaveFileName(self, "选择目录", self.save_path)[0]
        if self.save_path == '':
            return 0
        data = pd.DataFrame(columns=['resistance', 'current'])
        length = len(self._experiment2_data_resistance)
        i = 0
        while i < length:
            data = data.append(
                {'resistance': self._experiment2_data_resistance[i], 'current': self._experiment2_data_current[i]},
                ignore_index=True)
            i += 1
        if not os.path.exists(self.save_path + '.csv'):
            data.to_csv(self.save_path + '.csv')
            self.statusBar().showMessage('Save %s Done' % self.save_path)
        else:
            if QMessageBox().question(self, 'Warning', u"文件已存在！\n是否覆盖？", QMessageBox.Yes|QMessageBox.No) == 16384:
                os.remove(self.save_path + '.csv')
                data.to_csv(self.save_path + '.csv')
                self.statusBar().showMessage('Save %s Done' % self.save_path)

    def autocontrol_command_lineedit_setFocus(self):
        self._autocontrol_command_lineedit.selectAll()
        self._autocontrol_command_lineedit.setFocus()

    def manualcontrol_execute_pushbutton_clicked(self):
        self.ManualControlExecute_Signal.emit(self._manualcontrol_speed_lineedit.text(), self._manualcontrol_step_lineedit.text())

    def manualcontrol_returnzeropoint_pushbutton_clicked(self):
        self.experiment1_start_pushbutton_clicked()
        self.ManualControlReturnZeroPoint_Signal.emit(self._handle_data)

    def manualcontrol_forward_pushbutton_clicked(self):
        self.ManualControlForward_Signal.emit(self._manualcontrol_speed_lineedit.text())

    def manualcontrol_reverse_pushbutton_clicked(self):
        self.ManualControlReveres_Signal.emit(self._manualcontrol_speed_lineedit.text())

    def manualcontrol_pause_pushbutton_clicked(self):
        if self._manualcontrol_pause_pushbutton.text() == '暂停':
            self._serial_3.send_data(self._motor.pause_command())
            self._manualcontrol_pause_pushbutton.setText('继续')
        elif self._manualcontrol_pause_pushbutton.text() == '继续':
            self._serial_3.send_data(self._motor.continue_command())
            self._manualcontrol_pause_pushbutton.setText('暂停')

    def manualcontrol_stop_pushbutton_clicked(self):
        if self._manualcontrol_pause_pushbutton.text() == '暂停':
            self._serial_3.send_data(self._motor.pause_command())
            self._serial_3.send_data(self._motor.stop_motor_command())
        elif self._manualcontrol_pause_pushbutton.text() == '继续':
            self._serial_3.send_data(self._motor.stop_motor_command())
            self._manualcontrol_pause_pushbutton.setText('暂停')

    def autocontrol_command_add_pushbutton_clicked(self):
        if self._autocontrol_command_lineedit.text() == '':
            self.warning_message('填写正确参数！')
            return 0
        elif self._autocontrol_command_combox.currentText() == '速度':
            self._autocontrol_listwidget.insertItem(self._autocontrol_listwidget.currentRow()+1, '设置速度 ' + self._autocontrol_command_lineedit.text())
        elif self._autocontrol_command_combox.currentText() == '步数':
            self._autocontrol_listwidget.insertItem(self._autocontrol_listwidget.currentRow()+1, '设置步数 ' + self._autocontrol_command_lineedit.text())
        elif self._autocontrol_command_combox.currentText() == '暂停（秒）':
            self._autocontrol_listwidget.insertItem(self._autocontrol_listwidget.currentRow() + 1,
                                                    '设置暂停 ' + self._autocontrol_command_lineedit.text())
        elif self._autocontrol_command_combox.currentText() == '循环次数':
            loop_digtal = self._autocontrol_command_lineedit.text().replace('，', ',')
            [start, times] = loop_digtal.split(',')
            self._autocontrol_listwidget.insertItem(self._autocontrol_listwidget.currentRow()+1, '设置循环 %s,%s' % (start, times))
        self._autocontrol_listwidget.setCurrentRow(self._autocontrol_listwidget.count()-1)
        self.autocontrol_command_lineedit_setFocus()

    def autocontrol_command_del_pushbutton_clicked(self):
        self._autocontrol_listwidget.takeItem(self._autocontrol_listwidget.currentRow())

    def autocontrol_command_execute_pushbutton_clicked(self):    # 无法嵌套循环
        command1 = []
        command = []
        loopTimes = 0
        times = 1
        for i in range(self._autocontrol_listwidget.count()-1, -1, -1):
            if '设置循环' in self._autocontrol_listwidget.item(i).text():
                loopTimes += 1
                [start, times] = self._autocontrol_listwidget.item(i).text().split()[1].split(',')
                end = i
        if loopTimes > 1:
            self.warning_message('不能处理嵌套循环！')
            return 0

        for i in range(self._autocontrol_listwidget.count()):
            if '设置步数' in self._autocontrol_listwidget.item(i).text():
                step = self._autocontrol_listwidget.item(i).text().split()[1]
                for j in range(i, -1, -1):
                    if '设置速度' in self._autocontrol_listwidget.item(j).text():
                        speed = self._autocontrol_listwidget.item(j).text().split()[1]
                        break
                    speed = 100
                command1.append(self._motor.appoint_command(speed, step))
            elif '设置暂停' in self._autocontrol_listwidget.item(i).text():
                command1.append('sleep ' + self._autocontrol_listwidget.item(i).text().split(' ')[1])
            else:
                command1.append(' ')

        if loopTimes > 0:
            for k1 in range(int(times)):
                for k2 in range(int(start)-1, int(end)):
                    if command1[k2] != ' ':
                        command.append(command1[k2])
        else:
            for k1 in range(command1.count(' ')):
                command1.remove(' ')
            command = command1
        self.AutoControlCommandExecute_Signal.emit(command)

    def autocontrol_pause_pushbutton_clicked(self):
        if self._autocontrol_pause_pushbutton.text() == '暂停':
            self._serial_3.send_data(self._motor.pause_command())
            self._autocontrol_pause_pushbutton.setText('继续')
        elif self._autocontrol_pause_pushbutton.text() == '继续':
            self._serial_3.send_data(self._motor.continue_command())
            self._autocontrol_pause_pushbutton.setText('暂停')

    def autocontrol_stop_pushbutton_clicked(self):
        if self._autocontrol_pause_pushbutton.text() == '暂停':
            self._serial_3.send_data(self._motor.pause_command())
            self._serial_3.send_data(self._motor.stop_motor_command())
        elif self._autocontrol_pause_pushbutton.text() == '继续':
            self._serial_3.send_data(self._motor.stop_motor_command())
            self._autocontrol_pause_pushbutton.setText('暂停')

    def warning_message(self, content):
        QMessageBox().warning(self, 'Warning', content, QMessageBox.Yes)

    def init_conf(self):
        if not os.path.exists(sys.path[0] + "\ZhiZuo.conf"):
            with open(sys.path[0] + '\ZhiZuo.conf', 'w+') as f:
                cf = configparser.ConfigParser()
                cf.add_section('COM1')
                cf.set('COM1', 'port', self._serial_information1_port_combox.currentText())
                cf.set('COM1', 'baudrate', self._serial_information1_baudrate_combox.currentText())
                cf.add_section('COM2')
                cf.set('COM2', 'port', self._serial_information2_port_combox.currentText())
                cf.set('COM2', 'baudrate', self._serial_information2_baudrate_combox.currentText())
                cf.add_section('COM3')
                cf.set('COM3', 'port', self._serial_information3_port_combox.currentText())
                cf.add_section('DATA')
                cf.set('DATA', 'size', self._experiment1_datasize_lineedit.text())
                cf.write(f)
        else:
            cf = configparser.ConfigParser()
            cf.read(sys.path[0] + '\ZhiZuo.conf')
            try:
                self._serial_information1_port_combox.setCurrentText(cf.get('COM1', 'port'))
                self._serial_information1_baudrate_combox.setCurrentText(cf.get('COM1', 'baudrate'))
                self._serial_information2_port_combox.setCurrentText(cf.get('COM2', 'port'))
                self._serial_information2_baudrate_combox.setCurrentText(cf.get('COM2', 'baudrate'))
                self._serial_information3_port_combox.setCurrentText(cf.get('COM3', 'port'))
                self._experiment1_datasize_lineedit.setText(cf.get('DATA', 'size'))
            except:
                os.remove(sys.path[0] + "\ZhiZuo.conf")

    def plot(self, F, R, D):
        if self._plot_times == 0:
            self._plot_first_data = [F, R, D]
            self._plot_last_data = [F, R, D]
        else:
            self.ax1.plot([self._plot_last_data[0], F], [self._plot_last_data[1], R])
            self.ax1.plot([self._plot_last_data[0], F], [self._plot_last_data[1], R], 'k.')
            self.ax2.plot([self._plot_last_data[0] - self._plot_first_data[0], F - self._plot_first_data[0]],
                          [self._plot_last_data[2] - self._plot_first_data[2], R - self._plot_first_data[2]])
            self.ax2.plot([self._plot_last_data[0] - self._plot_first_data[0], F - self._plot_first_data[0]],
                          [self._plot_last_data[2] - self._plot_first_data[2], R - self._plot_first_data[2]], 'k.')
            self._plot_last_data = [F, R, D]
        self._plot_times += 1
        self.canvas1.draw()
        self.canvas2.draw()
        self.statusBar().showMessage('Now is %d' % self._plot_times)

    def read_resistance(self):
        if self._serial2_is_open == 0:
            self.warning_message('串口未打开！')
            return 0
        self._experiment2_data_current.append(self._experiment2_current_lineedit.text())
        self._experiment2_data_resistance.append(self._handle_data.handle_resistance(self._serial_2.read_data()))
        self._experiment2_current_lineedit.selectAll()
        self.statusBar().showMessage('Get %s Succed' % (self._experiment2_current_lineedit.text()))

    def save_data(self, alldata):
        self.save_path = QFileDialog.getSaveFileName(self, "选择目录", self.save_path)[0]
        if self.save_path == '':
            return 0
        data = pd.DataFrame(columns=['force_original', 'force_switch', 'force_stress', 'resistance', 'displacement'])
        length = len(alldata.force_original)
        i = 0
        while i < length:
            data = data.append({'force_original': alldata.force_original[i], 'force_switch': alldata.force_switch[i],
                                'force_stress': alldata.force_stress[i], 'resistance': alldata.resistance[i],
                                'displacement': alldata.displacement[i], 'time': alldata.time[i] - alldata.time[0]},
                               ignore_index=True)
            i += 1
        if not os.path.exists(self.save_path + '.csv'):
            data.to_csv(self.save_path + '.csv')
            self.figure1.savefig(self.save_path + '-FR' + '.jpg', dpi=1000)
            self.figure2.savefig(self.save_path + '-FL' + '.jpg', dpi=1000)
            self.statusBar().showMessage('Save %s Done' % self.save_path)
        else:
            if QMessageBox().question(self, 'Warning', u"文件已存在！\n是否覆盖？", QMessageBox.Yes|QMessageBox.No) == 16384:
                os.remove(self.save_path + '.csv')
                os.remove(self.save_path + '-FR' + '.jpg')
                os.remove(self.save_path + '-FL' + '.jpg')
                data.to_csv(self.save_path + '.csv')
                self.figure1.savefig(self.save_path + '-FR' + '.jpg', dpi=1000)
                self.figure2.savefig(self.save_path + '-FL' + '.jpg', dpi=1000)
                self.statusBar().showMessage('Save %s Done' % (self.save_path + '.csv'))
                self.statusBar().showMessage('Save %s Done' % self.save_path)

    def closeEvent(self, *args, **kwargs):
        cf = configparser.ConfigParser()
        cf.read(sys.path[0] + '\ZhiZuo.conf')
        cf.set('COM1', 'port', self._serial_information1_port_combox.currentText())
        cf.set('COM1', 'baudrate', self._serial_information1_baudrate_combox.currentText())
        cf.set('COM2', 'port', self._serial_information2_port_combox.currentText())
        cf.set('COM2', 'baudrate', self._serial_information2_baudrate_combox.currentText())
        cf.set('COM3', 'port', self._serial_information3_port_combox.currentText())
        cf.set('DATA', 'size', self._experiment1_datasize_lineedit.text())
        with open(sys.path[0] + '\ZhiZuo.conf', 'w') as f:
            cf.write(f)

if __name__ == '__main__':
    cgitb.enable(format='text')
    app = QApplication(sys.argv)
    bear = Bearing()
    sys.exit(app.exec_())