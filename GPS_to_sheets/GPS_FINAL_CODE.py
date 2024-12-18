import pynmea2
import platform
import glob
import serial
import serial.tools.list_ports
import time
import gspread
import folium
# from folium.plugins import MarkerCluster
from oauth2client.service_account import ServiceAccountCredentials
from geopy.geocoders import Nominatim

# Initializing Nominatim geocoder
geolocator = Nominatim(user_agent="my_geolocator")

# Define the scope for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Define the ID of your Google Sheets spreadsheet
SPREADSHEET_ID = '1l22khPDvMOBthaCFC_6CDAElbuF2mDTxfroNSNGiyhI'


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
        m = folium.Map(location=[0, 0], zoom_start=12)
        # Authorize Google Sheets API
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/vepas/.vscode/GPS_Module/mylivegps.json',
                                                                 scope)
        client = gspread.authorize(creds)

        # Open the workbook
        workbook = client.open_by_key(SPREADSHEET_ID)
        worksheet = workbook.sheet1  # Use the first sheet

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
            if data.startswith('$GPRMC'):
                try:
                    # Parse the GNRMC sentence
                    msg = pynmea2.parse(data)
                    latitude = msg.latitude
                    longitude = msg.longitude
                    speed = msg.spd_over_grnd
                    location = geolocator.reverse((latitude, longitude))
                    print("Latitude:", latitude, "Longitude:", longitude, "Speed (knots):", speed, location.address)

                    # Construct the URL for Google Maps
                    map_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

                    # Update Google Sheets with data
                    row = [latitude, longitude, speed, time.strftime("%Y-%m-%d %H:%M:%S"), location.address, map_url]
                    worksheet.insert_row(row, index=2)

                    # Create the Folium map centered on your location
                    m = folium.Map(location=[latitude, longitude], zoom_start=12)

                    # =============================================

                    # # Add marker to the map
                    # folium.Marker(location=[latitude, longitude], popup='Current Location').add_to(m)

                    # # Save map to HTML file
                    # m.save('map.html')

                    # =============================================

                    # Define the URL pattern for the Esri World Imagery tileset
                    tile_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

                    # Add the Esri World Imagery tile layer to the map
                    folium.TileLayer(
                        tiles=tile_url,
                        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                        name='Esri World Imagery',
                        overlay=True
                    ).add_to(m)

                    # Add a marker to the map at the specified location
                    folium.Marker([latitude, longitude], popup='Your Location').add_to(m)

                    # Save the map to an HTML file
                    m.save('map.html')

                except pynmea2.ParseError as e:
                    print("Parse error:", e)

            # Introduce a delay of 5 minutes (300 seconds)
            time.sleep(1)

    except serial.SerialException as e:
        print(f"Failed to open COM port: {e}")


if __name__ == "__main__":
    main()
