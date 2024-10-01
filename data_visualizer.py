import matplotlib.pyplot as plt
from collections import deque

class DataVisualizer:
    def __init__(self, max_points=200):
        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=2, label='Data Stream')
        self.anomaly_scatter, = self.ax.plot([], [], 'ro', label='Anomalies')
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Data Value')
        self.ax.set_title('Real-time Data Visualization with Anomaly Detection')
        self.ax.grid()
        self.ax.legend()

    def update_plot(self, data_point, anomalies):
        self.data_points.append(data_point)
        
        times = [dp.time for dp in self.data_points]
        values = [dp.value for dp in self.data_points]
        self.line.set_data(times, values)
        
        anomaly_times = [a.time for a in anomalies if a.time >= times[0]]
        anomaly_values = [a.value for a in anomalies if a.time >= times[0]]
        self.anomaly_scatter.set_data(anomaly_times, anomaly_values)
        
        self.ax.set_xlim(max(0, data_point.time - self.max_points + 1), data_point.time + 1)
        
        return self.line, self.anomaly_scatter
