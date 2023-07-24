<<<<<<< HEAD
// Power distribution board manual: https://www.infineon.com/dgdl/Infineon-24V_ProtectedSwitchShield_with_Profet+24V_for_Arduino_UsersManual_10.pdf-UserManual-v01_01-EN.pdf?fileId=5546d46255dd933d0156074933e91fe2
// Wilfred's variables for pin assignments, based off/copied from https://github.com/panoptes/POCS/blob/develop/resources/arduino/PowerBoard/PowerBoard.ino as of 7/25/2023

// Meanwell UPS AC and Battery pins
const int AC_OK = 11;
const int BAT_LOW = 12;

// Relay pin assignments                           // Connected component based off of https://www.youtube.com/watch?v=Uq_ytlCmLIw&t=221s 
const int RELAY_0 = A3; // 0_0 PROFET-0 Channel 0 (A3 = 17) ---> Weather sensor
const int RELAY_1 = 3;  // 1_0 PROFET-0 Channel 1           ---> Unassigned
const int RELAY_2 = 4;  // 0_1 PROFET-1 Channel 0           ---> Fan
const int RELAY_3 = 7;  // 1_1 PROFET-1 Channel 1           ---> Cameras
const int RELAY_4 = 8;  // 0_2 PROFET-2 Channel 0           ---> Mount

// Current Sense
const int I_SENSE_0 = A0; // (PROFET-0 A0 = 14)
const int I_SENSE_1 = A1; // (PROFET-1 A1 = 15)
const int I_SENSE_2 = A2; // (PROFET-2 A2 = 16)

// Channel select
const int DSEL_0 = 2; // PROFET-0
const int DSEL_1 = 6; // PROFET-1

// Enable Sensing
const int DEN_0 = A4; // PROFET-0 (A4 = 18)
const int DEN_1 = 5;  // PROFET-1
const int DEN_2 = 9;  // PROFET-2

const int relayArray[] = {RELAY_0, RELAY_1, RELAY_2, RELAY_3, RELAY_4};

// Serial communication variables
const int maxChars = 10;
char command[maxChars];
bool haveNewCmd = false;

void setup(){
  Serial.begin(9600);
  Serial.setTimeout(5);

  // Set modes for pins
  pinMode(AC_OK, INPUT_PULLUP);
  pinMode(BAT_LOW, INPUT_PULLUP);

  pinMode(RELAY_0, OUTPUT);
  pinMode(RELAY_1, OUTPUT);
  pinMode(RELAY_2, OUTPUT);
  pinMode(RELAY_3, OUTPUT);
  pinMode(RELAY_4, OUTPUT);

  pinMode(I_SENSE_0, INPUT);  // I think this isn't necessary, default behavior is already INPUT, but these are also analog pins
  pinMode(I_SENSE_1, INPUT);  // going to leave it as is since I don't have access to hardware and don't want to fry anything
  pinMode(I_SENSE_2, INPUT);

  pinMode(DEN_0, OUTPUT);
  pinMode(DEN_1, OUTPUT);
  pinMode(DEN_2, OUTPUT);

  // Write values to pins
  // Need to do this to read current of each relay
  digitalWrite(DEN_0, HIGH);
  digitalWrite(DEN_1, HIGH);
  digitalWrite(DEN_2, HIGH);

  // Jank and obfuscated, do not let into production.
  // Should be initialized with pinMode, doing it this way makes 
  // the microcontroller choose the pinMode based off of default behavior.
  // Currently, I think digitalWrite is assigning these to pinMode(DSEL_X, INPUT_PULLUP).
  // For now just pray that arduino doesn't change digitalWrite() default behavior. 
  // When someone can physically observe the system or test on a seperate arduino or disconnect
  // cabling testing with a voltometer should be done with explicit pinMODE(DSEL_X, INPUT_PULLUP)
  digitalWrite(DSEL_0, LOW);  
  digitalWrite(DSEL_1, LOW);

  // Not exactly what I would've wanted to do, but am limited by hardware.
  // The arduino runs setup when a new serial connection is opened (at least by python). If a user turns off certain relays and restarts
  // moxa-pocs, when moxa-pocs tries to communicate with the arduino it will write the pins to high again. Trade off is that this way if 
  // power goes out and then comes back on, arduino will automatically turn on all of the components.
  digitalWrite(RELAY_0, HIGH);
  digitalWrite(RELAY_1, HIGH);
  digitalWrite(RELAY_2, HIGH);
  digitalWrite(RELAY_3, HIGH);
  digitalWrite(RELAY_4, HIGH);
  Serial.println("|r|");
}

void loop() {
  if (haveNewCmd == false){
    readSerial();
  }
  else if (haveNewCmd == true){
    execute_command();
    haveNewCmd = false;
  }
  delay(100);
}

void readSerial() {
  char currentChar;
  bool recievingCmd = false;
  int i = 0;

  while (Serial.available() > 0){
    currentChar = Serial.read();
    if (currentChar == byte('<') && recievingCmd == false){
      recievingCmd = true;
    }
    else if (currentChar != byte('>') && recievingCmd == true && i < maxChars){
      command[i] = currentChar;
      i++;
    }
    else {
      command[i] = '\0';
      i = 0;
      recievingCmd = false;
      haveNewCmd = true;
      break;
    }
  }
}

void execute_command(){
  char baseCmd[maxChars] = {0};
  char * strIdx;
  strIdx = strtok(command,",");
  strcpy(baseCmd, strIdx);
  int switchCmd = atoi(baseCmd);
  strIdx = strtok(NULL, ",");

  int relayIdx;

  if (switchCmd == 0){
    relayIdx = atoi(strIdx);
    turnRelayOff(relayIdx);
  }
  else if (switchCmd == 1){
    relayIdx = atoi(strIdx);
    turnRelayOn(relayIdx);
  }
  else if (switchCmd == 2){
    sendCurrentData();
  }
}

// Command functions
void turnRelayOn(int relayIndex){
  digitalWrite(relayArray[relayIndex], HIGH);
  Serial.println("|#|");
}

void turnRelayOff(int relayIndex){
  digitalWrite(relayArray[relayIndex], LOW);
  Serial.println("|#|");
}

void sendCurrentData(){
  // Read current in each channel on each device and print the currents in the same order as the relayArray
  int current_readings[5];

  digitalWrite(DSEL_0, LOW);
  digitalWrite(DSEL_1, LOW);
  delay(500);

  current_readings[0] = analogRead(I_SENSE_0); // 0_0 Weather sensor
  current_readings[2] = analogRead(I_SENSE_1); // 0_1 Fan
  current_readings[4] = analogRead(I_SENSE_2); // 0_2 Mount

  digitalWrite(DSEL_0, HIGH);
  digitalWrite(DSEL_1, HIGH);
  delay(500);

  current_readings[1] = analogRead(I_SENSE_0); // 1_0 Unassigned
  current_readings[3] = analogRead(I_SENSE_1); // 1_1 Cameras

  Serial.print("|");
  for (int i = 0; i <= 4; i++){
    Serial.print(current_readings[i]);
    Serial.print(",");
  }
  Serial.print("|");
  Serial.println();

}
=======
int reboot = 0;
String cmd;
void setup(){
    Serial.begin(9600);
    Serial.setTimeout(1);
}

void loop() {

  cmd = Serial.readString();
  Serial.print(cmd);
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
>>>>>>> 073a191 (Initial arduino infrastructure, going to test on dev unit)
