import RPi.GPIO as GPIO
import time
import conf, json, time, math, statistics
from boltiot import Sms, Bolt


history_data=[]
GPIO.setmode(GPIO.BCM)
TRIG = 17                                 #Associate pin 23 to TRIG
ECHO = 27
PIR = 22 
PIR2 = 26
indicator = 23
print("Distance measurement in progress")

GPIO.setup(PIR,GPIO.IN)

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(indicator,GPIO.OUT)


def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]
                 #Set pin as GPIO in

while True:
    
  if GPIO.input(PIR) == 1:
      GPIO.output(indicator, GPIO.HIGH)
      time.sleep(2) 
  else:
      GPIO.output(indicator, GPIO.LOW)

  GPIO.output(TRIG, False)                 #Set TRIG as LOW
  print("Waitng For Sensor To Settle")
  time.sleep(1)                            #Delay of 2 seconds

  GPIO.output(TRIG, True)                  #Set TRIG as HIGH
  time.sleep(0.00001)                      #Delay of 0.00001 seconds
  GPIO.output(TRIG, False)                 #Set TRIG as LOW

  while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
    pulse_start = time.time()              #Saves the last known time of LOW pulse

  while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
    pulse_end = time.time()                #Saves the last known time of HIGH pulse 

  pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

  distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
  distance = round(distance, 2)            #Round to two decimal points

  if distance > 2 and distance < 400:      #Check whether the distance is within range
    response = distance - 0.5
    print("Distance:",response,"cm")  #Print distance with 0.5 cm calibration

    bound = compute_bounds(history_data,5,4)
    if not bound:
        required_data_count=5-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(int(response))
        time.sleep(0.5)
        continue
    history_data.append(response);

    try:
        if response > bound[0] :
            print ("Distance increased suddenly. Sending an SMS.")
            #response = sms.send_sms("Someone turned on the lights")
            print("This is the response ",response)
        elif response < bound[1]:
            print ("Distance decreased suddenly. Sending an SMS.")
            
            GPIO.output(indicator, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(indicator, GPIO.LOW)
            #response = sms.send_sms("Someone turned off the lights")
            print("This is the response ",response)
        
    except Exception as e:
        print ("Error1234",e)
    time.sleep(0.5)
    
    num = 0
    if GPIO.input(PIR) == 1:
      num += 1
      if num >= 2:
          GPIO.output(indicator, GPIO.HIGH)
      else:
          GPIO.output(indicator, GPIO.LOW)
    else:
        num  = 0
  print(num)

  #else:
   #   print("0") # there needs to be out of range in palce of '0'
  #print(GPIO.input(PIR))

      
#need to delete the pervious data in the algorithm so that we can use it way more predictive




