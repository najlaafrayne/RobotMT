""" PinceClass.py - An object to control the servomotor of the clamp.
 
Original author:
 Marc Bocquet <marc.bocquet@univ-amu.fr>
 
Current maintainer:
 Marc Bocquet <marc.bocquet@univ-amu.fr>
 
Contributors:
 
 
Example::
 
    from PinceClass import PinceClass
    Pince = PinceClass()
    Pince.ascenseur_move(100)
    Pince.open()
    Pince.close()
 
path.py requires Python 2.7 or later.
"""
################################################################################
################################################################################
import serial
import time
import RPi.GPIO as GPIO


PING       = [0x01]
READ_DATA  = [0x02]
WRITE_DATA = [0x03]
REG_WRITE  = [0x04]
ACTION     = [0x05]
RESET      = [0x06]
SYNC_WRITE = [0x83]

_ServoAdd={'Model':0, 'id':0x03, 'AlarmLED':0x11, 'GlobalPos':0x1E, 'PosCur':0x24}

LED_ON = WRITE_DATA + [0x19,0x01]
LED_OFF = WRITE_DATA + [0x19,0x00]

closeR = WRITE_DATA + [0x1E,0xA0,0x00,0xFF,0x00,0xFF,0x00]
openR =  WRITE_DATA + [0x1E,0x78,0x05,0xFF,0x03,0xFF,0x03]

closeL = WRITE_DATA + [0x1E,0x94,0x0C,0xFF,0x00,0xFF,0x00]
openL =  WRITE_DATA + [0x1E,0x48,0x08,0xFF,0x03,0xFF,0x03]

UP = WRITE_DATA + [0x1E,0x00,0x00,0xFF,0x03]
DOWN =  WRITE_DATA + [0x1E,0x00,0x00,0xFF,0x07]
STOP =  WRITE_DATA + [0x1E,0x00,0x00,0x00,0x00]
class PinceClass:
    def __init__(self, portstring="/dev/ttyAMA0"):
        self.port = serial.Serial(portstring, baudrate=57600, bytesize=8, parity='N', timeout=3.0)
        self.id_ServoR = 0x01
        self.id_ServoL = 0x02
        self.id_ServoC = 0x03
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)

    def _Checksum(self, s):
        """Calculate the Dynamixel checksum (~(ID + length + ...)) & 0xFF."""
        return (~sum(s)) & 0xFF

    def make_string(self, id_Servo,packet):
        P = [id_Servo,len(packet)+1] + packet
        return [0xFF,0xFF] + P + [self._Checksum(P)]

    def servo_read(self, id_Servo, RegAdd, nbReg):
        self.port.flushInput()
        GPIO.output(18, GPIO.HIGH) # Write Mode
        if type(RegAdd) is str:
            packet = READ_DATA + [_ServoAdd[RegAdd]] + [nbReg]
        else:
            packet = READ_DATA + [RegAdd] + [nbReg]
        s = self.make_string(id_Servo,packet)
        self.port.write("".join(map(chr,s)))
        self.port.flushOutput()
        time.sleep(0.0012)
        GPIO.output(18, GPIO.LOW) # Read Mode
        # Handle the read.
        res = [map(ord, self.port.read())[0]]
        while self.port.inWaiting() > 0:
            res.append(map(ord, self.port.read())[0])
        GPIO.output(18, GPIO.HIGH) # Write Mode
        
        if len(res) == 0 or res[0] != 0xFF or res[1] != 0xFF:
          raise ValueError, "Bad Header! ('%s')" % str(res)
        
        if self._Checksum(res[2:-1]) != res[-1]:
          raise ValueError, "Checksum %s should be %s" % (self._Checksum(res[2:-1]),res[-1])
          
        id_Servo_read, length = res[2:4]
        if id_Servo_read != id_Servo:
          raise ValueError, "Bad id_Servo! ('%s')" % str(res)
        parameters = res[5:-1]
        return parameters
    def servo_write(self,id_Servo,packet):
        self.port.write("".join(map(chr,self.make_string(id_Servo,packet))))
        time.sleep(0.01)
    def open(self):
        # OPEN
        GPIO.output(18, GPIO.HIGH) # Write Mode
        self.servo_write(self.id_ServoR,openR)
        self.servo_write(self.id_ServoL,openL)
    def close(self):
        # CLOSE
        GPIO.output(18, GPIO.HIGH) # Write Mode
        self.servo_write(self.id_ServoR,closeR)
        self.servo_write(self.id_ServoL,closeL)
    def up(self):
        self.servo_write(self.id_ServoC,UP)
    def down(self):
        self.servo_write(self.id_ServoC,DOWN)
    def stop(self):
        self.servo_write(self.id_ServoC,STOP)
    def ascenseur_move(self,Vts):
        """
            Vts : -1023 to 1023
        """
        Sgn=0
        if Vts<0:
            Sgn=4
            Vts=-Vts
        if not 0 <= Vts <= 1023:
            raise ValueError, "EnWiring illegal value: %d" % Vts
        self.servo_write(self.id_ServoC,WRITE_DATA + [0x20, Vts & 255, (Vts >> 8)|Sgn])
    def led_off(self):
        self.servo_write(self.id_ServoL,LED_OFF)
        self.servo_write(self.id_ServoR,LED_OFF)
        self.servo_write(self.id_ServoC,LED_OFF)
    def led_on(self):
        self.servo_write(self.id_ServoL,LED_ON)
        self.servo_write(self.id_ServoR,LED_ON)
        self.servo_write(self.id_ServoC,LED_ON)