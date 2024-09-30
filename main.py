import numpy as np
import random

def generate_data_point(t : int) -> float:
    
    seasonal = 10 * np.sin(0.1 * t)
    
    noise = random.gauss(0, 2)
    
    if random.random() < 0.1:
        anomaly = random.choice([30, -30])
        return seasonal + noise + anomaly
    
    return seasonal + noise

if __name__ == "__main__":
    for t in range(100):
        print(generate_data_point(t))