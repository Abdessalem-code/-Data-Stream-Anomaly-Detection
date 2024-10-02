import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from anomaly_detector import AnomalyDetectionSystem
from data_streamer import DataStreamer
from data_visualizer import DataVisualizer

def main():
    try:
        data_streamer = DataStreamer()
        data_generator = data_streamer.generate_data_point()
        anomaly_system = AnomalyDetectionSystem()
        visualizer = DataVisualizer()

        def update(frame):
            try:
                # Generate and process new data point
                data_point = next(data_generator)
                anomaly_system.process_data_point(data_point)
                anomalies = anomaly_system.get_anomalies()
                
                # Update visualization
                return visualizer.update_plot(data_point, anomalies)
            except StopIteration:
                print("Data stream ended.")
                plt.close()
            except Exception as e:
                print(f"Error in update function: {str(e)}")
                return visualizer.line, visualizer.anomaly_scatter

        # Set up the animation
        animation = FuncAnimation(
            visualizer.fig,
            update,
            interval=100,
            blit=False,
            save_count=100
        )

        plt.show()

    except KeyboardInterrupt:
        print("\nVisualization interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up resources
        plt.close('all')
        print("Visualization ended.")

if __name__ == "__main__":
    print("Starting the real-time data visualization...")
    main()
