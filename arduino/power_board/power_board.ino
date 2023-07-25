const int maxChars = 32;
char data[maxChars];

void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(10);
}

void loop() {
  readSerial();
  if (sizeof(data) != 0) {
    char buffer[sizeof(data)];
    sprintf(data, "%s", data);
    Serial.println(data);
  }
  Serial.println("main loop complete");

}

void readSerial() {
  Serial.println("in readSerial");
  int currentChar;
  int i = 0;
  bool recievingSerial = false;

  while (Serial.available()){
    Serial.println("In read while loop");
    currentChar = Serial.read();

    if (currentChar == byte('<') && recievingSerial == false) {
      recievingSerial = true;
    }
    else if (currentChar != byte('>') && i <= maxChars && recievingSerial == true) {
      data[i] = currentChar;
      i++;
    }
    else {
      i = 0;
      recievingSerial = false;
    }
  }
  
}
