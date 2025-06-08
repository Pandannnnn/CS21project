import sys
class Arch242Assembler:
    def __init__(self) -> None:
        self.instruction_set= {
        "rot-r": [0x00],
        "rot-l": [0x01],
        "rot-rc": [0x02],
        "rot-lc": [0x03],
        "from-mba": [0x04],
        "to-mba": [0x05],
        "from-mdc": [0x06],
        "to-mdc": [0x07],
        "addc-mba": [0x08],
        "add-mba": [0x09],
        "subc-mba": [0x0A],
        "sub-mba": [0x0B],
        "inc*-mba": [0x0C],
        "dec*-mba": [0x0D],
        "inc*-mdc": [0x0E],
        "dec*-mdc": [0x0F],

        #Register stuff (0-7)
        "inc*-reg":lambda r:[0x10|r<<1],
        "dec*-reg":lambda r:[0x11|r<<1],
        "to-reg":lambda r:[0x20|r<<1],
        "from-reg":lambda r:[0x21|r<<1],
        
        "and-ba": [0x1A],
        "xor-ba": [0x1B],
        "or-ba": [0x1C],
        "and*-mba": [0x1D],
        "xor*-mba": [0x1E],
        "or*-mba": [0x1F],


        "clr-cf": [0x2A],
        "set-cf": [0x2B],
        "ret": [0x2E],
        "inc": [0x31],
        "from-ioa": [0x32],
        "bcd": [0x36],
        "shutdown": [0x37, 0x3E],
        "nop": [0x3E],
        "dec": [0x3F],

        #inst with immediate  (0-15 lang pwede)
        "add": lambda r: [0x40, r&0x0F],
        "sub": lambda r: [0x41, r&0x0F],
        "and": lambda r: [0x42, r&0x0F],
        "xor": lambda r: [0x43, r&0x0F],
        "or": lambda r: [0x44, r&0x0F],
        "r4": lambda r: [0x46, r&0x0F],
        "acc":lambda r:[0x70|r&0x0F],


        #imm (0-255)
        "rarb":lambda r:[0x50|(r&0x0F),r>>4 &0x0F],
        "rcrd":lambda r:[0x60|(r&0x0F),r>>4 &0x0F],
        
        #imm(0-2047)
        "b-bit":lambda k,r:[0x80|k<<3|(r>>8&0x07),r&0xFF], #k (0-3)
        "bnz-a":lambda r:[0xA0|(r>>8 &0x07),r&0xFF],
        "bnz-b":lambda r:[0xA8|(r>>8 &0x07),r&0xFF],
        "beqz":lambda r:[0xB0|(r>>8 &0x07),r&0xFF],
        "bnez":lambda r:[0xB8|(r>>8 &0x07),r&0xFF],
        "beqz-cf":lambda r:[0xC0|(r>>8 &0x07),r&0xFF],
        "bnez-cf":lambda r:[0xC8|(r>>8 &0x07),r&0xFF],
        "bnz-d":lambda r:[0xD8|(r>>8 &0x07),r&0xFF],

        #imm(0-4095)
        "b":lambda r:[0xE0|(r>>8 &0x0F),r&0xFF],
        "call":lambda r:[0xF0|(r>>8 &0x0F),r&0xFF],

        #byte
        ".byte":lambda r:[r]
        }
    def is_label(self,length,instruction):
        if length==1 and instruction[-1]==":":
            return True
        return False
    def get_labels(self,filename,format):
        current_pc=0x0000
        label={}

        register_instructions=["inc*-reg","dec*-reg","to-reg","from-reg"]
        imm_4bits=["add","sub","and","xor","or","r4","acc"]
        imm_8bits=["rarb","rcrd"]
        imm_11bits=["b-bit","bnz-a","bnz-b","beqz","bnez","beqz-cf","bnez-cf","bnz-d"]
        imm_12bits=["b","call"]

        if not filename.endswith('.asm'):
            raise ValueError("Input File must have an .asm extension")
        if format not in ["bin","hex"]:
            raise ValueError("Invalid Format!")
        
        with open (filename,"r") as f:
            for idx,line in enumerate(f):
                comment=line.find("#")
                if comment!=-1:
                    instruction_line=line[:comment].strip().split()
                else:instruction_line=line.strip().split()
                try:
                    length=len(instruction_line)
                    if not length:
                        continue
                    instruction=instruction_line[0]
                    if self.is_label(length,instruction): #if label
                        label[instruction[:-1]]=current_pc #remove : character
                    elif instruction not in self.instruction_set:
                        continue
                    elif not callable(self.instruction_set[instruction]) and length==1 and instruction!=".byte": 
                        #encoding.extend(self.instruction_set[instruction])
                        current_pc+=len(self.instruction_set[instruction])
                    
                    elif instruction==".byte":
                        if length!=2:
                            raise ValueError("Instruction not valid! Line {}".format(idx))
                        immediate=instruction_line[1].lower()
                        if immediate[:2]=="0x":
                            immediate=int(immediate,16)
                        else:
                            immediate=int(immediate)
                        assert 0<=immediate<=255,"immediate should be between 0-255"
                        #encoding.extend(self.instruction_set[instruction](immediate))
                        current_pc+=len(self.instruction_set[instruction](immediate))

                    else:

                        if instruction in register_instructions: #0-3
                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            assert 0<=immediate<=4 ,"immediate should be between 0-4"
                            #encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))


                        elif instruction in imm_4bits:

                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            assert 0<=immediate<=15,"immediate should be between 0-15"
                            #encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))


                        elif instruction in imm_8bits:
                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                           
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            
                            assert 0<=immediate<=255,"immediate should be between 0-255"
                            
                            #encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))
                        elif instruction in imm_11bits:
                            current_pc+=2
                        elif instruction in imm_12bits:
                            current_pc+=2
                        else:
                            raise ValueError("Instruction not valid! Line {}".format(idx))
                
                except:
                    raise ValueError("Instruction not valid! Line {}".format(idx))
        return label
    def parse_asmfile(self,filename,format):
        current_pc=0x0000
        encoding=[]
        label=self.get_labels(filename,format)

        register_instructions=["inc*-reg","dec*-reg","to-reg","from-reg"]
        imm_4bits=["add","sub","and","xor","or","r4","acc"]
        imm_8bits=["rarb","rcrd"]
        imm_11bits=["b-bit","bnz-a","bnz-b","beqz","bnez","beqz-cf","bnez-cf","b-timer","bnz-d"]
        imm_12bits=["b","call"]
        
        if not filename.endswith('.asm'):
            raise ValueError("Input File must have an .asm extension")
        if format not in ["bin","hex"]:
            raise ValueError("Invalid Format!")
        
        with open (filename,"r") as f:
            for idx,line in enumerate(f):
                comment=line.find("#")
                if comment!=-1:
                    instruction_line=line[:comment].strip().split()
                else:instruction_line=line.strip().split()
                try:
                    length=len(instruction_line)
                    if not length:
                        continue
                    instruction=instruction_line[0]
                    if instruction not in self.instruction_set:
                        continue 
                    elif not callable(self.instruction_set[instruction]) and length==1 and instruction!=".byte": 
                        encoding.extend(self.instruction_set[instruction])
                        current_pc+=len(self.instruction_set[instruction])
                    
                    elif instruction==".byte":
                        if length!=2:
                            raise ValueError("Instruction not valid! Line {}".format(idx))
                        immediate=instruction_line[1].lower()
                        if immediate[:2]=="0x":
                            immediate=int(immediate,16)
                        else:
                            immediate=int(immediate)
                        assert 0<=immediate<=255,"immediate should be between 0-255"
                        encoding.extend(self.instruction_set[instruction](immediate))
                        current_pc+=len(self.instruction_set[instruction](immediate))

                    else:

                        if instruction in register_instructions: #0-3
                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            assert 0<=immediate<=4 ,"immediate should be between 0-4"
                            encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))


                        elif instruction in imm_4bits:

                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            assert 0<=immediate<=15,"immediate should be between 0-15"
                            encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))


                        elif instruction in imm_8bits:
                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1].lower()
                           
                            if immediate[:2]=="0x":
                                immediate=int(immediate,16)
                            else:
                                immediate=int(immediate)
                            
                            assert 0<=immediate<=255,"immediate should be between 0-255"
                            
                            encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))

                        elif instruction in imm_11bits:
                            if length==3 and instruction=="b-bit":#b-bit
                                k,immediate=instruction_line[1],instruction_line[2].lower()
                                k=int(k)
                                immediate=instruction_line[1]
                                if immediate in label:
                                    immediate=label[immediate]
                                
                                else:
                                    immediate=immediate.lower()
                                    if immediate[:2]=="0x":
                                        immediate=int(immediate,16)
                                    else:
                                        immediate=int(immediate)
                                assert 0<=k<=3,"k should be between 0-3"
                                assert 0<=immediate<=2047,"immediate should be between 0-2047"
                                encoding.extend(self.instruction_set[instruction](k,immediate))
                                current_pc+=len(self.instruction_set[instruction](k,immediate))

                            elif length==2:
                                immediate=instruction_line[1]
                                if immediate in label:
                                    immediate=label[immediate]
                                else:
                                    immediate=immediate.lower()
                                    if immediate[:2]=="0x":
                                        immediate=int(immediate,16)
                                    else:
                                        immediate=int(immediate)
                                assert 0<=immediate<=2047,"immediate should be between 0-2047"
                                encoding.extend(self.instruction_set[instruction](immediate))
                                current_pc+=len(self.instruction_set[instruction](immediate))

                            else:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                        elif instruction in imm_12bits:
                            if length!=2:
                                raise ValueError("Instruction not valid! Line {}".format(idx))
                            immediate=instruction_line[1]
                            if immediate in label:
                                immediate=label[immediate]
                            else:
                                immediate=immediate.lower()
                                if immediate[:2]=="0x":
                                    immediate=int(immediate,16)
                                else:
                                    immediate=int(immediate)
                            assert 0<=immediate<=4095,"immediate should be between 0-4095"
                            encoding.extend(self.instruction_set[instruction](immediate))
                            current_pc+=len(self.instruction_set[instruction](immediate))

                        else:
                            raise ValueError("Instruction not valid! Line {}".format(idx))
                
                except:
                    raise ValueError("Instruction not valid! Line {}".format(idx))
                
        with open("output.txt","w") as output:
            if format=="bin":
                for bits in encoding:
                    output.write(f"{bits:08b}\n")
            else:
                output.write("v3.0 hex words\n")
                for bits in encoding:
                    output.write(f"{bits:04x}\n")
        
        
