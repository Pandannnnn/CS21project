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
        
        self.REG = {
            0 : self.RA,
            1 : self.RB,
            2 : self.RC,
            3 : self.RD,
            4 : self.RE
        }
    
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
        instruction = self.instructions[self.PC]
        
        # SIMPLE OPERATIONS (check for 4 leftmost bits == 0b0000)
        # rot-r
        if instruction == 0x00:
            self.ACC = (self.ACC << 3 & 0x0F) | (self.ACC >> 1)
        
        # rot-l
        elif instruction == 0x01:
            self.ACC = (self.ACC >> 3) | (self.ACC << 1 & 0x0F)
        
        # rot-rc
        elif instruction == 0x02:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc << 4 & 0x1F) | (cfacc >> 1)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0x0F
        
        # rot-lc
        elif instruction == 0x03:
            cfacc = (self.CF << 4) | self.ACC
            cfacc = (cfacc >> 4) | (cfacc << 1 & 0x1F)
            self.CF = cfacc >> 4
            self.ACC = cfacc & 0x0F
        
        # from-mba
        elif instruction == 0x04:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.memory[ba]
        
        # to-mba
        elif instruction == 0x05:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC
            
        # from-mdc
        elif instruction == 0x06:
            dc = (self.RD << 4) | self.RC
            self.ACC = self.memory[dc]   
        
        # to-mdc
        elif instruction == 0x07:
            dc = (self.RD << 4) | self.RC
            self.memory[dc] = self.memory[dc]
        
        # addc-mba
        elif instruction == 0x08:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba] + self.CF
            if acc >> 4:
                self.CF = acc >> 4 & 0x01
                self.ACC = acc & 0x0F
            else:
                self.ACC = acc
        
        # add-mba   
        elif instruction == 0x09:
            ba = (self.RB << 4) | self.RA
            acc = self.ACC + self.memory[ba]
            if acc >> 4:
                self.CF = acc >> 4
                self.ACC = acc & 0x0F
            else:
                self.ACC = acc
        
        # subc-mba
        elif instruction == 0x0A:
            ba = (self.RB << 4) | self.RA
            val = self.ACC - self.memory[ba] + self.CF
            if val < 0:
                self.CF = 1
            self.ACC = val
            
        # sub-mba
        elif instruction == 0x0B:
            ba = (self.RB << 4) | self.RA
            val = self.ACC - self.memory[ba]
            if val < 0:
                self.CF = 1
            self.ACC = val
            
        # inc*-mba
        elif instruction == 0x0C:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] += 1
            
        # dec*-mba
        elif instruction == 0x0D:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] -= 1
            
        # inc*-mdc
        elif instruction == 0x0E:
            dc = (self.RD << 4) | self.RC
            self.memory[dc] += 1
            
        # dec*-mdc
        elif instruction == 0x0F:
            dc = (self.RD << 4) | self.RC
            self.memory[dc] -= 1


        # REG INSTRUCTIONS (check 4 leftmost == 0b0001 and bits 2-4 <= 4 (4 registers))
        # inc*-reg
        elif (instruction >> 4 == 0x1) and (instruction & 0x01 == 0b0) and (instruction & 0x0E >> 1 <= 4):
            reg = instruction & 0x0E >> 1
            if 0 <= reg <= 4:
                self.REG[reg] += 1
                
        # dec*-reg
        elif (instruction >> 4 == 0x1) and (instruction & 0x01 == 0b1) and (instruction & 0x0E >> 1 <= 4):
            reg = instruction & 0x0E >> 1
            if 0 <= reg <= 4:
                self.REG[reg] -= 1
                

        # LOGICAL OPERATIONS (check 4 leftmost == 0b0001)
        # and-ba
        elif instruction == 0x1A:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.ACC & self.memory[ba]
            
        # xor-ba
        elif instruction == 0x1B:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.ACC ^ self.memory[ba]
        
        # or-ba
        elif instruction == 0x1C:
            ba = (self.RB << 4) | self.RA
            self.ACC = self.ACC | self.memory[ba]
            
        # and*-mba
        elif instruction == 0x1D:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC & self.memory[ba]
            
        # xor*-mba
        elif instruction == 0x1E:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC ^ self.memory[ba]
            
        # or*-mba
        elif instruction == 0x1F:
            ba = (self.RB << 4) | self.RA
            self.memory[ba] = self.ACC | self.memory[ba]
        
        
        # REG to/from ACC OPERATION (4 leftmost == 0b0010 and bits 2-4 >= 4)
        # to-reg
        elif (instruction >> 4 == 0b0010) and (instruction & 0x01 == 0) and (instruction & 0x0E >> 1 <= 4):
            reg = instruction & 0x0E >> 1
            self.REG[reg] = self.ACC
            
        # from-reg
        elif (instruction >> 4 == 0b0010) and (instruction & 0x01 == 1) and (instruction & 0x0E >> 1 <= 4):
            reg = instruction & 0x0E >> 1
            self.ACC = self.REG[reg]
            
            
        self.step()
        
            
                  
    
class EmulatorPyxel:
    ...
    

# Testing Grounds

test = Arch242Emulator([0x0A])
test.CF = 0b0
test.ACC = 0x1
test.RA = 0x0
test.RB = 0x1
test.memory[0x01] = 0
test.memory[0x10] = 2

test.execute()

print()
print(bin(test.ACC))
print(test.ACC)
print(test.ACC & 0x0F)
print(test.CF)