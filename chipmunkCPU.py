from random import random

class Chip8_Base:
    def __init__(self, debugState):
        self.debug = debugState
        self.mem = [1]*4096 # need 4096 zeroes
        self.vram = [0]*32*64 # need exactly this amount of zeroes(I know it wasn't VRAM before but whatever)
        self.keyinput = [0]*16 # 16 key inputs
        self.mem[0:79] = [0xF0, 0x90, 0x90, 0x90, 0xF0,
                          0x20, 0x60, 0x20, 0x20, 0x70,
                          0xF0, 0x10, 0xF0, 0x80, 0xF0,
                          0xF0, 0x10, 0xF0, 0x10, 0xF0,
                          0x90, 0x90, 0xF0, 0x10, 0x10,
                          0xF0, 0x80, 0xF0, 0x10, 0xF0,
                          0xF0, 0x80, 0xF0, 0x90, 0xF0,
                          0xF0, 0x10, 0x20, 0x40, 0x40,
                          0xF0, 0x90, 0xF0, 0x90, 0xF0,
                          0xF0, 0x90, 0xF0, 0x10, 0xF0,
                          0xF0, 0x90, 0xF0, 0x90, 0x90,
                          0xE0, 0x90, 0xE0, 0x90, 0xE0,
                          0xF0, 0x80, 0x80, 0x80, 0xF0,
                          0xE0, 0x90, 0x90, 0x90, 0xE0,
                          0xF0, 0x80, 0xF0, 0x80, 0xF0,
                          0xF0, 0x80, 0xF0, 0x80, 0x80]
        # some stolen font
        self.soundtimer = 0 # at early stages I won't be bothering with these timers, HOWEVER.....
        self.delaytimer = 0
        self.pc = 0x200 # program counter, AKA IP or EIP or RIP, instruction pointer
        self.registers = [0]*16 # 16 V registers
        self.stack = []
        self.i = 0 # memory adress register
        self.ExecutionEngine = Chip8_Exeggutor(self) # I wonder if we can do THAT
        self.currentOp = 0x0000
        self.drawflag = False
    def LoadROM(self, ROM):
        with open(ROM, "rb") as rom:
            dotbin = rom.read()
        for ip, vs in enumerate(dotbin):
            self.mem[self.pc+ip] = vs # enumerate handy here
    def Process(self):
        opcode = self.mem[self.pc] << 8 | self.mem[self.pc+1]
        self.currentOp = opcode
        self.ExecutionEngine.run_instruction(opcode)

class Chip8_Exeggutor:
    def __init__(self, base):
        self.machine = base
        self.keypad = {
        "1" : 0x1, "2" : 0x2, "3" : 0x3, "4" : 0xC,
        "q" : 0x4, "w" : 0x5, "e" : 0x6, "r" : 0xD,
        "a" : 0x7, "s" : 0x8, "d" : 0x9, "f" : 0xE,
        "z" : 0xA, "x" : 0x0, "c" : 0xB, "v" : 0xF }
    def run_instruction(self, opcode):
        # all things come from the doc below
        # http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
        # and a pong rom as a test
        nnn =  opcode & 0x0FFF
        n   =  opcode & 0x000F
        x   = (opcode & 0x0F00) >> 8
        y   = (opcode & 0x00F0) >> 4
        kk  =  opcode & 0x00FF
        if self.machine.debug:
            print("opcode:"+hex(opcode))
        if opcode == 0x00EE: # 0x00E: return from a subroutine, need to set PC to the last value on stack, then remove that value from stack
            self.machine.pc = self.machine.stack.pop()
        elif opcode & 0xF000 == 0x6000: # 0x6xkk: set V[x] == kk(got LULZ when writing this)
            self.machine.registers[x] == kk
        elif opcode & 0xF000 == 0xA000: # 0xAnnn: set I = nnn
            self.machine.i = nnn
        elif opcode & 0xF000 == 0xD000: # 0xDxyn: draw n-byte sprite in memory I at (Vx, Vy), set VF = collision
            # pass # skip drawing for now, need a solid CPU emulation first ### Time for DRAWING!!
            reg_x_coordinate = self.machine.registers[x]
            reg_y_coordinate = self.machine.registers[y]
            self.machine.registers[0xF] = 0
            for y_offset in range(n): # y_offset is row of sprite
                sprite_int = self.machine.mem[y_offset + self.machine.i]

                actual_y_coordinate = reg_y_coordinate + y_offset

                for x_offset, bit in enumerate(format(sprite_int, '08b')):
                    # loop through each bit in the byte
                    # find index in gfx memory array
                    # then XOR on the sprite bit vs gfx memory
                    actual_x_coordinate = reg_x_coordinate + x_offset

                    gfx_mem_index = actual_y_coordinate * 64 + actual_x_coordinate
                    pixel = self.machine.vram[gfx_mem_index]
                    # XOR written like this for clarity
                    if int(bit) == 1 and pixel == 1:
                        self.machine.registers[0xF] = 1
                        self.machine.vram[gfx_mem_index] = 0

                    if int(bit) == 1 and pixel == 0:
                        self.machine.vram[gfx_mem_index] = 1

                    if int(bit) == 0 and pixel == 1:
                        self.machine.vram[gfx_mem_index] = 1

                    if int(bit) == 0 and pixel == 0:
                        self.machine.vram[gfx_mem_index] = 0
            self.drawflag = True    
        elif opcode & 0xF000 == 0x2000: # 0x2nnn: call subroutine at nnn
            self.machine.stack.append(self.machine.pc) # save PC at top of the stack
            self.machine.pc = nnn - 2
        elif opcode & 0xF0FF == 0xF015: # 0xFx15: set delay timer = Vx
            self.machine.delaytimer = self.machine.registers[x]
        elif opcode & 0xF0FF == 0xF033: # 0xFx33: store BCD representation of Vx in memory I, I+1 and I+2
            value = int(self.machine.registers[x])
            self.machine.mem[self.machine.i] = value // 100 #  hundreds
            self.machine.mem[self.machine.i+1] = (value / 10) %10 # tenth, probably not a good solution
            self.machine.mem[self.machine.i+1] = value % 10 # units
        elif opcode & 0xF0FF == 0xF065: # 0xFx65: read registers V0 through Vx from memory starting at location I
            for V in range(x):
                #self.machine.mem[self.machine.i + 2*V] = self.machine.registers[V] # not a good solution probably ############ IT WAS A BAD SOLUTION, IT WASNT RIGHT!
                self.machine.registers[V] = self.machine.mem[self.machine.i + V]
        elif opcode & 0xF0FF == 0xF029: # 0xFx29: set I = location of sprite for digit Vx
            # pass # skip drawing for now nope, need it now
            self.machine.i = self.machine.registers[x] * 5 # 5B per sprite
        elif opcode & 0xF000 == 0x7000: # 0x7xkk: set Vx = Vx + kk
            self.machine.registers[x] = (self.machine.registers[x] + kk) % 255
            self.machine.registers[0xF] = 1 if self.machine.registers[x] + kk > 255 else 0 # Do we need that carry flag? It's undocumented!
        elif opcode & 0xF00F == 0xF007: # 0xFx07: set Vx to DT
            self.machine.registers[x] = self.machine.delaytimer
        elif opcode & 0xF000 == 0x3000: # 0x3xkk: skip next instruction if Vx == kk
            if self.machine.registers[x] == kk:
                self.machine.pc += 2
        elif opcode & 0xF000 == 0xC000: # 0xCxkk: set Vx = random byte & kk
            self.machine.registers[x] = kk & int(random()*255) # Is it bad docs? IT FUCKING FIXED IBM LOGO!
        elif opcode & 0xF0FF == 0xE0A1: # 0xExA1: skip next instruction if key with the value of Vx is not pressed
            if self.machine.debug:
                print("Is key "+str([name for name,val in self.keypad.items() if val == self.machine.registers[x]])+" pressed?y/n")
                i = input("")
                if i == "y":
                    self.machine.pc += 2
            elif self.machine.keyinput[self.machine.registers[x]] == 0:
                self.machine.pc += 2
        elif opcode & 0xF00F == 0x8002: # 0x8002: set Vx = Vx & Vy
            self.machine.registers[x] = self.machine.registers[x] & self.machine.registers[y]
        elif opcode & 0xF00F == 0x8000: # 0x8000: set Vx = Vy
            self.machine.registers[x] = self.machine.registers[y]
        elif opcode & 0xF000 == 0x4000: # 0x4000: skip next instruction if Vx != kk
            if not self.machine.registers[x] == kk:
                self.machine.pc += 2
        elif opcode & 0xF00F == 0x8004: # 0x8xy4: set Vx = Vx+Vy, set VF = carry
            result = self.machine.registers[x] + self.machine.registers[y]
            self.machine.registers[x] = result % 255 # only lower 8 bits
            if result > 255:
                self.machine.registers[0xF] = 1 # set carry
            else:
                self.machine.registers[0xF] = 0 # don't set carry
        elif opcode & 0xF000 == 0x1000: # 0x1nnn: JMP to adress nnn
            self.machine.pc = nnn - 2
        elif opcode & 0x00FF == 0x00E0: # 0x00E0: CLS
            self.machine.vram = [0]*32*64
        elif opcode & 0xF0FF == 0xF00A: # 0xFx0A: wait for a key press, store the key in Vx
            if self.machine.debug:
                try:
                    print("wait for key: choose key(0x1 to 0xF)")
                    i = input()
                    self.machine.registers[x] = int(i)
                except:
                    raise Exception("Ctrl+C on ... thing")
        elif opcode & 0xF0FF == 0xF01E: # 0xFx1E: set I = I + Vx
            self.machine.i = self.machine.i + self.machine.registers[x]
        else:
            print("chipmunk: execution error: unknown opcode "+hex(opcode))
            raise Exception