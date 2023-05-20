#define CODE_SUCSSES    0
#define CODE_ERROR      1

#define DATA_LEN        52

#define DATA_PIN        28  // B0 pin

#define CMD_RUN         82  // 'R'
#define CMD_REC_DATA    68  // 'D'
#define CMD_SET_TIME    84  // 'T'

int g_transmit_flag = 0;
char g_data [ DATA_LEN ];
int g_time = 50;

void setup() {
    Serial.begin(9600);
    while(!Serial){ 
      
    }
    pinMode(DATA_PIN, OUTPUT);
    Serial.println("HELLO WORLD");

}

void loop() {
    if( Serial.available() > 0 ){
        parse_command();
    }

    if ( g_transmit_flag ) {
        transmit();
    }

  
}


int parse_command() {
    char received_byte;
    received_byte = Serial.read();
    switch(received_byte) {
        case CMD_RUN:
            if ( cmd_run() ){
                return CODE_ERROR;
            }
            Serial.print("g_transmit_flag = ");
            Serial.print(g_transmit_flag, DEC);
            Serial.println(" ");
            break;

        case CMD_REC_DATA:
            if (cmd_rec_data() ) {
                return CODE_ERROR;
            }
            break;
        case CMD_SET_TIME:
            if (cmd_set_time() ) {
                return CODE_ERROR;
            }
        default:
            Serial.println("command not supported");
            break;
    }
    return CODE_SUCSSES;
}


int cmd_run() { 
    if ( g_transmit_flag ) {
        return CODE_ERROR;
    }
    g_transmit_flag = 1;
    return CODE_SUCSSES;
}


int cmd_rec_data() {
    int index = 0;
    char received_byte;
    Serial.write("Start receiving data\n");
    for( index = 0; index <= DATA_LEN-1; index = index + 1 ){
        while (!Serial.available()){}
        received_byte = Serial.read();
        g_data[index] = received_byte;

        Serial.print("Buffer[");
        Serial.print(index, DEC);
        Serial.print("] = ");
        Serial.print(received_byte, DEC);
        Serial.println(" ");
    }

}

int cmd_set_time() {
  int time = 0;
  char received_byte;
  for (int i = 0; i < 4; i = i + 1){
    while (!Serial.available()){}
    received_byte = Serial.read();
    time = time<<8;
    time += received_byte;
  }
  Serial.print("Set the time delay to: ");
  Serial.println(time, DEC);
  g_time = time;
}


int transmit() {
    Serial.write("transmit data begin\n");
    g_transmit_flag = 0;
    int cur_bit;
    int i;
    for(i = 0; i < DATA_LEN - 1; i = i + 1){ 
      Serial.print("|");
    
      cur_bit = get_bit_from_byte(g_data[i],0);
      
      Serial.print(cur_bit, DEC);
      digitalWrite(DATA_PIN, cur_bit);
      delay(g_time);
      Serial.print(cur_bit^1, DEC);  
      digitalWrite(DATA_PIN, cur_bit^1);
      delay(g_time);
    }
    digitalWrite(DATA_PIN, LOW);

    Serial.println(" Done");
}


int get_bit_from_byte(char in_byte, int offset) {

    return (in_byte>>offset) & 1;
}
