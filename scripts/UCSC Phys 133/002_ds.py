import numpy as np
from numpy.polynomial.polynomial import polyval
import matplotlib.pyplot as plt
import vector_impedance_meter as vm

datafile = "002.dat"
dd = vm.dd(datafile)

### load variables
f = dd['f']
magZ, argZ, reZ, imZ = dd['magZ'], dd['argZ'], dd['reZ'], dd['imZ']

V1, V2, phi = dd['V1'], dd['V2'], dd['phi']
Rtest, navg, ntrials = dd['Rtest'], dd['navg'], dd['ntrials']
sigma_f, sigma_magZ, sigma_argZ = dd['sigma_f'], dd['sigma_magZ'], dd['sigma_argZ']
sigma_V1, sigma_V2, sigma_phi = dd['sigma_V1'], dd['sigma_V2'], dd['sigma_phi']



### create model

## quick linear fit for approximate L
slope, intercept = np.polyfit((f[:-5])**2,(magZ[:-5])**2,1)
L = np.sqrt(slope) / (2.*np.pi)
# print L0

#R = 110.         #Ohms
#L = 10.5e-3       #Henries


# ## quick quadratic fit for R(f)
# polycoeffs = np.polyfit(f,reZ,2)[::-1]
# print "polycoeffs (intercept first) =\n%s"%(polycoeffs)
# def R(ff):
# 	return polyval(ff,polycoeffs)

## quick exponential fit for R(f)
intercept, slope = np.polyfit(f,np.log(reZ),1)[::-1]
Rdc, fac = np.exp(intercept), 1./slope
print "expcoeffs (Rdc, fac) =\n(%s, %s)"%(Rdc, fac)
def R(ff):
	return Rdc * np.exp( ff / fac)

def z_mod(ff,L):
	w = 2.*np.pi*ff
	z = R(ff) + 1j*w*L
	return z

ff = np.linspace(1e-1,100,10000) * 1e3
Zth = z_mod(ff,L)
magZth = np.abs(Zth)
argZth = np.arctan(Zth.imag/Zth.real) * 180. / np.pi
reZth = magZth * np.cos(np.pi*argZth/180.)


## magnitude
fig1 = plt.figure(1,figsize=(6,6))
ax1  = plt.subplot(111)
## plot data and model
plt.errorbar(x = (f/1000.)**1, y = (magZ/1000.)**1, xerr = sigma_f/1000., yerr = sigma_magZ/1000., ls='none', marker='.',color='k',zorder=20)
plt.plot((ff/1000.)**1,(magZth/1000.)**1,'k-')
## format
plt.title('Impedance: Magnitude vs Frequency')
plt.xlabel('frequency (kHz)'), plt.ylabel('|z| (kOhm)')
plt.grid()
ax1.set_xscale("log", nonposx='clip')
ax1.set_yscale("log", nonposy='clip') 


## phase
fig2 = plt.figure(2,figsize=(6,6))
ax2  = plt.subplot(111)
## plot data and model
plt.errorbar(x = f/1000., y = argZ, xerr = sigma_f/1000., yerr = sigma_argZ, ls='none', marker='.',color='k')
plt.plot(ff/1000.,argZth,'k-',zorder=10)
## format
plt.title('Impedance: Phase vs Frequency')
plt.xlabel('frequency (kHz)'), plt.ylabel('Arg(z) (degree)')
plt.ylim(-95,95), plt.grid()
plt.yticks([-90,-45,0,45,90])
ax2.set_xscale("log", nonposx='clip')


## real part
fig3 = plt.figure(3,figsize=(6,6))
ax3  = plt.subplot(111)
## plot data and model
plt.errorbar(x = f/1000., y = reZ/1000., ls='none', marker='.',color='k')
plt.plot(ff/1000.,reZth/1000.,'k-',zorder=10)
## format
plt.title('Re(z) vs Frequency')
plt.xlabel('frequency (kHz)'), plt.ylabel('Re(z) (kOhms)')
plt.grid(), 
#plt.ylim(0,.6)
ax3.set_xscale("log", nonposx='clip')
ax3.set_yscale("log", nonposy='clip') 



## save plots
fig1file = '002_ds_fig1.pdf'
fig2file = '002_ds_fig2.pdf'
fig3file = '002_ds_fig3.pdf'
fig1.savefig(fig1file, bbox_inches='tight', dpi=600)
fig2.savefig(fig2file, bbox_inches='tight', dpi=600)
fig3.savefig(fig3file, bbox_inches='tight', dpi=600)


## show plots
plt.show()




