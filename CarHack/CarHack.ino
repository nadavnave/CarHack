#define CODE_SUCSSES    0
#define CODE_ERROR      1

#define DATA_LEN        30

#define CMD_RUN         0
#define CMD_REC_DATA    1

int g_transmit_flag = 0;
char g_data [ DATA_LEN ];

void setup() {
    Serial.begin(9600);
    while(!Serial){ 
      
    }
    
    Serial.println("HELLO WORLD");

}

void loop() {
    if( Serial.available() > 0 ){
        parse_command();
    }

    if ( g_transmit_flag ) {
        send_data();
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
    for( index = 0; index <= DATA_LEN-1; index++ ){
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


int send_data() {
    Serial.write("transmit data begin\n");
    g_transmit_flag = 0;
    int cur_bit;
    for(int i = 0; i < DATA_LEN; i++){ 
      cur_bit = get_bit_from_byte(g_data[i],0);
      Serial.println(cur_bit, DEC);
      
      Serial.println(cur_bit^1, DEC);  
    }

}


int get_bit_from_byte(char in_byte, int offset) {

    return (in_byte>>offset) & 1;
}
