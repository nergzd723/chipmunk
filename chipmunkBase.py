from chipmunkCPU import *
import curses
from time import sleep
clock_delay = 1/60
def getDelay():
    return clock_delay
def setDelay(delay):
    global clock_delay
    clock_delay = delay
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
def render(stdscr, chip8CPU):
    stdscr.clear()
    stdscr.refresh()
    s = ""
    for y in range(32):
        row = chip8CPU.vram[y*64 : y*64 + 64]
        for x in row:
            if x == 1:
                s += "█"#"#"
            else:
                s += " "
        s += "\n"
    try:
        stdscr.addstr(0, 0, s)
    except:
        print("Make sure the terminal is big enough!")
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    stdscr.refresh()
    chip8CPU.drawflag = False
def update_keys(screen, chipchip):
    c = screen.getch()
    if c != -1:
        c = chr(c)
        for k,v in keypad.items(): # reset all to 0
            keypad[k] = 0
            if k == c:
                chipchip.keyinput[keypad.get(c)] == 1
def gfx(chip8):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(True)
    stdscr.nodelay(True)
    render(stdscr, chip8)
    while True:
        chip8.Process()
        processTimers(chip8)
        if chip8.drawflag:
            render(stdscr, chip8)
        update_keys(stdscr, chip8)
        sleep(1/60)
if __name__ == "__main__":
    chip8 = Chip8_Base(debugState=True)
    chip8.LoadROM("test_opcode.ch8")
    print("chipmunk: chip8 emulator/debugger")
    print("Please select command: s for step, c for infinite run, ldrom for loading rom")
    while True:
        main(chip8)