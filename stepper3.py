from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

sleep_time = 1000
  
orange = 29
yellow = 31
pink = 33
blue = 35

wave_sequence = [[1,0,0,0],
				 [0,1,0,0],
				 [0,0,1,0],
				 [0,0,0,1]]
  
GPIO.setup(orange, GPIO.OUT)
GPIO.output(orange, GPIO.LOW)

GPIO.setup(yellow, GPIO.OUT)
GPIO.output(yellow, GPIO.LOW)

GPIO.setup(pink, GPIO.OUT)
GPIO.output(pink, GPIO.LOW)

GPIO.setup(blue, GPIO.OUT)
GPIO.output(blue, GPIO.LOW)

def anticlockwise(rotations, speed):
  sleep_time=0.1 / float(speed)
  for loop in range(1,int(512*float(rotations))):
	  GPIO.output(coil_A_2_pin, 1)
	  sleep(sleep_time)
	  GPIO.output(coil_B_1_pin, 0)
	  sleep(sleep_time)
	  GPIO.output(coil_B_2_pin, 1)
	  sleep(sleep_time)
	  GPIO.output(coil_A_2_pin, 0)
	  sleep(sleep_time)
	  GPIO.output(coil_A_1_pin, 1)
	  sleep(sleep_time)
	  GPIO.output(coil_B_2_pin, 0)

	  sleep(sleep_time);
	  GPIO.output(coil_B_1_pin, 1)

	  sleep(sleep_time)
	  GPIO.output(coil_A_1_pin, 0)

	  sleep(sleep_time)
  GPIO.output(coil_B_1_pin, 0)

def clockwise(rotations, speed):
  sleep_time=0.1 / float(speed)
  for loop in range(1,int(512*float(rotations))):
	  pfio.digital_write(7,1)
	  sleep(sleep_time)
	  pfio.digital_write(4,0)
	  sleep(sleep_time)
	  pfio.digital_write(6,1)
	  sleep(sleep_time)
	  pfio.digital_write(7,0)
	  sleep(sleep_time)
	  pfio.digital_write(5,1)
	  sleep(sleep_time)
	  pfio.digital_write(6,0)
	  sleep(sleep_time)
	  pfio.digital_write(4,1)
	  sleep(sleep_time)
	  pfio.digital_write(5,0)
	  sleep(sleep_time)
  pfio.digital_write(4,0)

if __name__ == '__main__':
	try:
		for i in range(len(wave_sequence)):
			GPIO.output(orange, wave_sequence[i][0])
			GPIO.output(yellow, wave_sequence[i][1])
			GPIO.output(pink, wave_sequence[i][2])
			GPIO.output(blue, wave_sequence[i][3])
			#sleep(sleep_time)
			input("Press any key to the next step")
		
		
		GPIO.cleanup()
	except (KeyboardInterrupt, SystemExit):
			GPIO.cleanup()

