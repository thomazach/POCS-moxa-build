
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