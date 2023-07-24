void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {
  Serial.println("Test message!");
  delay(5000);
}
