import numpy as np
import random

class DataStreamer:
    def __init__(self, noise_level=2, anomaly_chance=0.01, amplitude=10, anomaly_magnitude=30):
        self.noise_level = noise_level
        self.anomaly_chance = anomaly_chance
        self.amplitude = amplitude
        self.anomaly_magnitude = anomaly_magnitude
        self.t = 0

    def generate_data_point(self):
        """
        Generate a single data point based on the current time step.
        """
        while True:
            seasonal = self.amplitude * np.sin(0.1 * self.t)
            noise = random.gauss(0, self.noise_level)
            
            if random.random() < self.anomaly_chance:
                anomaly = random.choice([self.anomaly_magnitude, -self.anomaly_magnitude])
                data_point = seasonal + noise + anomaly
            else:
                data_point = seasonal + noise
            
            yield self.t, data_point
            self.t += 1