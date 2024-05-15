#define pot1 A0
#define pot2 A1
#define pot3 A2

float val;
String pos;

void setup() {
  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  Serial.begin(9600);

}

void loop() {
  //Prints the value of ADC
  for (int chan=0; chan<3; chan++) {
    if (chan == 0) {
      val = analogRead(pot1);
      pos = "c";
    }
    else if (chan == 1) {
      val = analogRead(pot2); 
      pos = "l";
    }
    else {
      val = analogRead(pot3);
      pos = "r";
    }
    if (val == 0.00) {
      val = 1;
    }
    val = 10 * log10(val);
    Serial.print("pot#");
    Serial.print(pos);
    Serial.print(": ");
    Serial.print(val);
    Serial.print(",\n");
  }
  
 
  delay(10);
}
