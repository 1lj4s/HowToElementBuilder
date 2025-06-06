simulator lang=local
parameters par1=2

include "D:\saves\Pycharm\HowToElementBuilder\Code\Files\cir\sRES.cir"

v1 1 0 vsource type=dc dc=par1
v2 2 0 vsource type=dc dc=par1
v3 3 0 vsource type=dc dc=par1
x1 1 0 sch1
x2 2 0 sch2 par1=5
x3 3 0 sch3

dc dc param=par1 values=[1 10]
opt options rawfmt=nutascii
save v1:p v2:p v3:p