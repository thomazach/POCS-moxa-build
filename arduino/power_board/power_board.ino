void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {
  readSerial();
}

void readSerial() {
  char currentChar;
  if (Serial.available()){
    currentChar = Serial.read()
    Serial.println(currentChar);
  }
  
}
