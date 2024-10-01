import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from anomaly_detector import AnomalyDetectionSystem
from data_streamer import DataStreamer
from data_visualizer import DataVisualizer

def main():
    data_streamer = DataStreamer()
    data_generator = data_streamer.generate_data_point()
    anomaly_system = AnomalyDetectionSystem()
    visualizer = DataVisualizer()

    def update(frame):
        data_point = next(data_generator)
        anomaly_system.process_data_point(data_point)
        anomalies = anomaly_system.get_anomalies()
        return visualizer.update_plot(data_point, anomalies)

    animation = FuncAnimation(
        visualizer.fig,
        update,
        interval=100,
        blit=False,
        save_count=100
    )
    plt.show()

if __name__ == "__main__":
    print("Starting the real-time data visualization...")
    main()
