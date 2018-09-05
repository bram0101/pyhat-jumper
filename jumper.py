from common.HATLib import *
import time
import random
from math import floor
from math import ceil
from math import pow

noisetable = array('f', [0] * 16 * 16 * 16)
for i in range(0, 16 * 16 * 16):
    noisetable[i] = random.random()

def lerp(x, y, t):
    return x * t + y * (1.0 - t)

def perlinnoise(x, y, z):
    minX = int(floor(x))
    minY = int(floor(y))
    minZ = int(floor(z))
    maxX = int(ceil(x))
    maxY = int(ceil(y))
    maxZ = int(ceil(z))
    fracX = x - minX
    fracY = y - minY
    fracZ = z - minZ
    
    x000 = noisetable[((minX % 16) * 16 + (minY % 16)) * 16 + (minZ % 16)]
    x100 = noisetable[((maxX % 16) * 16 + (minY % 16)) * 16 + (minZ % 16)]
    x010 = noisetable[((minX % 16) * 16 + (maxY % 16)) * 16 + (minZ % 16)]
    x110 = noisetable[((maxX % 16) * 16 + (maxY % 16)) * 16 + (minZ % 16)]
    
    x001 = noisetable[((minX % 16) * 16 + (minY % 16)) * 16 + (maxZ % 16)]
    x101 = noisetable[((maxX % 16) * 16 + (minY % 16)) * 16 + (maxZ % 16)]
    x011 = noisetable[((minX % 16) * 16 + (maxY % 16)) * 16 + (maxZ % 16)]
    x111 = noisetable[((maxX % 16) * 16 + (maxY % 16)) * 16 + (maxZ % 16)]
    
    y000 = lerp(x000, x100, fracX)
    y010 = lerp(x010, x110, fracX)
    y100 = lerp(y000, y010, fracY)
    y001 = lerp(x001, x101, fracX)
    y011 = lerp(x011, x111, fracX)
    y101 = lerp(y001, y011, fracY)
    return lerp(y100, y101, fracZ)

def fractalnoise(x, y, z):
    res = 0.0
    weight = 1.0
    mult = 1.0
    scale = 1.0
    for i in range(0, 4):
        mult = pow(0.5, i)
        scale = pow(2, i)
        res += perlinnoise(x * scale, y * scale, z * scale) * mult
        weight += mult
    return res / weight

def init():
    global framebuffer, targetDelta
    
    hat_init()
    hat_setRotation(90)
    hat_lowlight(True)
    framebuffer = HATFrameBuffer()
    targetDelta = 1.0 / 20.0
    
    reset()

def reset():
    global world, worldI, xPos, yPos, xVel, yVel, jumping, dblJump, tint, playerColor, gameover_time, gametime, speed
    
    world = array('b', [0] * 10)
    worldI = 0
    xPos = 0.0
    yPos = 1.0
    xVel = 3.0
    yVel = 0.0
    jumping = False
    dblJump = 0
    tint = [0, 1, 1]
    playerColor = [1.0 - tint[0], 1.0 - tint[1], 1.0 - tint[2]]
    if(playerColor[0] == 0 and playerColor[1] == 0 and playerColor[2] == 0):
        playerColor = [1, 0, 1]
    playerColorNormalizer = max(playerColor[0], max(playerColor[1], playerColor[2]))
    playerColor[0] /= playerColorNormalizer
    playerColor[1] /= playerColorNormalizer
    playerColor[2] /= playerColorNormalizer
    gameover_time = -1.0
    gametime = 0.0
    speed = 1.0
    
    hat_joystick_get() #Tijdens het knipperend doodscherm kan je de joystick gebruiken, maar die willen wij uit de queue halen.

def gameover():
    global gameover_time
    gameover_time = time.time()
    
def getWorldData(x):
    return world[int(x / 3) % 10]

def updateWorld():
    global world, worldI
    
    for i in range(worldI, int(xPos / 3) - 2):
        p1 = world[int(i - 1) % 10]
        p2 = world[int(i - 2) % 10]
        p3 = world[int(i - 3) % 10]
        r1 = random.randint(-5, 3)
        ny = p1 + r1
        if(random.randint(0, 1) == 0):
            ny = p1
        if(random.randint(0, 6) == 0):
            ny = -1
        if(ny > 5):
            ny = 5
        if(ny < -1):
            ny = -1
        if(p1 == -1 and p2 == -1):
            if(p3 <= 0):
                ny = 0
            else:
                ny = p3
        world[int(i) % 10] = ny
    
    worldI = int(xPos / 3) - 2

def input():
    global jumper_run, xPos, yPos, xVel, yVel, jumping, dblJump, gametime, speed
    
    events = hat_joystick_get()
    t1 = 0.0
    jumpTime = 0.0
    for e in events:
        if(e.action == "pressed"):
            t1 = e.timestamp
            jumping = True
            if(e.direction == "right"):
                jumper_run = False
        elif(e.action == "released"):
            jumpTime += e.timestamp - t1
            jumping = False
    
    if(gameover_time > 0):
        if(time.time() - gameover_time > 3):
            reset()
        return
    
    nxPos = xPos + delta * speed * xVel # We slaan het op naar een tijdelijke variabele voor botsing detectie.
    
    f = -7.0 # Zwaartekracht
    
    nwy = getWorldData(nxPos)
    
    if(int(yPos) - nwy != 1 and dblJump > 1):
        t1 = 0 # Als wij niet op een blok zitten, dan mag je niet springen.
    
    if(jumping and t1 > 0):
        yVel = 5.0 # De joystick is ingedrukt sinds de afgelopen tik. t1 wordt alleen aangepast als e.action "pressed" is.
        dblJump += 1 # Voeg een toe aan de double jump counter. Als die 2 of hoger komt, kan je niet meer springen.
    elif(jumpTime > 0 and t1 > 0):
        yVel = 5.0 * (jumpTime / delta / speed) # De joystick was heel kort ingedrukt, dus spring een klein beetje,    
    if(jumping and yVel > 0):
        f += 1.5 # Dit zorgt ervoor dat als wij de joystick langer ingedrukt houden, dat hij hoger springt.
    
    yVel += delta * f
    
    nyPos = yPos + delta * speed * yVel
    
    # Snelle botsing detectie.
    if(int(nyPos) <= nwy and int(yPos) > nwy):
        nyPos = nwy + 1
        yVel = 0
        dblJump = 0 # Reset de double jump counter
    elif(int(nyPos) >= nwy and int(yPos) < nwy):
        nyPos = nwy - 1
        yVel = 0
    elif(int(nyPos) == nwy):
        nyPos = nwy + 1
        yVel = 0
        dblJump = 0
    elif(int(yPos) == nwy and int(nyPos) + 1 == nwy):
        nyPos = nwy + 1
        yVel = 0
        dblJump = 0
    if(nyPos < 0):
        gameover()
    
    yPos = nyPos
    xPos = nxPos
    
    gametime += delta
    speed = ((gametime * 0.1) / ((gametime * 0.1) + 1)) * 2.0 + 1.0


def render():
    framebuffer.clear(tint)
    if(gameover_time > 0):
        if(int((time.time() - gameover_time) * 2) % 2 == 0):
            return
    
    for i in range(0, 8):
        for j in range(0, 8):
            n = min(1, max(0.25, fractalnoise((xPos + i) * 0.125, j * 0.125, gametime * 0.5) * 3.0 - 0.3333))
            framebuffer.setPixel(7 - i, j, [tint[0] * n, tint[1] * n, tint[2] * n, 1.0])
    
    for i in range(0, 8):
        y = getWorldData(xPos + i - 3)
        framebuffer.setPixel(7-i, y, [0, 0, 0, 1])
    framebuffer.setPixel(5, yPos, [playerColor[0], playerColor[1], playerColor[2], 1])
    
    if(worldI == 0): # Countdown
        framebuffer.setPixel(2, 6, [0, 0, 0, 1])
        framebuffer.setPixel(3, 6, [0, 0, 0, 1])
        framebuffer.setPixel(4, 6, [0, 0, 0, 1])
        framebuffer.setPixel(5, 6, [0, 0, 0, 1])
        framebuffer.setPixel(5, 5, [0, 0, 0, 1])
        framebuffer.setPixel(2, 4, [0, 0, 0, 1])
        framebuffer.setPixel(3, 4, [0, 0, 0, 1])
        framebuffer.setPixel(4, 4, [0, 0, 0, 1])
        framebuffer.setPixel(5, 4, [0, 0, 0, 1])
        framebuffer.setPixel(2, 3, [0, 0, 0, 1])
        framebuffer.setPixel(2, 2, [0, 0, 0, 1])
        framebuffer.setPixel(3, 2, [0, 0, 0, 1])
        framebuffer.setPixel(4, 2, [0, 0, 0, 1])
        framebuffer.setPixel(5, 2, [0, 0, 0, 1])
    elif(worldI == 1):
        framebuffer.setPixel(5, 6, [0, 0, 0, 1])
        framebuffer.setPixel(5, 5, [0, 0, 0, 1])
        framebuffer.setPixel(5, 4, [0, 0, 0, 1])
        framebuffer.setPixel(4, 4, [0, 0, 0, 1])
        framebuffer.setPixel(3, 4, [0, 0, 0, 1])
        framebuffer.setPixel(2, 6, [0, 0, 0, 1])
        framebuffer.setPixel(2, 5, [0, 0, 0, 1])
        framebuffer.setPixel(2, 4, [0, 0, 0, 1])
        framebuffer.setPixel(2, 3, [0, 0, 0, 1])
        framebuffer.setPixel(2, 2, [0, 0, 0, 1])
    elif(worldI == 2):
        framebuffer.setPixel(2, 6, [0, 0, 0, 1])
        framebuffer.setPixel(3, 6, [0, 0, 0, 1])
        framebuffer.setPixel(4, 6, [0, 0, 0, 1])
        framebuffer.setPixel(5, 6, [0, 0, 0, 1])
        framebuffer.setPixel(2, 5, [0, 0, 0, 1])
        framebuffer.setPixel(2, 4, [0, 0, 0, 1])
        framebuffer.setPixel(3, 4, [0, 0, 0, 1])
        framebuffer.setPixel(4, 4, [0, 0, 0, 1])
        framebuffer.setPixel(5, 4, [0, 0, 0, 1])
        framebuffer.setPixel(2, 3, [0, 0, 0, 1])
        framebuffer.setPixel(2, 2, [0, 0, 0, 1])
        framebuffer.setPixel(3, 2, [0, 0, 0, 1])
        framebuffer.setPixel(4, 2, [0, 0, 0, 1])
        framebuffer.setPixel(5, 2, [0, 0, 0, 1])
    elif(worldI == 3):
        framebuffer.setPixel(2, 6, [0, 0, 0, 1])
        framebuffer.setPixel(3, 6, [0, 0, 0, 1])
        framebuffer.setPixel(4, 6, [0, 0, 0, 1])
        framebuffer.setPixel(5, 6, [0, 0, 0, 1])
        framebuffer.setPixel(2, 5, [0, 0, 0, 1])
        framebuffer.setPixel(2, 4, [0, 0, 0, 1])
        framebuffer.setPixel(3, 4, [0, 0, 0, 1])
        framebuffer.setPixel(4, 4, [0, 0, 0, 1])
        framebuffer.setPixel(5, 4, [0, 0, 0, 1])
        framebuffer.setPixel(5, 3, [0, 0, 0, 1])
        framebuffer.setPixel(2, 2, [0, 0, 0, 1])
        framebuffer.setPixel(3, 2, [0, 0, 0, 1])
        framebuffer.setPixel(4, 2, [0, 0, 0, 1])
        framebuffer.setPixel(5, 2, [0, 0, 0, 1])
    elif(worldI == 4):
        framebuffer.setPixel(2, 2, [0, 0, 0, 1])
        framebuffer.setPixel(3, 2, [0, 0, 0, 1])
        framebuffer.setPixel(4, 2, [0, 0, 0, 1])
        framebuffer.setPixel(3, 3, [0, 0, 0, 1])
        framebuffer.setPixel(3, 4, [0, 0, 0, 1])
        framebuffer.setPixel(3, 5, [0, 0, 0, 1])
        framebuffer.setPixel(3, 6, [0, 0, 0, 1])
        framebuffer.setPixel(4, 5, [0, 0, 0, 1])
        

def cleanUp():
    hat_clearMatrix([0, 0, 0])
    hat_setRotation(0)

def run():
    global jumper_run, delta
    
    init()
    
    jumper_run = True
    time1 = time.time()
    time2 = time.time()
    
    while(jumper_run):
        time2 = time.time()
        delta = time2 - time1
        time1 = time2
        
        updateWorld()
        input()
        render()
        framebuffer.swapBuffers()
        
        sleepAmt = max(targetDelta - (time.time() - time2), 0)
        print("D: " + str(int(delta * 1000)) + "ms  sleep: " + str(int(sleepAmt * 1000)) + "ms")
        time.sleep(sleepAmt)
    
    cleanUp()

if __name__ == "__main__":
    run()