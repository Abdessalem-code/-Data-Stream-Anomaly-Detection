import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from data_streamer import DataStreamer
from data_visualizer import DataVisualizer

def main():
    visualizer = DataVisualizer()
    data_streamer = DataStreamer()
    data_generator = data_streamer.generate_data_point()
    
    # Using FuncAnimation to update the plot
    animation = FuncAnimation(
        visualizer.fig,
        visualizer.update_plot,
        fargs=(data_generator,),
        interval=100,
        blit=True,
        save_count=100
    )
    plt.show()

if __name__ == "__main__":
    print("Starting the real-time data visualization...")
    main()
