.SUBCKT sch1 1 2 par1=3
r1 1 2 resistor r=par1
.ENDS sch1

.SUBCKT sch2 1 2 par1=4
r1 1 2 resistor r=par1
.ENDS sch2

.SUBCKT sch3 1 2 par1=2
r1 1 2 resistor r=par1**0.5
.ENDS sch3