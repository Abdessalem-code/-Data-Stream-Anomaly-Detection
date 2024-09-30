import matplotlib.pyplot as plt

class DataVisualizer:
    def __init__(self, max_points=100):
        self.max_points = max_points
        self.times = []
        self.data_points = []
        
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(-50, 50)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Data Value')
        self.ax.set_title('Real-time Data Visualization')
        self.ax.grid()

    def update_plot(self, _, data_streamer):
        # Generate the data point from the data streamer
        t, data_point = next(data_streamer)  # Get the next data point
        self.times.append(t)
        self.data_points.append(data_point)
        
        # Keep only the last max_points
        if len(self.times) > self.max_points:
            self.times.pop(0)
            self.data_points.pop(0)
        
        self.line.set_data(self.times, self.data_points)
        self.ax.set_xlim(max(0, t - self.max_points + 1), t + 1)
        
        return self.line,
