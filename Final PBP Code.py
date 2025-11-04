from machine import Pin, PWM, I2C, UART
import time

# Pin configuration
PWM_PIN = 16
BUTTON_PIN = 13
UART_TX = 8
UART_RX = 9

DUTY_DEFAULT = 32768
DEBOUNCE = 0.2

# I2C Signal Pins
I2C_SDA = 14    #serial data 
I2C_SCL = 15    #serial clock 
ADS1015_ADDR = 0x48     #address for the analog - to - digital converter
ADS1015_PWM = 2

# Sets up hardware
pwm = PWM(Pin(16))
pwm.freq(1000)
pwm.duty_u16(DUTY_DEFAULT)

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
uart = UART(1, 115200, tx=Pin(UART_TX), rx=Pin(UART_RX))

# I2C + ADS 1015 configuration information
i2c = I2C(1, sda=Pin(14), scl=Pin(15))
from ads1x15 import ADS1015    #code given by the prof to convert the signals into digital format
adc = ADS1015(i2c, ADS1015_ADDR)

# Helping functions
def send_value(value):
    uart.write(str(value) + "\n")# Turns value into string and send it to UART
    time.sleep(0.05)

def receive_value():
    if uart.any():       #check if there's data in progress
        try:
            return int(uart.readline().strip()) #deciphers the line and turns it back into integer + cleans it up
        except:
            return None
    return None

def read_filtered_pwm():
    raw = adc.read(0, ADS1015_PWM) # Reads voltage from ADC channel 0
    time.sleep(0.05)
    return raw

def button_pressed():
    if button.value():
        time.sleep(0.2)    #debounces the button 
        return True
    return False

# Main loop that measures, sends, and receives PWM values
while True:
    if button_pressed():
        # Sends PWM duty to partner
        send_value(DUTY_DEFAULT)
        
        # Receive partner's PWM duty
        partner_pwm = None
        while partner_pwm is None:
            partner_pwm = receive_value()
            
        # Measures our PWM
        my_measure = read_filtered_pwm()
        
        # Sends our measurement back to partner
        send_value(my_measure)
        
        # Receive partner's ADC measurement
        partner_measure = None
        while partner_measure is None:
            partner_measure = receive_value()
        
        # Computes and prints difference
        difference = abs(partner_measure - my_measure)
        
        print("\n=== RESULT ===")
        print("Partner measured:", partner_measure)
        print("You measured:    ", my_measure)
        print("Difference:      ", difference)

        time.sleep(0.5)
