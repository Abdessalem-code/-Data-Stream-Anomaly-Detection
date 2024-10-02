import numpy as np
import random

from data_point import DataPoint

class DataStreamer:
    """
    Simulates a real-time data stream by generating data points with noise, seasonality, and anomalies

    Attributes:
        noise_level (float): The standard deviation of the noise to be added to the data
        anomaly_chance (float): The probability of generating an anomaly at any time step
        amplitude (float): The amplitude of the seasonal component
        anomaly_magnitude (float): The magnitude of anomalies
        t (int): The current time step of the data stream
    """
    def __init__(self, noise_level=2, anomaly_chance=0.1, amplitude=5, anomaly_magnitude=25):
        # Validate input parameters
        if not all(isinstance(x, (int, float)) and x > 0 for x in [noise_level, amplitude, anomaly_magnitude]):
            raise ValueError("noise_level, amplitude, and anomaly_magnitude must be positive numbers")
        if not 0 <= anomaly_chance <= 1:
            raise ValueError("anomaly_chance must be between 0 and 1")

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
            try:
                # Generate seasonal component
                seasonal = self.amplitude * np.sin(0.1 * self.t)
                
                noise = random.gauss(0, self.noise_level)
                
                # Introduce anomaly with specified probability
                if random.random() < self.anomaly_chance and self.t > 30:
                    anomaly = random.choice([self.anomaly_magnitude, -self.anomaly_magnitude])
                    data_point = seasonal + noise + anomaly
                else:
                    data_point = seasonal + noise
                
                yield DataPoint(self.t, data_point)
                
                self.t += 1
            except Exception as e:
                print(f"Error generating data point at time {self.t}: {str(e)}")
                self.t += 1