int maxChars = 32;
char data[32];

void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {
  readSerial();
  if (sizeof(data) != 0) {
    for (int i = 0; i <= sizeof(data); i++){
      Serial.print(data[i]);
    }
    Serial.println("");
  }


}

void readSerial() {
  int currentChar;
  int i = 0;
  bool recievingSerial = false;

  while (Serial.available()){
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
