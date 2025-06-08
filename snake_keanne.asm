# -- Initial --
rarb 214    # Mat Addr

rcrd 16     # Seg1 (Tail)
from-reg 0  # Mat Addr 1/2
to-mdc
rcrd 17
from-reg 1  # Mat Addr 2/2
to-mdc
acc 4       # 0100 Segment
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
acc 2       # 0010 Segment
to-mdc

rcrd 22     # Seg3 (Head)
from-reg 0  # Mat Addr 1/2
to-mdc
rcrd 23
from-reg 1  # Mat Addr 2/2
to-mdc
rcrd 24
acc 1       # 0001 Segment
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
# Get address of head to Reg C and D
call get_head_add
from-mdc
to-reg 0    # Store 1/2 Address to A
call next_address
from-mdc
to-reg 1    # Store 2/2 Address to B
call next_address
from-mdc
to-reg 4    # Store val to E

# Check if pixel is on rightmost of column set
call check_right_pixel

# Get address of 
rarb 0
from-mba
and 1
bnez right_mem


right_mem:


get_head_add:
rarb 5
from-mba
to-reg 2
rarb 6
from-mba
to-reg 3
ret

next_address:
from-reg 2
sub 15
beq inc_2nd
inc*-reg 2
ret

inc_2nd:
inc*-reg 2
inc*-reg 3
ret

check_right_pixel:
from-reg 4
and 1
bnez col_right

col_right:
from-reg 0
sub 15
beq inc_2nd_mem
inc*-reg 

inc_2nd_mem:
inc*-reg 0
inc*-reg 1
ret