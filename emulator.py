import pyxel

class Arch242Emulator:
    def __init__(self, instructions: list[int]):
        self.PC = 0x0000
        
        # Memory
        self.memory = [0] * 256
        
        # Registers
        self.RA = self.RB = self.RC = self.RD = self.RE = 0
        self.ACC = 0
        self.CF = 0
        self.IOA = self.IOB = self.IOC = 0
    
        # Timer
        self.TIMER = 0
        self.timer_running = False
        
        self.TEMP = 0
        self.instructions = instructions
        
    def step(self):
        instruction = self.instructions[self.PC]
        
        inst_str = instruction >> 4
        if inst_str == 0x07:
            self.PC += 1
        if inst_str >= 0x04:
            self.PC += 2
        else:
            self.PC += 1
            
    def execute(self):
        self.instruction = self.instructions[self.PC]
        if self.instruction == 0x0000:
            self.ACC = (self.ACC << 3) | (self.ACC >> 1)
            
        elif self.instruction == 0x0001:
            self.ACC = (self.ACC >> 3) | (self.ACC << 1)
            
        elif self.instruction == 0x0002:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc << 4) | (cfacc >> 1)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0b01111
            
        elif self.instruction == 0x0003:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc >> 4) | (cfacc << 1)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0b01111    
            
        elif self.instruction == 0x0004:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.memory[ba]
            
        elif self.instruction == 0x0005:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC
            
        elif self.instruction == 0x0006:
            dc = (self.RD << 4) | self.RC
            self.ACC = self.memory[dc]   
            
        elif self.instruction == 0x0007:
            dc = (self.RD << 4) | self.RC
            self.memory[dc] = self.memory[dc]
            
        elif self.instruction == 0x0008:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba] + self.CF
            if acc >> 8:
                self.CF = acc >> 8
                self.ACC = acc & 0b11111111
            else:
                self.ACC = acc
                
        elif self.instruction == 0x0009:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba]
            if acc >> 8:
                self.CF = acc >> 8
                self.ACC = acc & 0b11111111
            else:
                self.ACC = acc
                
        elif self.instruction == 0x000A:
            ...
            
        self.step()
        
            
                  
    
class EmulatorPyxel:
    ...