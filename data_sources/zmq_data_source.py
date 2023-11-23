import zmq
import stream_data_pb2 as stream_data

"""
This is a Protobuf over ZMQ data source. 
To use it you need a generated protobuf file for Python to use in the root level

An example to instantiate a ZMQDataSource:
d = ZMQDataSource(["fused_pose", "timestamp"], ["fused_pose", "angular_velocity", "x"], 8799)
"""

class ZMQDataSource:
    def __init__(self, x_field_names, y_field_names, endpoint=7000):
        self.endpoint = endpoint
        self.context = zmq.Context()
        self.socket = self.initialize_socket()
        self.x_field_names = x_field_names
        self.y_field_names = y_field_names

    def initialize_socket(self):
        socket = self.context.socket(zmq.SUB)
        socket.setsockopt(zmq.CONFLATE, 1)
        socket.connect('tcp://localhost:{}'.format(self.endpoint))
        socket.subscribe(b'')
        socket.RCVTIMEO = 1000
        return socket
    
    @staticmethod
    def get_nested_field(message, field_names):
        current_field = message
        for field_name in field_names:
            current_field = getattr(current_field, field_name)
        return current_field

    def get_data(self):
        data = self.socket.recv()
        message = stream_data.StreamData()
        message.ParseFromString(data)

        data_point_x = ZMQDataSource.get_nested_field(message, self.x_field_names)
        data_point_y = ZMQDataSource.get_nested_field(message, self.y_field_names)
        return [data_point_x, data_point_y]