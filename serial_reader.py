import serial

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
while True:
    line = ser.readline().decode('utf-8').strip()  # Read a line, strip newline
    print(line + '\r')  # Add carriage return
