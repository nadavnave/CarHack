from time import sleep
from serial import Serial

CMD_RUN         = b'R'
CMD_REC_DATA    = b'D'
CMD_SET_TIME    = b'T'

class CarHacker:
    def __init__(self, comport: str) -> None:
        self.s = Serial(comport)

    def nice_print(self, line):
        print(line.decode('utf-8'))

    def nice_read_all(self):
        print(self.s.read_all().decode('utf-8'))

    def nice_readline(self):
        line = self.s.readline()
        self.nice_print(line)

    def write_data(self, data: list):
        self.nice_read_all()
        self.s.write(CMD_REC_DATA)
        self.nice_readline()
        for bit in data:
            self.s.write(bit.to_bytes(1,'little'))
            self.nice_readline()

    def set_time(self, time: int):
        self.s.write(CMD_SET_TIME)
        self.s.write(time.to_bytes(4,'big'))
        line = self.s.readline()
        self.nice_print(line)

    def run(self):
        self.nice_read_all()
        self.s.write(CMD_RUN)
        self.nice_readline() # transmit flag change
        self.nice_readline() # start transmitting
        self.nice_readline() # wait for done
        
    