const byte maxChars = 32;
char recievedChars[maxChars];

bool cmd_recieved = false;


void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {
  recieveCommand();
  if (cmd_recieved == true) {
    Serial.println(recievedChars);
    cmd_recieved = false;
  }
}

void recieveCommand() {
  static bool inProgress = false;
  static byte i = 0;
  char startChar = '<';
  char endChar = '>';
  char incomingChar;

  while (Serial.available() && cmd_recieved == false) {
    incomingChar = Serial.read();
    Serial.println(incomingChar);


    if (incomingChar == startChar) {
      inProgress = true;
    }
    else if (inProgress == true) {
      if (incomingChar != endChar) {
        recievedChars[i] = incomingChar;
        i++;
        if (i >= maxChars) {
          i = maxChars - 1;
        }
      }
      else {
        recievedChars[i] = '\0';
        inProgress = false;
        i = 0;
        cmd_recieved = true;
      }
    }
  }

}