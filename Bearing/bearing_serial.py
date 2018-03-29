from PyQt5.QtCore import QObject
from PyQt5.Qt import pyqtSignal
from serial import Serial
from minimalmodbus import Instrument

class Bearing_Serial(QObject):
    Warning_Signal = pyqtSignal(str)

    def __init__(self, com, baudrate, serialtype):
        super(Bearing_Serial, self).__init__()
        self._port = com
        self._baudrate = baudrate
        self._serialtype = serialtype

    def set_setting(self, com, baudrate, serialtype):
        self._port = com
        self._baudrate = baudrate
        self._serialtype = serialtype

    def open_serial(self):
        if (self._serialtype == 'serial'):
            try:
                self._serial = Serial()
                self._serial.port = self._port
                self._serial.baudrate = self._baudrate
                self._serial.open()
                self.Warning_Signal.emit('打开串口成功')
                return 1
            except:
                self.Warning_Signal.emit('打开串口失败')
                return 0
        elif(self._serialtype == 'modbus'):
            try:
                self._serial = Instrument(self._port, 1)
                self._serial.serial.baudrate = self._baudrate
                self.Warning_Signal.emit('打开串口成功')
                return 1
            except:
                self.Warning_Signal.emit('打开串口失败')
                return 0

    def read_data(self, n=0):
        if (self._serialtype == 'serial'):
            try:
                if n > 0:
                    return self._serial.read(n)
                else:
                    self._serial.reset_input_buffer()
                    data = self._serial.readline()
                    return data
            except:
                self.Warning_Signal.emit('读取数据失败，请检查串口！')
        elif (self._serialtype == 'modbus'):
            try:
                data = self._serial.read_registers(0, 8)
                return data
            except:
                self.Warning_Signal.emit('读取数据失败，请检查串口！')

    def send_data(self, data):
        if (self._serialtype == 'serial'):
            self._serial.write(data)

    def close(self):
        if (self._serialtype == 'serial'):
            try:
                self._serial.close()
            except IOError:
                self.Warning_Signal.emit('关闭串口失败')
        elif (self._serialtype == 'modbus'):
            pass


if __name__=='__main__':
    serial = Bearing_Serial('COM6', 19200, 'serial')
    serial.open_serial()
    serial.open_serial()
    serial.close()
