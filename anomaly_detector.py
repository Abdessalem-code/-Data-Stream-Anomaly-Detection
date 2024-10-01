import numpy as np
from collections import deque
import threading
import queue

# Base class for anomaly detectors
class AnomalyDetector:
    def __init__(self, name, window_size=50):
        self.name = name
        self.window_size = window_size
        self.data_window = deque(maxlen=window_size)

    def update(self, data_point):
        self.data_window.append(data_point)
        return self.detect_anomaly()

    def detect_anomaly(self):
        # To be implemented by subclasses (concrete strategies)
        pass

# Z-Score based anomaly detector
class ZScoreDetector(AnomalyDetector):
    def __init__(self, threshold=3.0):
        super().__init__("Z-Score", window_size=50)
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

# Moving Average based anomaly detector
class MovingAverageDetector(AnomalyDetector):
    def __init__(self, threshold=2.0):
        super().__init__("Moving Average", window_size=20)
        self.threshold = threshold

    def detect_anomaly(self):
        if len(self.data_window) < self.window_size:
            return False
        values = [dp.value for dp in self.data_window]
        moving_avg = np.mean(values[:-1])
        return abs(self.data_window[-1].value - moving_avg) > self.threshold * np.std(values[:-1])

# Interquartile Range based anomaly detector
class IQRDetector(AnomalyDetector):
    def __init__(self, iqr_factor=1.5):
        super().__init__("IQR", window_size=50)
        self.iqr_factor = iqr_factor

    def detect_anomaly(self):
        if len(self.data_window) < self.window_size:
            return False
        values = [dp.value for dp in self.data_window]
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (self.iqr_factor * iqr)
        upper_bound = q3 + (self.iqr_factor * iqr)
        return self.data_window[-1].value < lower_bound or self.data_window[-1].value > upper_bound

# We will use threading for our anomaly detection system due to its efficiency in handling I/O-bound operations, even though we cannot achieve true parallelism with threading in the CPython implementation. This is particularly important because our application involves generating data in real-time and visualizing it, where the primary bottleneck is not CPU computation but rather waiting for data input and rendering the visual output.
class AnomalyDetectionWorker(threading.Thread):
    def __init__(self, detector, input_queue, output_queue):
        threading.Thread.__init__(self)
        self.detector = detector
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.daemon = True

    def run(self):
        while True:
            data_point = self.input_queue.get()
            if data_point is None:
                break
            is_anomaly = self.detector.update(data_point)
            self.output_queue.put((self.detector.name, is_anomaly))
            self.input_queue.task_done()

class AnomalyDetectionSystem:
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
        for input_queue in self.input_queues:
            input_queue.put(data_point)

        votes = 0
        for _ in range(len(self.detectors)):
            _, is_anomaly = self.output_queue.get()
            if is_anomaly:
                votes += 1
            self.output_queue.task_done()

        if votes > 0:
            self.anomalies.append(data_point)

    def get_anomalies(self):
        return self.anomalies.copy()