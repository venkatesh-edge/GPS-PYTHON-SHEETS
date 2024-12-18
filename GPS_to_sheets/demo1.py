import serial
import pynmea2
import platform
import glob
import serial.tools.list_ports
import time

def get_serial_port():
    system = platform.system()
    if system == 'Windows':
        # Automatically detect COM port on Windows
        ports = serial.tools.list_ports.comports()
        for port_info in ports:
            if 'USB-SERIAL' in port_info.description:
                return port_info.device
        raise Exception("No COM port found")
    elif system == 'Linux':
        # Automatically detect serial port on Linux
        for port in glob.glob('/dev/ttyUSB*'):
            return port
        raise Exception("No serial port found on Linux")
    else:
        raise Exception(f"Unsupported operating system: {system}")

def main():
    try:
        # Get the COM port dynamically
        COM_PORT = get_serial_port()
        print(f"Detected COM port: {COM_PORT}")

        # Open the COM port
        ser = serial.Serial(COM_PORT, 9600, timeout=1)
        print(f"Opened COM port {COM_PORT}")

        while True:
            # Read a line from the COM port
            data = ser.readline().decode('ascii')

            # Print the raw NMEA sentence
            print("Raw NMEA:", data.strip())

            # Check if the line contains a GNRMC sentence
            if data.startswith('$GNRMC'):
                try:
                    # Parse the GNRMC sentence
                    msg = pynmea2.parse(data)
                    latitude = msg.latitude
                    longitude = msg.longitude
                    speed = msg.spd_over_grnd
                    print("Latitude:", latitude, "Longitude:", longitude, "Speed (knots):", speed)
                except pynmea2.ParseError as e:
                    print("Parse error:", e)

            # Introduce a delay of 1 second
            time.sleep(60)

    except serial.SerialException as e:
        print(f"Failed to open COM port: {e}")

if __name__ == "__main__":
    main()
