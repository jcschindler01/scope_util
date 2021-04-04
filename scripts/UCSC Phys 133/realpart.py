import numpy as np
import matplotlib.pyplot as plt
import scope_utilities.vector_impedance_meter as vm


directory = "./"
filename = "001.dat"

dd = vm.dd(filename=filename, directory=directory)

f = dd['f']
magZ = dd['magZ']
argZ = dd['argZ']

reZ = magZ * np.cos( np.pi * argZ / 180. )


plt.figure(1,figsize=(6,6))
## plot
plt.plot(f,reZ,ls='none', marker='.',color='k')
## format
plt.title('Impedance: Real Part vs. Frequency')
plt.xlabel('frequency (kHz)'), plt.ylabel('Re(z) (kOhm)')
plt.grid()
plt.gca().set_xscale("log", nonposx='clip') 
# plt.gca().set_yscale("log", nonposy='clip')
## save
pathname  = directory + 'realpart.pdf'
plt.savefig(pathname,bbox_inches='tight',dpi=600)


plt.show()