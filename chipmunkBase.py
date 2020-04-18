from chipmunkCPU import *
import curses
from time import sleep
clock_delay = 1/1024
def getDelay():
    return clock_delay
def setDelay(delay):
    global clock_delay
    clock_delay = delay
keys = ["1", "2", "3", "4", "q", "w", "e", "r", "a", "s", "d", "f", "z", "x", "c", "v"]
keypad = {
    "1" : 0x1, "2" : 0x2, "3" : 0x3, "4" : 0xC,
    "q" : 0x4, "w" : 0x5, "e" : 0x6, "r" : 0xD,
    "a" : 0x7, "s" : 0x8, "d" : 0x9, "f" : 0xE,
    "z" : 0xA, "x" : 0x0, "c" : 0xB, "v" : 0xF }
def processTimers(chipchip):
    chipchip.pc += 2
    if chipchip.delaytimer > 0:
        chipchip.delaytimer -= 1
def main(chipchip):
    i = input(">>> ")
    if i == "s":
        chipchip.Process()
        processTimers(chipchip)
    elif i[:5] == "ldrom":
        rom = i.split(" ")
        print("Loading rom "+rom[1])
        chipchip.LoadROM(rom[1])
    elif i == "c":
            while True:
                try:
                    chipchip.Process()
                    processTimers(chipchip)
                    sleep(clock_delay)
                except Exception as e:
                    print("Error: stopping now")
                    print(e)
                    return
                except KeyboardInterrupt:
                    return
    elif i == "dump":
        print("pc:"+hex(chipchip.pc))
        print("opcode:"+hex(chipchip.currentOp))
    elif i == "skip":
        chipchip.pc += 2
    elif i[:4] == "dump":
        toDump = i.split(" ")[1]
        if toDump == "screen":
            string = ""
            ctr = 0
            for pixel in chipchip.vram:
                if ctr == 64:
                    ctr = 0
                    string = string+"\n"
                if pixel == 1:
                    string = string + chr(0x2588)
                else:
                    string = string + " "
                ctr+=1
            print(string)
        elif toDump == "registers":
            ctr = 0
            for register in chipchip.registers:
                print("V"+str(ctr)+":"+str(register))
                ctr+=1
    elif i[:5] == "delay":
        delay = i.split(" ")[1]
        setDelay(float(delay))
def gui(chipchip, screen):
    while True:
        try:
            update_keys(screen, chipchip)
            chipchip.Process()
            processTimers(chipchip)
            sleep(clock_delay)
            draw(screen, chipchip)
        except Exception as e:
            print("Error: stopping now")
            print(e)
            return
        except KeyboardInterrupt:
            return
def update_keys(screen, chipchip):
    c = screen.getch()
    if c != -1:
        c = chr(c)
        for key in chipchip.keyinput:
            chipchip.keyinput[chipchip.keyinput.index(key)] = 0 # reset all back to zero
        if c in keys:
            chipchip.keyinput[keys.index(c)] = 1

def draw(screen, chipchip):
    ctr = 0
    string = ""
    for pixel in chipchip.vram:
        if ctr == 64:
            ctr = 0
            string = string+"\n"
        if pixel == 1:
            string = string + chr(0x2588)
        else:
            string = string + " "
        ctr+=1
    screen.addstr(0,0,string)
    screen.refresh()
    chipchip.drawflag = False
if __name__ == "__main__":
    chip8 = Chip8_Base(debugState=False)
    chip8.LoadROM("pong.ch8")
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    screen.keypad(True)
    screen.nodelay(True)
    print("chipmunk: chip8 emulator/debugger")
    print("Please select command: s for step, c for infinite run, ldrom for loading rom")
    while True:
        gui(chip8, screen)