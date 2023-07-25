
String message = "Motor 1 off";

void setup(){
  Serial.begin(9600);
  Serial.setTimeout(5);
  delay(2000);
}

void loop() {
  readSerial();
  Serial.println(message);
  delay(100);
}

void readSerial() {
  char currentChar;
  while (Serial.available() > 0){
    currentChar = Serial.read();
    if (currentChar == byte('<')){
      message = "Motor 1 on";
    }
  }
}
