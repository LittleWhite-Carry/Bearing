from Bearing.bearing_serial import Bearing_Serial
from PyQt5.Qt import QObject, QThread, pyqtSignal
import time

class Read_Thread(QObject):
    ReadComplete_Signal = pyqtSignal(object, object, object)
    SaveData_Signal = pyqtSignal()

    def __init__(self, serial1=Bearing_Serial('COM1', 9600, 'modbus'), serial2=Bearing_Serial('COM2', 9600, 'serial')):
        super(Read_Thread, self).__init__()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._serial1 = serial1
        self._serial2 = serial2
        self._stop = 0

    def set_serial(self, serial1, serial2):
        self._serial1 = serial1
        self._serial2 = serial2

    def stop_function(self):
        self._stop = 1

    def read_data(self, number):
        self._stop = 0
        if number == 0:
            while not self._stop:
                self.ReadComplete_Signal.emit(self._serial1.read_data(), self._serial2.read_data())
            self.SaveData_Signal.emit()
        elif number > 0:
            for i in range(number):
                if self._stop:
                    break
                data1 = self._serial1.read_data()
                data2 = self._serial2.read_data()
                data3 = time.time()
                self.ReadComplete_Signal.emit(data1, data2, data3)
            self.SaveData_Signal.emit()


