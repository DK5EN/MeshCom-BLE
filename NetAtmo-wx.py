#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Name: NetAtmo-wx.py
Author: Martin Stefan Werner
CallSign: DK5EN
Where to find: https://www.qrz.com/db/DK5EN
Date: 2025-03-07
Version: 2025030701
Description: The example script reads wether data from a NetAtmo WX station and adds OpenWeatherMap data. It then 
             sends a weather Report to Group 20 to a MeshCom node via UDP
MC FW: MeshCom 4.34q
MC HW: TLORA_V2_1_1p6

A word of Caution: as the MeshCom firmware is under heavy development, expect to see changes on the UDP interface

    This project is based on work by: https://icssw.org/meshcom/
    With insights from: https://srv08.oevsv.at/meshcom/#

License:
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Copyright (c) 2025 Martin S. Werner

You are free to:
- Share - copy and redistribute the material in any medium or format
- Adapt - remix, transform, and build upon the material

Under the following terms:
- Attribution - You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- ShareAlike - If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

Disclaimer:
This script is provided "as is", without warranty of any kind, express or implied.

There are reprequistes to be met, otherwise the script will fail:
    You need a MeshCom Node
    You need a NetAtmo weather station with outdoor module, rain and wind 
    --extudp must be on you MeshCom node and it must be reachable within the network
    You need a RaspberryPi 5, with 8GB RAM and Debian Bookwork

This is an educational script, that helps to understand of how to communicate to a MeshCom Node.
This script also deals with the complicated, but highly secure method of Netatmo login handling

"""

import requests
import json
import re
import os
from datetime import datetime, timedelta
import socket

CONFIG_FILE = "config.jsonc"
TOKENS_FILE = "tokens.json"

#Go to openweathermap.org and generate an API key
#https://home.openweathermap.org/users/sign_up

#Go to NetAtmo and access various data, including the refresh token
#https://dev.netatmo.com
#maybe delte token.json, then refresh token is used from config file

#  MH Umrechnung
def lat_lon_to_maidenhead(lat, lon):
    lon180=lon+180
    lat90=lat+90

    A=int((lon180)/20)
    B=int((lat90)/10)

    C=int(((lon180)%20)/2)
    D=int((lat90)%10)

    E=int(((lon180)%2)*12)
    F=int(((lat90)%1)*24)

    locator=f"{chr(A + ord('A'))}{chr(B + ord('A'))}{C}{D}{chr(E + ord('a'))}{chr(F + ord('a'))}"

    return locator

# Begüßung nach Tageszeit
def get_greeting():
    hour = datetime.now().hour
    if hour < 10:
        return "Guten Morgen"
    elif hour < 13:
        return "Mahlzeit"
    elif hour < 18:
        return "Schönen Nachmittag"
    elif hour < 22:
        return "Guten Abend"
    else:
        return "Gute Nacht"

#jsonc Fehlerbehandlung
def get_faulty_line(filename, line_num):
    """Holt die fehlerhafte Zeile aus der Datei."""
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        return lines[line_num - 1].strip()

#URLs speziell behandeln, weil sonst sind das Kommentare
def remove_comments_from_line(line):
    """Entfernt Kommentare aus einer Zeile, wenn sie nicht Teil einer URL sind."""
    # Falls die Zeile eine URL enthält, ignorieren wir sie
    if 'http://' in line or 'https://' in line:
        return line
    # Entferne Kommentare, die mit // beginnen
    return re.sub(r"//.*", "", line)

#jsonc Config einlesen
def load_json_with_comments(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            # Liest alle Zeilen und entfernt Kommentare aus jeder Zeile
            lines = file.readlines()
            cleaned_lines = [remove_comments_from_line(line).strip() for line in lines]

            # Füge die bereinigten Zeilen zusammen
            cleaned_data = "\n".join(cleaned_lines)
            
            # Entferne ungültige Steuerzeichen (außer \n, \t, \r)
            cleaned_data = re.sub(r"[\x00-\x1F\x7F]", "", cleaned_data)  # Entfernt alle Steuerzeichen
            
            # Versuche, die bereinigte JSON-Daten zu laden
            return json.loads(cleaned_data)
    
    except json.JSONDecodeError as e:
        # Fehler bei der JSON-Dekodierung abfangen und detaillierte Informationen bereitstellen
        line_num = e.lineno
        column_num = e.colno
        error_msg = e.msg
        print(f"Fehler beim Laden der Datei: {filename}")
        print(f"Fehler in Zeile {line_num}, Spalte {column_num}: {error_msg}")
        print(f"Fehlerhafte Zeile: {get_faulty_line(filename, line_num)}")
        print("Hint: Stelle sicher, dass alle Zeilen im Format '\"key\" : \"value\",' sind.")
        exit(1)

def read_tokens(file_path):
    try:
      with open(file_path,'r') as file:
        tokens = json.load(file)
    except FileNotFoundError:
        # Fehler abfangen, einfach stur weitermachen
        tokens = {}

    #überprüfe, ob request token vorhanden ist
    if 'request_token' in tokens:
        request_token = tokens['request_token']
    else:
        #REQUEST_TOKEN aus Config holen
        request_token = get_refresh_token()

    if 'expire_time' in tokens:
        expire_time = tokens['expire_time']
    else:
        expire_time = 0

    now = datetime.now()  # Aktuelle Zeit abrufen
    now_s = int(now.timestamp())  # Umwandlung in Sekunden seit Epoch

    valid = now_s < expire_time

    if 'access_token' in tokens and valid:
        access_token = tokens['access_token']
    else:
        #access_token von NetAtmo API mit request_token abrufen
        access_token = get_access_token_from_netatmo(request_token)

    return request_token, access_token

def save_tokens(filepath, request_token, access_token, expire_time):
    tokens = {
            'request_token': request_token,
            'access_token': access_token,
            'expire_time': expire_time
            }
    with open(filepath,'w') as file:
        json.dump(tokens,file)

#Funktion zum Abrufen des access_token von der NetAtmo APO mit request_token
def get_access_token_from_netatmo(request_token):

    #Config File auslesen
    config = load_json_with_comments(CONFIG_FILE)
    CLIENT_ID = config['CLIENT_ID'] 
    CLIENT_SECRET = config['CLIENT_SECRET'] 
    TOKEN_URL = config['TOKEN_URL']

    payload = {
      'grant_type' : 'refresh_token',
      'refresh_token' : request_token,
      'client_id' : CLIENT_ID,
      'client_secret' : CLIENT_SECRET
       }

    headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            }

    now = datetime.now()  # Aktuelle Zeit abrufen
    now_s = int(now.timestamp())  # Umwandlung in Sekunden seit Epoch

    response = requests.post(url=TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
      access_token = response.json()['access_token']
      request_token = response.json()['refresh_token']
      expire_date = now_s + response.json()['expires_in']

      #Tokens in Datei speichern
      save_tokens(TOKENS_FILE, request_token, access_token, expire_date)
      return access_token
    else:
      raise Exception("Faild to get access token from NetAtmo API")

def get_Openweather_apikey():
    config = load_json_with_comments(CONFIG_FILE)
    return config['api_key'] #OpenWetherMap

def get_refresh_token():
    config = load_json_with_comments(CONFIG_FILE)
    return config['REFRESH_TOKEN'] #NetAtmo auf dev Seite

def get_open_weather_data (lat, lon):
  api_key = get_Openweather_apikey()

  url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=de"

  response = requests.get(url)

  #Wahnsinnstabelle für meine Zwecke flach klopfen
  if response.status_code == 200:
    data = response.json()
    weather_data = {
      "City": data.get("name", "Unbekannt"),
      "description": data.get("weather", [{}])[0].get("description", "Unbekannt"),
      "temperature": data["main"]["temp"],
      "temp_min": data["main"]["temp_min"],
      "temp_max": data["main"]["temp_max"],
      "humidity": data["main"]["humidity"],
      "air_pressure": data["main"]["pressure"],
      "cloud_coverage": data["clouds"]["all"],
      "wind_speed": data["wind"]["speed"],
      "wind_deg": data["wind"]["deg"],
      "rain_last_1h": data.get("rain", {}).get("1h", 0),
      "snow_last_1h": data.get("snow", {}).get("1h", 0)
    }
    return weather_data

  else:
    print(f"Failed to retrive data: {response.status_code}")
    return None


# Wetterdaten von NetAtmo abrufen
def get_netatmo_data(config):
    #Refresh / Access Spielereien von NetAtmo
    request_token, access_token = read_tokens(TOKENS_FILE)

    token = access_token
    url = config['WEATHER_URL']

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    data = response.json()
    
    if "body" in data and "devices" in data["body"]:
        for device in data["body"]["devices"]:
            print(f"Das Wetter wird für {device['home_name']} bei NetAtmo ausgelesen ..\n")
    else:
        print("Keine Geräte gefunden bei NetAtmo!")

    return data

def format_weather_report():
    config = load_json_with_comments("config.jsonc")
    weather_data = get_netatmo_data(config)

    station = weather_data["body"]["devices"][0]

    home = station["place"]["city"]

    # Maidenhead locator berechnen aus Angaben auf NetAtmo
    location = station["place"]["location"]
    lon=location[0]
    lat=location[1]

    locator = lat_lon_to_maidenhead(lat, lon)

    #print(f"Der Maidenhead Locator für die Koordinaten ({lat}, {lon}) ist: {locator}")

    weather_data = get_open_weather_data(lat, lon)

    if weather_data:
      snow_last_1h = weather_data["snow_last_1h"]

      OW_city = weather_data["City"]
      OW_wx_desc = weather_data["description"]
      OW_temp = weather_data["temperature"]
      OW_humidity = weather_data["humidity"]
      OW_pressure = weather_data["air_pressure"]
      OW_rain_last_1h = weather_data["rain_last_1h"]
      OW_wind = weather_data["wind_speed"] * 3.6 #wir wollen km/h und keine m/s
      OW_cloud_coverage = weather_data["cloud_coverage"]

    else:
        print ("Failed to retrieve OpenWeather data.")

    #Jetzt NetAtmo Behandlung
    modules = {m["module_name"]: m for m in station["modules"]}
    
    pressure = station["dashboard_data"]["Pressure"]
    abs_pressure = station["dashboard_data"]["AbsolutePressure"]
    rain = modules["Regen"]["dashboard_data"].get("sum_rain_24", 0)
    rain_now = modules["Regen"]["dashboard_data"].get("Rain", 0)
    wind = modules["Wind"]["dashboard_data"].get("GustStrength", 0)
    temp = modules["Terrasse"]["dashboard_data"]["Temperature"]
    humidity = modules["Terrasse"]["dashboard_data"]["Humidity"]

    # **Finale Ausgabe**

    # Sinnvoll kombinierte Ausgabe von NetAtmo und OpenWeather 
    #return f"{get_greeting()}, WX {home}/{locator} {OW_wx_desc}: {OW_temp:.1f}°C/Terrasse {temp}°C, {humidity}% relH, QNH:{pressure}hPa/{abs_pressure}hPa, Regen {rain}mm/24h, Wind {OW_wind:.1f}km/h / Terrasse:{wind}km/h, {OW_cloud_coverage}/8 Wolken"
    return f"{get_greeting()}, WX {home}/{locator} {OW_wx_desc}: {temp}°C, {humidity}% relH, QNH:{pressure}hPa/{abs_pressure}hPa, rain {rain}mm/24h, wind {wind:.1f}km/h, {OW_cloud_coverage}/8 Wolken"

def send_udp_message (message, ip_address, port):
  try:
    # Create an UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send a Message
    sock.sendto(message.encode(), (ip_address,port))

    # Close the socket
    sock.close()

    return True
  except Exception as e:
    print(f"Error: {e}")
    return False

def send_mc_msg(grp, text):
   port = 1799 #    stadard Port für MC
   hostname = "dk5en-99.local"

   #grp="999"
   #grp="DK5EN-99"
   #grp="*"

   #Standard Text an MeshCom
   #msg="Test " + text
   msg= text

   #Standard Text an APRS.fi
   #msg="APRS:Test auf die " + grp + " via UDP + DNS Auflösung zusammengesetzt"
   #msg="APRS: mal alles raus an aprsi.fi "

   message = "{\"type\":\"msg\",\"dst\":\"" + grp + "\",\"msg\":\"" + msg + "\"}"

   print(f"Message : {message}")

   ip_address = socket.gethostbyname(hostname)
   if send_udp_message(message,ip_address,port):
       print("Message sent sccessful!")
   else:
       print("Failed to send message.")

if __name__ == "__main__":
    #print(format_weather_report())
    wx_report = format_weather_report()
    
    #Wettermeldungen in Gruppe 20
    send_mc_msg("20", wx_report)
