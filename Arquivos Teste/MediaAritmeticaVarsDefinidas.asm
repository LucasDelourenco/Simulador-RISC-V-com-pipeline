.data
Num: .asciz "Insira o numero de notas: "
Nota: .asciz "Insira as notas:\n"
Media: .asciz "\nMédia: "

.text
li s0,3
li t0,0
li a1,0
for:
bge t0,s0,endfor
li a0,7
add a1,a1,a0
addi t0,t0,1
j for
endfor:
div a0,a1,s0
