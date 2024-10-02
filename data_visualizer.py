import matplotlib.pyplot as plt
from collections import deque

from data_validation_error import DataValidationError

class DataVisualizer:
    """
    Visualizes the data stream and detected anomalies in real-time using Matplotlib

    Attributes:
        max_points (int): The maximum number of points to display on the plot
        data_points (deque): A deque to store the most recent data points for visualization
        fig (Figure): The Matplotlib figure for plotting
        ax (Axes): The axes on which the data stream and anomalies are plotted
        line (Line2D): The line object representing the data stream
        anomaly_scatter (Line2D): The scatter plot for anomalies
    """
    def __init__(self, max_points=200):
        if not isinstance(max_points, int) or max_points <= 0:
            raise ValueError("max_points must be a positive integer")

        self.max_points = max_points
        self.data_points = deque(maxlen=max_points)
        
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=2, label='Data Stream')
        self.anomaly_scatter, = self.ax.plot([], [], 'ro', label='Anomalies')
        
        self.setup_plot()

    def setup_plot(self):
        """Set up the initial plot layout and labels"""
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Data Value')
        self.ax.set_title('Real-time Data Visualization with Anomaly Detection')
        self.ax.grid()
        self.ax.legend()

    def update_plot(self, data_point, anomalies):
        """
        Update the plot with new data point and anomalies
        
        :param data_point: The latest data point to add to the plot
        :param anomalies: List of anomaly points to display
        :return: Updated line and scatter
        """
        try:
            if not hasattr(data_point, 'time') or not hasattr(data_point, 'value'):
                raise DataValidationError(f"Invalid data point: {data_point}")
            
            self.data_points.append(data_point)
            
            # Update main data line
            times = [dp.time for dp in self.data_points]
            values = [dp.value for dp in self.data_points]
            self.line.set_data(times, values)
            
            # Update anomaly scatter plot
            anomaly_times = [a.time for a in anomalies if a.time >= times[0]]
            anomaly_values = [a.value for a in anomalies if a.time >= times[0]]
            self.anomaly_scatter.set_data(anomaly_times, anomaly_values)
            
            self.ax.set_xlim(max(0, data_point.time - self.max_points + 1), data_point.time + 1)
            
            return self.line, self.anomaly_scatter
        
        except Exception as e:
            print(f"Error updating plot: {str(e)}")
            return self.line, self.anomaly_scatter