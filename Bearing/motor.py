import binascii
from PyQt5.QtCore import QObject
from PyQt5.Qt import pyqtSignal, QThread
import time

class Motor(QObject):
    Warning_Signal = pyqtSignal(str)

    def __init__(self, serial):
        super(Motor, self).__init__()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self.command = []
        self.serial = serial

    def set_serial(self, serial):
        self.serial = serial

    def manualcontrol_execute(self, speed, step):
        if (speed != '') & (step != ''):
            step = int(step)
            speed = int(speed)
            if (4294967295 > step > (-4294967295)) & (0 < speed < 65535):
                try:
                    self.serial.send_data(self.appoint_command(speed, step))
                except:
                    self.Warning_Signal.emit('电机控制串口未打开！')
            else:
                self.Warning_Signal.emit('请设置正确的速度和步数！')
        else:
            self.Warning_Signal.emit('请设置正确的速度和步数！')

    def manualcontrol_forward(self, speed):
        try:
            self.serial.send_data(self.check_command())
            information = self.serial.read_data(16)
            status_now = self.analyse_result(information)[2]
            if status_now == '00':
                self.serial.send_data(bytes.fromhex('55 AA 5A A5 20 10 27 cc'))
            while status_now != '01':
                self.serial.send_data(self.check_command())
                info = self.serial.read_data(16)
                status_now = self.analyse_result(info)[2]
            if speed == '':
                speed = 100
            speed = self.ten2sixteen(speed, 4)
            self.serial.send_data(bytes.fromhex('55 AA 5A A5 22 ' + speed + 'cc'))
        except:
            self.Warning_Signal.emit('电机转动失败！')

    def manualcontrol_reverse(self, speed):
        try:
            self.serial.send_data(self.check_command())
            information = self.serial.read_data(16)
            status_now = self.analyse_result(information)[2]
            if status_now == '00':
                self.serial.send_data(bytes.fromhex('55 AA 5A A5 20 10 27 cc'))
            while status_now != '01':
                self.serial.send_data(self.check_command())
                info = self.serial.read_data(16)
                status_now = self.analyse_result(info)[2]
            if speed == '':
                speed = 100
            speed = self.ten2sixteen(speed, 4)
            self.serial.send_data(bytes.fromhex('55 AA 5A A5 21 ' + speed + 'cc'))
        except:
            self.Warning_Signal.emit('电机转动失败！')

    def manualcontrol_returnzeropoint(self, handle):
        # 考虑升级为无超调的PID控制，就可以应对所有情况
        speed = 150
        n = 0
        while len(handle._all_data.force_switch) == 0:
            pass
        while 1:
            if speed > 10:
                speed = speed - 20
            if handle._all_data.force_switch[-1] < 0:
                print('<1')
                self.manualcontrol_forward(speed)
            if handle._all_data.force_switch[-1] > 1:
                print('>2')
                self.manualcontrol_reverse(speed)
            if 0 < handle._all_data.force_switch[-1] < 1:
                print('ok')
                self.serial.send_data(self.step_RF_stop_command())
                time.sleep(1)
                if 0 < handle._all_data.force_switch[-1] < 1:
                    break
            time.sleep(speed / 100.00)
            n += 1

    def autocontrol_command_execute(self, command):
        for i in command:
            self.serial.send_data(bytes.fromhex('55 AA 5A A5 00'))
            info = self.serial.read_data(16)
            status_now = self.analyse_result(info)[2]
            while status_now != '01':
                self.serial.send_data(bytes.fromhex('55 AA 5A A5 00'))
                info = self.serial.read_data(16)
                status_now = self.analyse_result(info)[2]
            if type(i) == str:
                print('aaa')
                time.sleep(int(i.split(' ')[1]))
                continue
            self.serial.send_data(i)

    def ten2sixteen(self, data, bit):  # 4位是速度，8位是位置
        data = int(data)
        if data >= 0:
            data = hex(data).split(r'0x')[1]
            if bit == 4:
                for i in range(bit - len(data)):
                    data = '0' + data
                data = data[2:] + ' ' + data[:2] + ' '
            elif bit == 8:
                for i in range(bit - len(data)):
                    data = '0' + data
                data = data[6:8] + ' ' + data[4:6] + ' ' + data[2:4] + ' ' + data[0:2] + ' '
        else:
            data = hex(data & 0xffffffff).split(r'0x')[1]
            data = data[6:8] + ' ' + data[4:6] + ' ' + data[2:4] + ' ' + data[0:2] + ' '
        return data

    def appoint_command(self, speed, step):
        speed = self.ten2sixteen(speed, 4)
        step = self.ten2sixteen(step, 8)
        return bytes.fromhex('55 AA 5A A5 10 ' + speed + step + '00 00 00 00 CC')

    def check_command(self):
        return bytes.fromhex('55 AA 5A A5 00')

    def pause_command(self):
        return bytes.fromhex('55 AA 5A A5 01')

    def continue_command(self):
        return bytes.fromhex('55 AA 5A A5 02')

    def stop_motor_command(self):
        return bytes.fromhex('55 AA 5A A5 03')

    def step_RF_stop_command(self):
        return bytes.fromhex('55 AA 5A A5 20 00 00 cc')

    def step_right_command(self, speed):
        speed = self.ten2sixteen(speed, 4)
        return bytes.fromhex('55 AA 5A A5 21 ' + speed + 'cc')

    def step_left_command(self, speed):
        speed = self.ten2sixteen(speed, 4)
        return bytes.fromhex('55 AA 5A A5 22 ' + speed + 'cc')

    def analyse_result(self, data):
        data = binascii.b2a_hex(data).decode('utf-8')
        xPosition = data[4:12]
        speed_now = data[20:24]
        status_now = data[28:30]
        return xPosition, speed_now, status_now



