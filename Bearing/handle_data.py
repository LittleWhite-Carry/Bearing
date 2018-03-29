from PyQt5.Qt import QObject, QThread, pyqtSignal
from Bearing.all_data import AllData


class Handle_Data(QObject):
    HandleComplete_Signal = pyqtSignal(object, object, object)
    TranData_Signal = pyqtSignal(object)

    def __init__(self):
        super(Handle_Data, self).__init__()
        self._all_data = AllData()
        self._thread = QThread()
        self.moveToThread(self._thread)

    def save_all_data(self):
        self.TranData_Signal.emit(self._all_data)

    def clear_all_data(self):
        self._all_data.init_all()

    def invert(self, a):
        if a == '0':
            return '1'
        return '0'

    def handle(self, data1, data2, data3):
        # 此处data1是modbus的数据，data2是电阻的数据
        f = self.handle_modbus(data1)
        R = self.handle_resistance(data2)
        self._all_data.resistance.append(R)
        self._all_data.force_original.append(f[0])
        self._all_data.force_stress.append((float(f[0])) / 0.0508 / 0.0028274 / 1000)
        self._all_data.force_switch.append((float(f[0])) / 0.0508)
        self._all_data.displacement.append(float(f[1]) * 0.8)
        self._all_data.time.append(data3)
        self.HandleComplete_Signal.emit((float(f[0]) / 0.0508), R, (float(f[1]) * 0.8))

    def handle_modbus(self, data):
        # 对modbus的数据处理方式还待改善，涉及到一个invert()函数
        a = list(map(lambda x: hex(x), data))
        f1 = []
        for (i, j) in zip(a[::2], a[1::2]):
            if len(i) >= 4:
                if eval(i) > 32767:
                    c = hex((eval('0x' + i[-2:])) * (16 ** 4) + eval(j))
                    f1.append(
                        ~(eval(
                            "0b" + "".join(list(map(lambda x: self.invert(x), bin(eval(c))[2:])))) + 1) * 10 * 1.3 / (
                                2 ** 23))
                else:
                    f1.append((eval('0x' + i[-2:]) * (16 ** 4) + eval(j)) * 10 * 1.3 / (2 ** 23))
            elif len(i) >= 3:
                f1.append((eval('0x' + i[-1:]) * (16 ** 4) + eval(j)) * 10 * 1.3 / (2 ** 23))
        f = [f1[0] - f1[1], f1[3] - f1[2]]
        return f

    def handle_resistance(self, data):
        # 这里需不需要try还有待考证，此处为王师兄所写，感觉次次都是except
        try:
            R = float(data.decode()[1:].split(' ')[0])
        except:
            R = data.decode()[1:].split(' ')[0]
            R = float(R)
        return R

if __name__ == '__main__':
    handle = Handle_Data()
    handle.handle('','')
