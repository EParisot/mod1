from direct.showbase import DirectObject
import numpy as np

class Events_Handler(DirectObject.DirectObject):
    def __init__(self, base):
        self.base = base
        self.rain = False
        self.wave = False
        self.accept("f", self.handle_flood)
        self.accept("r", self.handle_rain)
        self.accept("w", self.handle_wave)

    def handle_flood(self):
        if self.base.flooding == True:
            self.base.taskMgr.remove("flood")
            self.base.flush = not self.base.flush
        elif self.wave == False and self.rain == False:
            self.base.taskMgr.removeTasksMatching("flood")
            self.base.taskMgr.add(self.base.flood, "flood")
        self.base.flooding = not self.base.flooding

    def handle_rain(self):
        if self.rain == True:
            self.base.raining = False
        elif self.base.flooding == False and self.wave == False:
            self.base.raining = True
            self.base.flush = False
            self.base.taskMgr.removeTasksMatching("rain")
            self.base.taskMgr.add(self.base.rain, "rain")
        self.rain = not self.rain

    def handle_wave(self):
        if self.wave == True:
            self.base.taskMgr.remove("wave")
        elif self.rain == False and self.base.flooding == False:
            # Initial condition for wave.
            for i in range(10):
                # Wave start
                self.base.wz[:, i:i+1] = (40 + self.base.H) * np.cos((i+1)/10)
            self.base.taskMgr.removeTasksMatching("wave")
            self.base.taskMgr.add(self.base.wave, "wave")
        self.wave = not self.wave