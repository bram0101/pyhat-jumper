from sense_hat import SenseHat
from array import array

"""
Initializeer de HATLib bibliotheek.
"""
def hat_init():
    global hat_handle
    hat_handle = SenseHat()

"""
Deze methode geeft de SenseHat instantie die de HATLib bibliotheek gebruikt.
"""
def hat_getHandle():
    global hat_handle
    return hat_handle

"""
Dit roteerd hoe de LED matrix wordt weergegeven.

--r
    Hoeveel de LED matrix moet worden geroteerd. 0, 90, 180 of 270 zijn geldige waardes.
"""
def hat_setRotation(r):
    global hat_handle
    hat_handle.set_rotation(r)

"""
Dit zet de gehele LED matrix naar één kleur, of helemaal uit.

--color
    De kleur waar het naartoe moet veranderen. Het is een lijst van drie (R G B) integer waardes tussen de 0 en de 255.
"""
def hat_clearMatrix(color):
    global hat_handle
    hat_handle.clear(color)

"""
Hiermee stel je de low light waarde van de LED matrix.

--lowlight
    True als low light aan moet, False als het uit moet.
"""
def hat_lowlight(lowlight):
    global hat_handle
    hat_handle.low_light = lowlight

"""
Geeft de luchtvochtigheid.

return
    Het percentage als een float.
"""
def hat_getHumidity():
    global hat_handle
    return hat_handle.get_humidity()

"""
Geeft de temperatuur

return
    De temperatuur in graden Celsius als een float.
"""
def hat_getTemperature():
    global hat_handle
    return hat_handle.get_temperature()

"""
Geeft de luchtdruk.

return
    De luchtdruk in millibar als een float.
"""
def hat_getPressure():
    global hat_handle
    return hat_handle.get_pressure()

"""
Zet de IMU sensor componenten aan of uit.

--kompas
    True als het kompas(magnetometer) aan moet, False als het uit moet.

--gyro
    True als het gyroscoop aan moet, False als het uit moet.

--accel
    True als de accelerometer aan moet, False als het uit moet.
"""
def hat_imu_config(kompas, gyro, accel):
    global hat_handle
    hat_handle.set_imu_config(kompas, gyro, accel)

"""
De oriëntatie van de Pi in radialen.

return
    Een dictionary die de pitch, roll en yaw geeft met de index strings van "pitch", "roll" en "yaw".
"""
def hat_getOrientation():
    global hat_handle
    return hat_handle.get_orientation_radians()

"""
Geeft de waardes van de magnetometer sensor.

return
    Een dictionary met de waardes van de magnetometer in microtesla met de index strings van "x", "y" en "z".
"""
def hat_getCompass():
    global hat_handle
    return hat_handle.get_compass_raw()

"""
Geeft de waardes van de gyroscoop.

return
    Een dictionary met de waardes van de gyroscoop radialen per seconde met de index strings van "x", "y" en "z".
"""
def hat_getGyroscope():
    global hat_handle
    return hat_handle.get_gyroscope_raw()

"""
Geeft de waardes van de accelerometer.

return
    Een dictionary met de waardes van de accelerometer in G met de index strings van "x", "y" en "z".
"""
def hat_getAccelerometer():
    global hat_handle
    return hat_handle.get_accelerometer_raw()

"""
Wacht totdat er een InputEvent komt voor de joystick. De methode neemt over en eindigt pas als er een event is.
InputEvent is een tuple met drie variabelen.
"timestamp" is de tijd wanneer het is gebeurd.
"direction" is een string die de richting geeft als "up", "down", "left", "right" of "middle".
"action" is een string van wat er is gebeurd als "pressed", "released" of "held".

return
    De InputEvent.
"""
def hat_joystick_wait():
    global hat_handle
    return hat_handle.stick.wait_for_event()

"""
Geeft een lijst van InputEvent'en die zijn gebeurd sinds de laatste keer dat deze methode of hat_joystick_wait() was geroepen.
InputEvent is een tuple met drie variabelen.
"timestamp" is de tijd wanneer het is gebeurd.
"direction" is een string die de richting geeft als "up", "down", "left", "right" of "middle".
"action" is een string van wat er is gebeurd als "pressed", "released" of "held".

return
    Een lijst met InputEvent'en.
"""
def hat_joystick_get():
    global hat_handle
    return hat_handle.stick.get_events()

"""
Deze klas houd een framebuffer bij waar naar getekend kan worden.
Als de waardes floating point getallen in plaats van integer, dan wordt er anti-aliasing gebruikt.
Wanneer color wordt gevraagt, dan moet het een List van 4 floats zijn.
Methodes met de fast prefix doen geen anti-aliasing of alpha blending.
"""
class HATFrameBuffer:
    
    def __init__(self):
        self.buffer = array('f', [0] * 192)
        self.tmpBuffer = [[0, 0, 0]] * 64
    
    def swapBuffers(self):
        for x in range(0, 192, 3):
            self.tmpBuffer[int(x / 3)] = [max(min(int(self.buffer[x] * 255), 255), 0), max(min(int(self.buffer[x + 1] * 255), 255), 0), max(min(int(self.buffer[x + 2] * 255), 255), 0)]
        hat_handle.set_pixels(self.tmpBuffer)
    
    def clear(self, color):
        for x in range(0, 192, 3):
            self.buffer[x] = color[0]
            self.buffer[x + 1] = color[1]
            self.buffer[x + 2] = color[2]
    
    def setPixel(self, x, y, color):
        a1 = color[3]
        a2 = 1.0 - a1
        minX = int(x)
        minY = int(y)
        maxX = minX + 1
        maxY = minY + 1
        fracX = x - minX
        fracY = y - minY
        fracXInv = 1.0 - fracX
        fracYInv = 1.0 - fracY
        
        if(fracX == 0 and fracY == 0):
            if(minX < 0 or minX >= 8 or minY < 0 or minY >= 8):
                return
            index = (minY * 8 + minX) * 3
            self.buffer[index] = color[0] * a1 + self.buffer[index] * a2
            self.buffer[index + 1] = color[1] * a1 + self.buffer[index + 1] * a2
            self.buffer[index + 2] = color[2] * a1 + self.buffer[index + 2] * a2
        else:
            if(fracX == 0 and fracY != 0):
                if(minX < 0 or minX >= 8 or minY < 0 or minY >= 8):
                    return
                index1 = (minY * 8 + minX) * 3
                index2 = (maxY * 8 + minX) * 3
                a1 = color[3] * fracYInv
                a2 = 1.0 - a1
                self.buffer[index1] = color[0] * a1 + self.buffer[index1] * a2
                self.buffer[index1 + 1] = color[1] * a1 + self.buffer[index1 + 1] * a2
                self.buffer[index1 + 2] = color[2] * a1 + self.buffer[index1 + 2] * a2
                
                if(maxX < 0 or maxX >= 8 or maxY < 0 or maxY >= 8):
                    return
                a1 = color[3] * fracY
                a2 = 1.0 - a1
                self.buffer[index2] = color[0] * a1 + self.buffer[index2] * a2
                self.buffer[index2 + 1] = color[1] * a1 + self.buffer[index2 + 1] * a2
                self.buffer[index2 + 2] = color[2] * a1 + self.buffer[index2 + 2] * a2
            elif(fracY == 0 and fracX != 0):
                if(minX < 0 or minX >= 8 or minY < 0 or minY >= 8):
                    return
                index1 = (minY * 8 + minX) * 3
                index2 = (minY * 8 + maxX) * 3
                a1 = color[3] * fracXInv
                a2 = 1.0 - a1
                self.buffer[index1] = color[0] * a1 + self.buffer[index1] * a2
                self.buffer[index1 + 1] = color[1] * a1 + self.buffer[index1 + 1] * a2
                self.buffer[index1 + 2] = color[2] * a1 + self.buffer[index1 + 2] * a2
                
                if(maxX < 0 or maxX >= 8 or maxY < 0 or maxY >= 8):
                    return
                a1 = color[3] * fracX
                a2 = 1.0 - a1
                self.buffer[index2] = color[0] * a1 + self.buffer[index2] * a2
                self.buffer[index2 + 1] = color[1] * a1 + self.buffer[index2 + 1] * a2
                self.buffer[index2 + 2] = color[2] * a1 + self.buffer[index2 + 2] * a2
            else:
                if(minX < 0 or minX >= 8 or minY < 0 or minY >= 8):
                    return
                index1 = (minY * 8 + minX) * 3
                index2 = (minY * 8 + maxX) * 3
                a1 = color[3] * fracYInv * fracXInv
                a2 = 1.0 - a1
                self.buffer[index1] = color[0] * a1 + self.buffer[index1] * a2
                self.buffer[index1 + 1] = color[1] * a1 + self.buffer[index1 + 1] * a2
                self.buffer[index1 + 2] = color[2] * a1 + self.buffer[index1 + 2] * a2
                
                if(maxX < 0 or maxX >= 8 or maxY < 0 or maxY >= 8):
                    return
                a1 = color[3] * fracYInv * fracX
                a2 = 1.0 - a1
                self.buffer[index2] = color[0] * a1 + self.buffer[index2] * a2
                self.buffer[index2 + 1] = color[1] * a1 + self.buffer[index2 + 1] * a2
                self.buffer[index2 + 2] = color[2] * a1 + self.buffer[index2 + 2] * a2
                
                index1 = (maxY * 8 + minX) * 3
                index2 = (maxY * 8 + maxX) * 3
                a1 = color[3] * fracY * fracXInv
                a2 = 1.0 - a1
                self.buffer[index1] = color[0] * a1 + self.buffer[index1] * a2
                self.buffer[index1 + 1] = color[1] * a1 + self.buffer[index1 + 1] * a2
                self.buffer[index1 + 2] = color[2] * a1 + self.buffer[index1 + 2] * a2
                
                a1 = color[3] * fracY * fracX
                a2 = 1.0 - a1
                self.buffer[index2] = color[0] * a1 + self.buffer[index2] * a2
                self.buffer[index2 + 1] = color[1] * a1 + self.buffer[index2 + 1] * a2
                self.buffer[index2 + 2] = color[2] * a1 + self.buffer[index2 + 2] * a2
    
    def fillRect(self, xMin, yMin, xMax, yMax, color):
        minX = int(xMin)
        minY = int(yMin)
        maxX = int(ceil(xMax))
        maxY = int(ceil(yMax))
        minXFrac = xMin - minX
        minYFrac = yMin - minY
        maxXFrac = maxX - xMax
        maxYFrac = maxY - yMax
        a1 = color[3]
        a2 = 1.0 - a1
        index = 0
        indexJ = 0
        for j in range(minY, maxY + 1):
            if(j < 0 or j >= 8):
                continue
            indexJ = j * 8 * 3
            for i in range(minX, maxX + 1):
                if(i < 0 or i >= 8):
                    continue
                index = indexJ + i * 3
                a1 = color[3]
                if(j == minY):
                    a1 *= 1.0 - minYFrac
                elif(j == maxY):
                    a1 *= maxYFrac
                if(i == minX):
                    a1 *= 1.0 - minXFrac
                elif(i == maxX):
                    a1 *= maxXFrac
                a2 = 1.0 - a1
                self.buffer[index] = color[0] * a1 + self.buffer[index] * a2
                self.buffer[index + 1] = color[1] * a1 + self.buffer[index + 1] * a2
                self.buffer[index + 2] = color[2] * a1 + self.buffer[index + 2] * a2
    
    def fastSetPixel(self, x, y, color):
        if(x < 0 or x >= 8 or y < 0 or y >= 8):
            return
        index = (int(y) * 8 + int(x)) * 3
        self.buffer[index] = color[0]
        self.buffer[index + 1] = color[1]
        self.buffer[index + 2] = color[2]
    
    def fastFillRect(self, xMin, yMin, xMax, yMax, color):
        minX = int(min(7, max(0, xMin)))
        minY = int(min(7, max(0, yMin)))
        maxX = int(min(7, max(0, xMax)))
        maxY = int(min(7, max(0, yMax)))
        index = 0
        for j in range(minY, maxY):
            index = j * 24 + minX * 3
            for i in range(minX, maxX):
                self.buffer[index] = color[0]
                self.buffer[index + 1] = color[1]
                self.buffer[index + 2] = color[2]
                index += 3
    
    def getPixel(self, x, y):
        if(x < 0 or x >= 8 or y < 0 or y >= 8):
            return
        index = (int(y) * 8 + int(x)) * 3
        return [self.buffer[index], self.buffer[index + 1], self.buffer[index + 2]]