.text
li t0,5
li s0,0
sw t0,0(s0)
addi t0,t0,1
sw t0,4(s0)
lw t1,0(s0)
lw t2,4(s0)