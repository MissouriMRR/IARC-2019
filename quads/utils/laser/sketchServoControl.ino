/*
 * This sketch sets up the servo and Serial Connections and updates
 * the servo based on the input of the Serial Connection
 */
#include <Servo.h> //include teh Servo header for easier servo control

Servo myservo;//creates the servo object

int pos = 0;//used for changing the angle of the motor
int currentPos = 0; //used to keep track of where the motor is currently
int usrInt = 0;//used to keep track of the number the user inputted
const int servoLimit = 180;
const int pinNum = 12;
const int baudrateNum = 9600;
const int msDelay = 10;

void setup() { //this runs only once when it starts
  Serial.begin(baudrateNum);//start the serial connection at baudrateNum baudrate
  myservo.attach(pinNum);//attach the servo to the pin pinNum
  myservo.write(0); //Resets the servo to 0 degrees

}

void loop() { //loops forever (with power after setup)
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)//if there is a new command in the Serial
  {
    usrInt = Serial.parseInt();//take the information given as an int and set userInt equal to it
    Serial.parseInt(); //take it again to clear the Serial but do nothing with it
    delay(10); //wait 10 ms
  }


  if(usrInt >servoLimit)//if over servoLimit mod the input by servoLimit to make it in range
  {
    usrInt = usrInt%servoLimit;
  }
  else if(usrInt < 0)//else if under servoLimit mod the absolute value of the input by servoLimit to get it in range
  {
    usrInt = abs(usrInt)%servoLimit;
  }
  Serial.println(usrInt); //print the number the user inputted back to the user

  if(usrInt > currentPos)//if the input is bigger than the current angle
  {
    for(pos = currentPos; pos <= usrInt; pos += 1) {//starting at the currentPos number, as long as the pos (counter) is less than the input,
      myservo.write(pos);                           //write the servo to 1 more degrees than before until it reaches the input
      delay(msDelay);//wait msDelay ms
      currentPos += 1; //increment the currentPos counter
    }
  }

  if(usrInt < currentPos)//if the input is smaller than the current angle
  {
    for(pos = currentPos; pos >= usrInt; pos -= 1) {//starting at the currentPos number, as long as the pos (counter) is more than the input,
      myservo.write(pos);                           //write the servo to 1 less degrees than before until it reaches the input
      delay(msDelay);//wait msDelay ms
      currentPos -= 1;//decrement the currentPos counter
    }
  }
   
}
