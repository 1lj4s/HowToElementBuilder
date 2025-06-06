simulator lang=local

global 0

NPORT0 1 0 2 0 3 0 4 0 nport file="C:\Users\USER_BASIC\YandexDisk\Work\CAD\Sprints\21.05-4.06\Mod_Sim\Netlist\SNP\ind_4n0.s4p"

PORT0 1 0 port r=50 num=1 type=sine rptstart=1 rpttimes=0
PORT1 2 0 port r=50 num=2 type=sine rptstart=1 rpttimes=0
PORT2 3 0 port r=50 num=3 type=sine rptstart=1 rpttimes=0
PORT3 4 0 port r=50 num=4 type=sine rptstart=1 rpttimes=0

SPSweep sp start=1 stop=20G step=10000 file="C:\Users\USER_BASIC\YandexDisk\Work\CAD\Sprints\21.05-4.06\Mod_Sim\Out_SimSpice\output_file_name.s4p"

DEFAULT_OPTIONS options tnom=27 temp=27 reltol=1.000000e-03
DEFAULT_OPTIONS options tnom=27 temp=27 reltol=1.000000e-03