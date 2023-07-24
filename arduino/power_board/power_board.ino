int reboot = 0;
String cmd;
void setup(){
    Serial.begin(9600);
    Serial.setTimeout(1);
}

void loop() {

  cmd = Serial.readString();
  Serial.println(cmd);
/*
  switch (cmd){
    case 'heartbeat':
      reboot = 0;
      continue
    case '':
      if (reboot > 1800){
        Serial.println("Time out reached!")
        // toggle main processors power
      }
      reboot += 1;
  }
  */
  delay(1000);
}