# -- Initial --
rarb 214    # Mat Addr
acc 14
to-mba

rcrd 16     # Seg1 (Tail)
from-reg 0  # Mat Addr 1/2
to-mdc
rcrd 17
from-reg 1  # Mat Addr 2/2
to-mdc
acc 2       # 0100 Segment
rcrd 18
to-mdc

rcrd 16     # Store Addr of Tail
rarb 7
from-reg 2
to-mba
rarb 8
from-reg 3
to-mba

rarb 214    # Mat Addr

rcrd 19     # Seg2 (Middle)
from-reg 0  # Mat Addr 1/2
to-mdc
rcrd 20
from-reg 1  # Mat Addr 2/2
to-mdc
rcrd 21
acc 4       # 0010 Segment
to-mdc

rcrd 22     # Seg3 (Head)
from-reg 0  # Mat Addr 1/2
to-mdc
rcrd 23
from-reg 1  # Mat Addr 2/2
to-mdc
rcrd 24
acc 8       # 0001 Segment
to-mdc

rcrd 22     # Store Addr of Head
rarb 5
from-reg 2
to-mba
rarb 6
from-reg 3
to-mba

acc 8       # Set initial direction to right
rarb 1
to-mba

# -- Game Loop --
game_loop:
# Apple Spawn
# Input
from-ioa
rarb 0
to-mba
bnez check_up
rarb 1
from-mba
rarb 0
to-mba


# Direction Checks
check_up:
rarb 0
from-mba
and 1
bnez move_up

check_down:
rarb 0
from-mba
and 2
bnez move_down

check_left:
rarb 0
from-mba
and 4
bnez move_left

check_right:
rarb 0
from-mba
and 8
bnez move_right


# Movement
move_up:
b game_loop

move_down:
b game_loop

move_left:
b game_loop

move_right:
call retrieve_head
# Check if pixel is on rightmost of column set
call check_right_pixel  # Moves to next address of matrix if on edge

# Add New Head Pixel
from-reg 4
rot-l
or*-mba
to-reg 4

# Add New Head Address to Deque
call next_address_dc    # Get the address +1 of head
from-reg 0              # 1/2 addr of led matrix
to-mdc                  # Store in new head 1/2 addr
from-reg 1              
rarb 9
to-mba                  # Temp store 2/2 led matrix addr to mem[9]
rarb 5                  # Mem index of 1/2 head pointer
from-reg 2              # Current 1/2 head addr
to-mba                  # Store
rarb 6
from-reg 3
to-mba
from-mdc
to-reg 0
call next_address_dc    
rarb 9
from-mba                # Retrieve temp stored 2/2 led matrix RE
to-mdc                  # Store in 2/2 head addr
to-reg 1
call next_address_dc
from-reg 4
to-mdc

b game_loop

# -- FUNCTIONS --
retrieve_head:
# Output = Head Address: RA&RB, Segment: RE

# Get 1/2 address of head to RC&RD
rarb 5
from-mba
to-reg 2
rarb 6
from-mba
to-reg 3
from-mdc
to-reg 0    # Store 1/2 Address to A

# Get 2/2 address of head to RC&RD
from-reg 2
sub 15
beqz inc_2nd
inc*-reg 2
bnez retrieve_head_skip_1
# If Overflow
inc_2nd:
inc*-reg 2
inc*-reg 3
retrieve_head_skip_1:
from-mdc
to-reg 1    # Store 2/2 Address to B

# Get Segment Value to RE
from-reg 2
sub 15
beqz inc_2nd
inc*-reg 2
bnez retrieve_head_skip_2
# If Overflow
inc_2nd:
inc*-reg 2
inc*-reg 3
retrieve_head_skip_2:
from-mdc
to-reg 4    # Store val to E
ret
# ------------


check_right_pixel:
# Input: Segment: RE
# Output: Head Address: 
from-reg 4
and 8

bnez col_right
ret

col_right:
from-reg 0
sub 15
beqz inc_2nd_mem
inc*-reg 0
ret


inc_2nd_mem:
inc*-reg 0
inc*-reg 1
ret
# ------------


# -- Copy Pasta Function Subparts -- (Used for building functions)

get_head_add:   
# Output = Head Address: RC & RD

rarb 5
from-mba
to-reg 2
rarb 6
from-mba
to-reg 3
ret
# ------------


get_tail_add:
rarb 7
from-mba
to-reg 2
rarb 8
from-mba
to-reg 3
ret
# ------------


next_address_dc:   
# Input = Head/Tail Address RC&RD
# Output = Head/Tail Address RC&RD

from-reg 3
sub 3
bnez next_address_resume_dc
from-reg 2
sub 4
beqz reset_deque_dc

next_address_resume_dc:
from-reg 2
sub 15
inc*-reg 2
bnez next_address_skip_dc
inc*-reg 3
next_address_skip_dc:
ret

reset_deque_dc:
acc 15
to-reg 2
acc 0
to-reg 3
b next_address_resume_dc
# ------------