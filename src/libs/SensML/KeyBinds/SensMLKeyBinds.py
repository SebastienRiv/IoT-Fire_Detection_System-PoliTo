class SensMLKeyBinds:
    
    def __init__(self, sensMLToRead) -> None:
        self.sensMLToRead = sensMLToRead
        
    def updateSensMLReading(self, newSensMLReading: dict) -> None:
        self.sensMLToRead = newSensMLReading
    
    @property
    def device_bn(self):
        return self.sensMLToRead.get("bn", None)
    
    @property
    def device_e(self):
        return self.sensMLToRead.get("e", None)
    
    @property
    def device_t(self):
        return self.sensMLToRead.get("t", None)
    
    @property
    def sensor_n(self):
        return self.sensMLToRead.get("n", None)
    
    @property
    def sensor_u(self):
        return self.sensMLToRead.get("u", None)
    
    @property
    def sensor_v(self):
        return self.sensMLToRead.get("v", None)
    
    @property
    def sensor_t(self):
        return self.sensMLToRead.get("t", None)
    
    @property
    def actuator_a(self):
        return self.sensMLToRead.get("a", None)
    
    @property
    def actuator_n(self):
        return self.sensMLToRead.get("n", None)
    
    @property
    def actuator_u(self):
        return self.sensMLToRead.get("u", None)
    
    @property
    def actuator_v(self):
        return self.sensMLToRead.get("v", None)
    
    @property
    def actuator_t(self):
        return self.sensMLToRead.get("t", None)