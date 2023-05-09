# Convert locations and time to sun angle
import PySimpleGUI as sg
import os.path
import sys
from datetime import datetime, time, timedelta
from math import pi, cos, sin
from pytz import timezone, utc
from timezonefinder import TimezoneFinder, timezonefinder
import datetime, pytz
import numpy
from sympy import *


def SunAngles2Loca(ele, azi, d, time):
    d = float(d)
    ele = float(ele)
    azi = float(azi)
    
    #fractional year
    gamma = 2 * pi / 365 * (d - 1 + (float(time[0] + time[1]) - 12) / 24)

    #equation of time
    eqtime = 229.18 * (0.000075 + 0.001868 * cos(gamma) - 0.032077 * sin(gamma) \
        - 0.014615 * cos(2 * gamma) - 0.040849 * sin(2 * gamma))

    #find declination
    decl = 0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma) \
        - 0.006758 * cos(2 * gamma) + 0.000907 * sin(2 * gamma) - 0.002697 \
            * cos(3 * gamma) + 0.00148 * sin(3 * gamma)

    la = Symbol('la')
    ha = Symbol('ha')
    f1 = cos(la)*cos(ha)*cos(decl) + sin(la)*sin(decl) - sin(2*pi*ele/180)
    f2 = sin(decl)*cos(la) - cos(decl)*sin(la)*cos(ha) - cos(azi)*cos(2*pi*ele/180)

    [la, ha] = nsolve((f1, f2), (la, ha), (1, 1), verify=False)

    tst = 4*(ha + 180)
    h = float(time[0] + time[1])
    min = float(time[3] + time[4])
    sc = float(time[6] + time[1])
    to = tst - h*60 - min - sc/60

    la = la*180/(2*pi)
    lo = 0
    for lo in range(-179, 180, 1):

        tf = timezonefinder.TimezoneFinder()
        tz_target = timezone(tf.certain_timezone_at(lng=lo, lat=la))
        tz = datetime.datetime.now(pytz.timezone(tz_target.zone)).strftime('%z')

        if abs(lo - ((to - eqtime + 60*float(tz)/100) / 4)) < 0.3:
            break

    return(la, lo)



file_list_column = [
    [
        sg.Text("Elevation Angle (°)              "),
        sg.In(size=(25, 1), enable_events=True, key="-ele-")
    ],
    [
        sg.Text("Azimuth Angle (°)               "),
        sg.In(size=(25, 1), enable_events=True, key="-azi-")
    ],
    [
        sg.Text("Time of Day (24h, XX:XX:XX)"),
        sg.In(size=(25, 1), enable_events=True, key="-time-")
    ],
    [
        sg.Text("Day of year                       "),
        sg.In(size=(25, 1), enable_events=True, key="-day-")
    ]
]


image_viewer_column = [
    [sg.Text("Location (Latitude, Longitude):")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]
# ----- Full layout -----
layout = [
    [sg.Column(file_list_column)], 
    [sg.Button("Submit")],
    [sg.HSeparator()],
    [sg.Column(image_viewer_column)],
]

window = sg.Window("Sun Angles and Time to Location", layout, element_justification='c')

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    if event == "Submit":
        out = SunAngles2Loca(values["-ele-"], values["-azi-"], values["-day-"], values["-time-"])
        window["-TOUT-"].update(out)

window.close()