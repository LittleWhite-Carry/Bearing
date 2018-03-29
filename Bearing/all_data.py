from PyQt5.QtCore import QObject
class AllData(QObject):

    def __init__(self):
        super(AllData, self).__init__()
        self.force_original = []    # 电压
        self.force_switch = []      # 直接转换的原力
        self.force_stress = []      # 应力
        self.resistance = []        # 电阻
        self.displacement = []      # 位移
        self.time = []  # 时间

    def init_all(self):
        self.force_original = []    # 电压
        self.force_switch = []      # 直接转换的原力
        self.force_stress = []      # 应力
        self.resistance = []        # 电阻
        self.displacement = []      # 位移
        self.time = []              # 时间
