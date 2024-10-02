import numpy as np
from collections import deque
import threading
import queue

from data_validation_error import DataValidationError

class AnomalyDetector:
    """
    Base class for all anomaly detectors

    Attributes:
        name (str): The name of the anomaly detection method
        window_size (int): The size of the data window used for anomaly detection
        data_window (deque): A deque storing recent data points for anomaly detection
    """
    def __init__(self, name, window_size=50):
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be a non-empty string")
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError("Window size must be a positive integer")
        
        self.name = name
        self.window_size = window_size
        self.data_window = deque(maxlen=window_size)

    def update(self, data_point):
        if not hasattr(data_point, 'value') or not isinstance(data_point.value, (int, float)):
            raise DataValidationError(f"Invalid data point: {data_point}")
        
        self.data_window.append(data_point)
        return self.detect_anomaly()

    def detect_anomaly(self):
        # To be implemented by subclasses (concrete strategies)
        raise NotImplementedError("Subclasses must implement detect_anomaly method")

class ZScoreDetector(AnomalyDetector):
    """
    Detects anomalies using the Z-Score method

    Attributes:
        threshold (float): The Z-Score threshold for classifying a data point as an anomaly
    """
    def __init__(self, threshold=2.0):
        super().__init__("Z-Score", window_size=30)
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError("Threshold must be a positive number")
        self.threshold = threshold

    def detect_anomaly(self):
        if len(self.data_window) < self.window_size:
            return False
        values = [dp.value for dp in self.data_window]
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return False
        z_score = abs((self.data_window[-1].value - mean) / std)
        return z_score > self.threshold

class MovingAverageDetector(AnomalyDetector):
    """
    Detects anomalies using the Moving Average method

    Attributes:
        threshold (float): The Moving Average threshold for classifying a data point as an anomaly
    """
    def __init__(self, threshold=1.5):
        super().__init__("Moving Average", window_size=15)
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError("Threshold must be a positive number")
        self.threshold = threshold

    def detect_anomaly(self):
        if len(self.data_window) < self.window_size:
            return False
        values = [dp.value for dp in self.data_window]
        moving_avg = np.mean(values[:-1])
        return abs(self.data_window[-1].value - moving_avg) > self.threshold * np.std(values[:-1])

class IQRDetector(AnomalyDetector):
    """
    Detects anomalies using the Interquartile Range (IQR) method

    Attributes:
        iqr_factor (float): The factor by which the IQR is multiplied to define anomaly thresholds
    """
    def __init__(self, iqr_factor=1.5):
        super().__init__("IQR", window_size=30)
        if not isinstance(iqr_factor, (int, float)) or iqr_factor <= 0:
            raise ValueError("IQR factor must be a positive number")
        self.iqr_factor = iqr_factor

    def detect_anomaly(self):
        if len(self.data_window) < self.window_size:
            return False
        values = [dp.value for dp in self.data_window]
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        if iqr == 0:
            return False
        lower_bound = q1 - (self.iqr_factor * iqr)
        upper_bound = q3 + (self.iqr_factor * iqr)
        return self.data_window[-1].value < lower_bound or self.data_window[-1].value > upper_bound

# We will use threading for our anomaly detection system due to its efficiency in handling I/O-bound operations, even though we cannot achieve true parallelism with threading in the CPython implementation. This is particularly important because our application involves generating data in real-time and visualizing it, where the primary bottleneck is not CPU computation but rather waiting for data input and rendering the visual output.
class AnomalyDetectionWorker(threading.Thread):
    """
    A worker thread that processes data points using a specific anomaly detection algorithm

    Each worker fetches data from an input queue, applies the assigned anomaly detection 
    method, and stores the result (whether an anomaly was detected) in the output queue

    Attributes:
        detector (AnomalyDetector): The anomaly detection method used by this worker
        input_queue (queue.Queue): The queue from which the worker fetches data points
        output_queue (queue.Queue): The queue where the worker stores anomaly detection results
    """
    def __init__(self, detector, input_queue, output_queue):
        threading.Thread.__init__(self)
        self.detector = detector
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.daemon = True

    def run(self):
        while True:
            try:
                # Use a timeout to prevent indefinite blocking
                data_point = self.input_queue.get(timeout=1)
                if data_point is None:
                    break
                is_anomaly = self.detector.update(data_point)
                self.output_queue.put((self.detector.name, is_anomaly))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in {self.detector.name}: {str(e)}")
            finally:
                self.input_queue.task_done()

class AnomalyDetectionSystem:
    """
    A system for managing and coordinating multiple anomaly detection methods

    This system distributes data points across multiple detection algorithms, gathers results,
    and identifies anomalies with a vote based logic

    Attributes:
        detectors (list): A list of anomaly detectors to be used
        input_queues (list): A list of input queues for each anomaly detection worker
        output_queue (queue.Queue): A queue where workers send detection results
        workers (list): A list of worker threads responsible for anomaly detection
        anomalies (list): A list to store detected anomalies
    """
    def __init__(self):
        self.detectors = [
            ZScoreDetector(),
            MovingAverageDetector(),
            IQRDetector(),
        ]
        self.input_queues = [queue.Queue() for _ in self.detectors]
        self.output_queue = queue.Queue()
        self.workers = [AnomalyDetectionWorker(d, iq, self.output_queue) 
                        for d, iq in zip(self.detectors, self.input_queues)]
        self.anomalies = []

        for worker in self.workers:
            worker.start()

    def process_data_point(self, data_point):
        if not hasattr(data_point, 'value') or not isinstance(data_point.value, (int, float)):
            raise DataValidationError(f"Invalid data point: {data_point}")

        for input_queue in self.input_queues:
            input_queue.put(data_point)

        votes = 0
        for _ in range(len(self.detectors)):
            try:
                _, is_anomaly = self.output_queue.get(timeout=1)
                if is_anomaly:
                    votes += 1
            except queue.Empty:
                print("Timeout waiting for detector result")
            finally:
                self.output_queue.task_done()

        if votes >= 2:
            self.anomalies.append(data_point)

    def get_anomalies(self):
        return self.anomalies.copy()