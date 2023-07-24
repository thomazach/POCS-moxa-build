void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {
  String test = Serial.readStringUntil("!");
  Serial.println(test);
  delay(2000);
}
