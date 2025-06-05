import pyxel,sys
from assembler import Arch242Assembler
from collections import deque


class Arch242Emulator:
    def __init__(self, instructions: list[int]):
        self.PC = 0x0000
        
        # Memory
        self.memory = [0] * 256
        
        # Registers
        self.RA = self.RB = self.RC = self.RD = self.RE = 0x0
        self.ACC = 0x0
        self.CF = 0b0
        self.TEMP = 0
        self.IOA = 0x0
        
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
        print(self.PC)
        
        # REG INSTRUCTIONS (check 4 leftmost == 0b0001 and bits 2-4 <= 4 (4 registers))
        if ((instruction >> 4) == 0x01) and (((instruction & 0x0E) >> 1) <= 4):
            # inc*-reg
            if (instruction & 0x01) == 0b0:
                reg = (instruction & 0x0E) >> 1
                if 0 <= reg <= 4:
                    if reg == 0: self.RA += 1
                    elif reg == 1: self.RB += 1
                    elif reg == 2: self.RC += 1
                    elif reg == 3: self.RD += 1
                    elif reg == 4: self.RE += 1
            
            # dec*-reg
            elif (instruction & 0x01) == 0b1:
                reg = (instruction & 0x0E) >> 1
                if 0 <= reg <= 4:
                    if reg == 0: self.RA -= 1
                    elif reg == 1: self.RB -= 1
                    elif reg == 2: self.RC -= 1
                    elif reg == 3: self.RD -= 1
                    elif reg == 4: self.RE -= 1    
                    
            self.step()           


        # REG to/from ACC INSTRUCTIONS (4 leftmost == 0b0010 and bits 2-4 <= 4)
        elif ((instruction >> 4) == 0b0010) and (((instruction & 0x0E) >> 1) <= 4):
            # to-reg
            if ((instruction & 0x01) == 0):
                reg = (instruction & 0x0E) >> 1
                if reg == 0: self.RA = self.ACC
                elif reg == 1: self.RB = self.ACC
                elif reg == 2: self.RC = self.ACC
                elif reg == 3: self.RD = self.ACC
                elif reg == 4: self.RE = self.ACC
            
            # from-reg
            elif ((instruction & 0x01) == 1):
                reg = (instruction & 0x0E) >> 1
                if reg == 0: self.ACC = self.RA
                elif reg == 1: self.ACC = self.RB
                elif reg == 2: self.ACC = self.RC
                elif reg == 3: self.ACC = self.RD
                elif reg == 4: self.ACC = self.RE
                
            self.step()


        # IMMEDIATE OPERATIONS
        elif 0x40 <= instruction <= 0x46:
            # add
            if instruction==0x40:
                immediate=self.instructions[self.PC+1]
                self.ACC+=immediate
            
            # sub
            elif instruction==0x41:
                immediate=self.instructions[self.PC+1]
                self.ACC-=immediate
            
            # and
            elif instruction==0x42:
                immediate=self.instructions[self.PC+1]
                self.ACC&=immediate

            # xor
            elif instruction==0x43:
                immediate=self.instructions[self.PC+1]
                self.ACC^=immediate
            
            # or
            elif instruction==0x44:
                immediate=self.instructions[self.PC+1]
                self.ACC|=immediate

            # r4
            elif instruction==0x46:
                immediate=self.instructions[self.PC+1]
                self.RE=immediate
                
            self.step()


        # IMMEDIATE ASSIGNMENT
        elif (0b0101 <= instruction>>4 <= 0b0111):
            # rarb 
            if (instruction>>4==0b0101):
                ra_immediate=instruction&0x0F
                rb_immediate=self.instructions[self.PC+1]
                self.RA=ra_immediate
                self.RB=rb_immediate
            
            # rcrd 
            elif (instruction>>4==0b0110):
                rc_immediate=instruction&0x0F
                rd_immediate=self.instructions[self.PC+1]
                self.RC=rc_immediate
                self.RD=rd_immediate
            
            #acc
            elif (instruction>>4==0b0111):
                immediate=instruction&0x0F
                self.ACC=immediate
                
            self.step()
        
        
        #b-bit  
        elif(instruction>>5==0b100):
            k=(instruction>>3) & 0x03
            immediate= (instruction&0x07)<<8|self.instructions[self.PC+1]
            if self.ACC>>k:
                self.PC=(self.PC&0xF800)|immediate
            else:
                self.step()
        
        
        # IMMEDIATE BRANCH INSTRUCTIONS
        elif 0b10100 <= instruction>>3 <= 0b11011:
            #bnz-a
            if(instruction>>3==0b10100):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.RA!=0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #bnz-B
            elif(instruction>>3==0b10101):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.RB!=0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #beqz
            elif(instruction>>3==0b10110):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.ACC==0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #bnez
            elif(instruction>>3==0b10111):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.ACC!=0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #beqz-cf
            elif(instruction>>3==0b11000):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.CF==0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #beqz-cf
            elif(instruction>>3==0b11001):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.CF!=0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
            
            #bnz-d
            elif(instruction>>3==0b11011):
                immediate= ((instruction&0x07)<<8)|self.instructions[self.PC+1]
                if self.RD!=0:
                    self.PC=(self.PC&0xF800)|immediate
                else:
                    self.step()
        
        #b
        elif(instruction>>4==0b1110):
            immediate= ((instruction&0x0F)<<8)|self.instructions[self.PC+1]
            self.PC=(self.PC&0xF000)|immediate
        
        #call
        elif(instruction>>4==0b1111):
            self.TEMP = self.PC + 2
            immediate= ((instruction&0x0F)<<8)|self.instructions[self.PC+1]
            self.PC=(self.PC&0xF000)|immediate
            
        
        # SIMPLE OPERATIONS (check for 4 leftmost bits == 0b0000)
        elif 0x00 <= instruction <= 0x0F:
            # rot-r
            if instruction == 0x00:
                self.ACC = ((self.ACC << 3) & 0x0F) | (self.ACC >> 1)
            
            # rot-l
            elif instruction == 0x01:
                self.ACC = (self.ACC >> 3) | ((self.ACC << 1) & 0x0F)
            
            # rot-rc
            elif instruction == 0x02:
                cfacc = (self.CF << 4) | self.ACC
                cfacc = ((cfacc << 4) & 0x1F) | (cfacc >> 1)
                self.CF = cfacc >> 4
                self.ACC = cfacc & 0x0F
            
            # rot-lc
            elif instruction == 0x03:
                cfacc = (self.CF << 4) | self.ACC
                cfacc = (cfacc >> 4) | ((cfacc << 1) & 0x1F)
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
                self.memory[dc] = self.ACC
            
            # addc-mba
            elif instruction == 0x08:
                ba = (self.RB << 4) | self.RA
                acc = self.ACC + self.memory[ba] + self.CF
                if acc >> 4:
                    self.CF = (acc >> 4) & 0x01
                    self.ACC = acc & 0x0F
                else:
                    self.ACC = acc
            
            # add-mba   
            elif instruction == 0x09:
                ba = (self.RB << 4) | self.RA
                acc = self.ACC + self.memory[ba]
                if acc >> 4:
                    self.CF = (acc >> 4) & 0x01
                    self.ACC = acc & 0x0F
                else:
                    self.ACC = acc
            
            # subc-mba
            elif instruction == 0x0A:
                ba = (self.RB << 4) | self.RA
                val = self.ACC - self.memory[ba] + self.CF
                if val < 0:
                    self.CF = 1
                self.ACC = val & 0x0F
                
            # sub-mba
            elif instruction == 0x0B:
                ba = (self.RB << 4) | self.RA
                val = self.ACC - self.memory[ba]
                if val < 0:
                    self.CF = 1
                self.ACC = val & 0x0F
                
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
                
            self.step()


        # LOGICAL OPERATIONS (check 4 leftmost == 0b0001)
        elif 0x1A <= instruction <= 0x1F:
            # and-ba
            if instruction == 0x1A:
                ba = (self.RB << 4) | self.RA
                self.ACC &= self.memory[ba]
                
            # xor-ba
            elif instruction == 0x1B:
                ba = (self.RB << 4) | self.RA
                self.ACC ^= self.memory[ba]
            
            # or-ba
            elif instruction == 0x1C:
                ba = (self.RB << 4) | self.RA
                self.ACC |= self.memory[ba]
                
            # and*-mba
            elif instruction == 0x1D:
                ba = (self.RB << 4) | self.RA
                self.memory[ba] &= self.ACC
                
            # xor*-mba
            elif instruction == 0x1E:
                ba = (self.RB << 4) | self.RA
                self.memory[ba] ^= self.ACC
                
            # or*-mba
            elif instruction == 0x1F:
                ba = (self.RB << 4) | self.RA
                self.memory[ba] |= self.ACC
                
            self.step()
        
        
        elif 0x2A <= instruction <= 0x2B:
            # clr-cf    
            if instruction==0x2A:
                self.CF=0
            
            # set-cf
            elif instruction==0x2B:
                self.CF=1
                
            self.step()
            
        # ret
        elif instruction==0x2E:
            self.PC=(self.PC&0xF000)|(self.TEMP&0x0FFF)
            self.TEMP=0
        

        elif 0x32 <= instruction <= 0x3F:
            # from-ioa
            if instruction==0x32:
                self.ACC=self.IOA
                self.step()
                
            # inc
            elif instruction==0x31:
                self.ACC+=1
                self.step()
                
            # bcd
            elif instruction==0x36:
                if self.ACC>=10 or self.CF:
                    self.ACC+=6
                    self.CF=1
                self.step()
                
            # shutdown
            elif instruction==0x37:
                exit()
            
            # nop
            elif instruction==0x3E:
                self.step()
            
            # dec
            elif instruction==0x3F:
                self.ACC-=1
                self.step()
                
      
        #invalid instruction from .byte
        else:
            print("Invalid Instruction!")
            exit()


#############
# Constants #
#############

COL_BACKGROUND = 3
COL_BODY = 11
COL_HEAD = 7
COL_DEATH = 8
COL_APPLE = 8

TEXT_DEATH = ["GAME OVER", "(Q)UIT", "(R)ESTART"]
COL_TEXT_DEATH = 0
HEIGHT_DEATH = 5

HEIGHT_SCORE = pyxel.FONT_HEIGHT
COL_SCORE = 6
COL_SCORE_BACKGROUND = 5

class EmulatorPyxel:
    def __init__(self, instructions):
        self.emulator = Arch242Emulator(instructions)
        
        # LED MATRIX
        self.rows=20
        self.cols=10
        self.start_address = 192
        self.end_address = 241
        self.cell_size = 5
        
        pyxel.init(
            self.cols * self.cell_size, 
            self.rows * self.cell_size, 
            title="Arch-242 Emulator", 
            fps=30, 
            display_scale=12, 
            capture_scale=6
        )
        sound_and_music()
        pyxel.run(self.update, self.draw)
        

    ##############
    # Game logic #
    ##############
        
    def update(self):
        # Input
        self.emulator.IOA = 0b0000
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
          
            self.emulator.IOA |= 0b0001
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.emulator.IOA |= 0b0010
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.emulator.IOA |= 0b0100
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.emulator.IOA |= 0b1000
            
        # Execute and Step Arch242
        self.update_Arch242Cycle()
        
    def update_Arch242Cycle(self):
        try:
            self.emulator.execute()
        except:
            print("Invalid Instruction! / .byte")
            
    

    ##############
    # Draw logic #
    ##############
    
    def draw(self):
        pyxel.cls(0)
        
        for addr in range(self.start_address, self.end_address + 1):
            memory_offset = addr - self.start_address
            led_row = memory_offset // 5
            base_col = led_row * 4
            
            value = self.emulator.memory[addr] & 0x0F
            
            for bit in range(4):
                led_col = base_col + bit
                
                is_on = (value >> bit) & 1
                color = 7 if is_on else 1
                pyxel.rect(
                    led_col * self.cell_size,
                    led_row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                    color
                )
        
        
        
###########################
# Music and sound effects #
###########################

def sound_and_music():
    ...
        


# Testing Grounds
"""
test = Arch242Emulator([0x0A])
test.CF = 0b0
test.ACC = 0x1
test.RA = 0x0
test.RB=0x1
test.memory[0x01] = 0
test.memory[0x10] = 2

test.execute()

print()
print(bin(test.ACC))
print(test.ACC)
print(test.ACC & 0x0F)
print(test.CF)
"""


test2=Arch242Assembler()
args=sys.argv
if len(args)!=2:
    print("Usage: python emulator.py <asmfile>")
_,asmfile=args
test2.parse_asmfile(asmfile,"bin")
instructions=[]
with open("output.txt","r") as f:
    for line in f:
        instructions.append(int(line,2))

emulate=EmulatorPyxel(instructions)

