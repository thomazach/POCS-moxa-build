const int maxChars = 10;
char command[maxChars];

void setup(){
  Serial.begin(9600);
  Serial.setTimeout(5);
  delay(2000);
  Serial.println("<Arduino is ready!>");
}

void loop() {
  readSerial();
  delay(100);
}

void readSerial() {
  char currentChar;
  bool recievingCmd = false;
  int i = 0;

  while (Serial.available() > 0){
    currentChar = Serial.read();
    if (currentChar == byte('<') && recievingCmd == false){
      recievingCmd = true;
    }
    else if (currentChar != byte('>') && recievingCmd == true && i < maxChars){
      command[i] = currentChar;
      i++;
    }
    else {
      command[i] = '\0';
      i = 0;
      recievingCmd = false;
      Serial.println(command);
      break
    }
  }

}
