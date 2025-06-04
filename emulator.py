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
        # rot-r
        self.instruction = self.instructions[self.PC]
        if self.instruction == 0x00:
            self.ACC = (self.ACC << 3 & 0x0F) | (self.ACC >> 1)
        
        # rot-l
        elif self.instruction == 0x01:
            self.ACC = (self.ACC >> 3) | (self.ACC << 1 & 0x0F)
        
        # rot-rc
        elif self.instruction == 0x02:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc << 4 & 0x1F) | (cfacc >> 1)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0x0F
        
        # rot-lc
        elif self.instruction == 0x03:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc >> 4) | (cfacc << 1 & 0x1F)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0x0F
            
        elif self.instruction == 0x04:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.memory[ba]
            
        elif self.instruction == 0x05:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC
            
        elif self.instruction == 0x06:
            dc = (self.RD << 4) | self.RC
            self.ACC = self.memory[dc]   
            
        elif self.instruction == 0x07:
            dc = (self.RD << 4) | self.RC
            self.memory[dc] = self.memory[dc]
            
        elif self.instruction == 0x08:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba] + self.CF
            if acc >> 8:
                self.CF = acc >> 8
                self.ACC = acc & 0b11111111
            else:
                self.ACC = acc
                
        elif self.instruction == 0x09:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba]
            if acc >> 8:
                self.CF = acc >> 8
                self.ACC = acc & 0b11111111
            else:
                self.ACC = acc
                
        elif self.instruction == 0x0A:
            ...
            
        self.step()
        
            
                  
    
class EmulatorPyxel:
    ...
    
    
test = Arch242Emulator([0x03])
test.CF = 0b0
test.ACC = 0b1000

test.execute()

print()
print(test.CF)
print(test.ACC)