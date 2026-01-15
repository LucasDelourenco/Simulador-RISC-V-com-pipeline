.text
li a0,3
li a1,5
li a2,2
li a3,1
add t0,a0,a1
add t1,a2,a3
sub a4,t0,t1
li a2,1
li a3,0
li t0,3
sum:
bgt a2,t0,fim
add a3,a3,a2
addi a2,a2,1
j sum
fim:
