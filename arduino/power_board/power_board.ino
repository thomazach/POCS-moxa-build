
void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(10);
}

void loop() {
  readSerial();
  delay(100);
}

void readSerial() {
  int data[5];
  int i = 0;
  bool new_command = false;
  while (Serial.available() > 0){
    data[i] = Serial.readStringUntil(',').toInt();
    i += 1;
    new_command = true;
  }
  if (new_command == true){
    Serial.print(data[0]);
    Serial.print(", ");
    Serial.print(data[1]);
    Serial.print(", ");
    Serial.print(data[2]);
    Serial.print(", ");
    Serial.print(data[3]);
    Serial.print(", ");
    Serial.print(data[4]);
    Serial.println("");
    new_command = false;
  }

}
