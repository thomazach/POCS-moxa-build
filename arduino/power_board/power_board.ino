int reboot = 0;
int cmd;
void setup(){
    Serial.begin(9600);
    Serial.setTimeout(5);
    delay(2000);
}

void loop() {

  while (Serial.available() > 0){
    cmd = Serial.readStringUntil(',').toInt();
  }
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
  delay(100);
}