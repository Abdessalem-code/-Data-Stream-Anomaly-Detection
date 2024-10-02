from data_validation_error import DataValidationError

class DataPoint:
    """
    Represents a single data point in the data stream

    Attributes:
        time (int): The timestamp or sequence number of the data point.
        value (float): The actual data value generated.
    """
    def __init__(self, time, value):
        if not isinstance(time, (int, float)) or time < 0:
            raise DataValidationError(f"Invalid time value: {time}. Must be a non-negative number.")
        if not isinstance(value, (int, float)):
            raise DataValidationError(f"Invalid data value: {value}. Must be a number.")
        self.time = time
        self.value = value