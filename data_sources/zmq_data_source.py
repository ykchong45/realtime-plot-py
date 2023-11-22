import zmq
import stream_data_pb2 as stream_data

"""
This is a Protobuf over ZMQ data source. 
To use it you need a generated protobuf file for Python to use in the root level
"""

class ZMQDataSource:
    def __init__(self, endpoint=7000):
        self.endpoint = endpoint
        self.context = zmq.Context()
        self.socket = self.initialize_socket()

    def initialize_socket(self):
        socket = self.context.socket(zmq.SUB)
        socket.setsockopt(zmq.CONFLATE, 1)
        socket.connect('tcp://localhost:{}'.format(self.endpoint))
        socket.subscribe(b'')
        socket.RCVTIMEO = 1000
        return socket

    def get_data(self):
        data = self.socket.recv()
        message = stream_data.StreamData()
        message.ParseFromString(data)

        # edit the following line when using
        newDataTime = message.imu_data.recorded_time / 1000000
        data_point_y = message.imu_data.gyroscope.x  # edit this when using
        return newDataTime, data_point_y