

import scope_utilities.scope_util as scope
import numpy as np
import matplotlib.pyplot as plt
import os, shutil





def aq_setup(navg=1):
	#scope.reset_all()
	scope.set_aq('avg',navg)
	scope.set_aq('single')


def get_Z(V1,V2,phi,Rtest):
	z = Rtest * V2 / ( V1 * np.exp(-1j*phi) - V2 )
	magZ = np.abs(z)
	argZ = np.arctan(z.imag / z.real)
	return magZ, argZ


def get_data1(params):
	scope.aq1()
	freq = scope.meas_tfreq()
	V1   = scope.meas_rms1() * np.sqrt(2.)
	V2   = scope.meas_rms2() * np.sqrt(2.)
	phi  = scope.meas_phi12()
	## get Z
	Rtest = params['Rtest']
	phi_rad = np.pi * phi / 180.
	magZ, argZ_rad = get_Z(V1,V2,phi_rad,Rtest)
	argZ = 180. * argZ_rad / np.pi
	## return
	datum  = [freq, magZ, argZ, V1, V2, phi]
	return datum

def get_data(params):
	scope.aq1()
	scope.frame()
	ntrials = params['ntrials']
	data = np.zeros((6,ntrials))
	for i in range(ntrials):
		dat = get_data1(params)
		for j in range(6):
			data[j][i] = dat[j]
	return data

def avsig(data):
	av  = np.mean(data,axis=1)
	sig2 =  np.sqrt( np.mean(data**2,axis=1) - av**2 )
	## improved sigma correct DOFs
	ntrials = np.shape(data)[1]
	if ntrials == 1:
		sig = np.zeros(np.shape(data)[0])
	if ntrials >  1:
		diff = get_difference(data)
		sig = np.sqrt( np.sum(diff**2,axis=1) / float(ntrials-1) )
	## return
	return [av, sig]

def get_difference(data):
	av  = np.mean(data,axis=1)
	diff = np.zeros_like(data)
	for i in range(np.shape(diff)[0]):
		for j in range(np.shape(diff)[1]):
			diff[i][j] = data[i][j] - av[i]
	return diff

def datapoint(params):
	datp = avsig(get_data(params))
	return datp

def write_data(DATA,params,header,datafile):
	header0 = header[0:6]
	out0 = [ '%.5e'%(dat) for dat in DATA[0] ]
	header1 = header[6:12]
	out1 = [ '%.5e'%(dat) for dat in DATA[1] ]
	header2 = header[12:15]
	out2 = [ '%.5e'%(params['Rtest']), '%03d'%(params['navg']), '%03d'%(params['ntrials']) ]
	outlist = out0 + out1 + out2
	outlist = stringpad(outlist)
	outstring = ', '.join(outlist)
	datafile.write(outstring + '\n')
	print header0
	print out0
	print header1
	print out1
	print header2
	print out2

def make_header():
	header0 = ['f','magZ','argZ','V1','V2','phi']
	header1 = ['sigma_' + name for name in header0]
	header2 = ['Rtest','navg','ntrials']
	header  = header0 + header1 + header2
	header  = stringpad(header)
	return header 

def make_header2():
	header0 = ['(Hz)','(Ohm)','(degree)','(V)','(V)','(degree)']
	header1 = header0
	header2 = ['(Ohm)','(1)','(1)']
	header  = header0 + header1 + header2
	header  = stringpad(header)
	return header


def stringpad(stringlist):
	length = 12
	return [sl.ljust(length) for sl in stringlist]

def update_params(params):
	instring = raw_input('STOP or NEW Rtest? ')
	if not instring.strip() == '':
		if instring.strip() == 'STOP':
			params.update({'go':False})
		else:
			params.update({'Rtest':float(instring)})
			update_params(params)
	return params

def get_init_params():
	params = {'go':True}
	params.update({'navg':int(raw_input('navg? '))})
	params.update({'ntrials':int(raw_input('ntrials? '))})
	params.update({'Rtest':float(raw_input('Rtest? '))})
	raw_input('GO? ')
	print params
	return params

def get_idno():
	instring = raw_input('ID TAG? ')
	if instring.strip() == '':
		return 'temp'
	else:
		return instring.strip()

def setup_raw_output(savedirec,savepath):
	direcname = savedirec
	pathname  = savepath + '.dat'
	## decide whether to overwrite
	if os.path.exists(pathname):
		go = raw_input('OVERWRITE DIRECTORY? (y/n) ')
		if go == 'y':
			shutil.rmtree(direcname)
		else:
			print 'DO NOT OVERWRITE'
			raise SystemExit
	## continue
	os.mkdir(direcname)
	datafile  = open(pathname,'w')
	return datafile

def get_plotdata(savepath):
	pathname  = savepath + '.dat'
	allDATA   = np.genfromtxt(pathname,delimiter=', ',skip_header=2,unpack=True,autostrip=True)
	f, magZ, argZ = allDATA[0], allDATA[1], allDATA[2]
	sigma_f, sigma_magZ, sigma_argZ = allDATA[6], allDATA[7], allDATA[8]
	print f, magZ, argZ
	print sigma_f, sigma_magZ, sigma_argZ
	return f, magZ, argZ, sigma_f, sigma_magZ, sigma_argZ

def do_experiment(savedirec,savepath):
	## set up output file
	datafile = setup_raw_output(savedirec,savepath)
	header  = make_header()
	header2 = make_header2()
	datafile.write(', '.join(header) +'\n')       ## header = ['f', 'V1', 'V2', 'phi', 'sigma_f', 'sigma_V1', 'sigma_V2', 'sigma_phi', 'Rtest', 'navg', 'ntrials']
	datafile.write(', '.join(header2) +'\n')
	## begin experiment
	params = get_init_params()
	aq_setup(params['navg'])
	while params['go'] == True:
		DATA = datapoint(params)   ## DATA = [ [freq, V1, V2, phi], [sigma_freq, sigma_V1, sigma_V2, sigma_phi] ]
		write_data(DATA,params,header,datafile)
		params = update_params(params)        ## params = { 'go', 'navg', 'ntrials', 'Rtest' }
	## close output file
	datafile.close()


def make_plots(savepath):
	f, magZ, argZ, sigma_f, sigma_magZ, sigma_argZ = get_plotdata(savepath)
	mag_plot(f,magZ,sigma_f,sigma_magZ,savepath)
	arg_plot(f,argZ,sigma_f,sigma_argZ,savepath)

def mag_plot(f,magZ,sigma_f,sigma_magZ,savepath):
	plt.figure(1,figsize=(6,6))
	## plot
	plt.errorbar(x=f/1e3,y=magZ/1e3,xerr=sigma_f/1e3,yerr=sigma_magZ/1e3,ls='none', marker='.',color='k')
	## format
	plt.title('Impedance: Magnitude vs. Frequency')
	plt.xlabel('frequency (kHz)'), plt.ylabel('|z| (kOhm)')
	xmax, ymax = 1.1*np.max(f)/1e3, 1.1*np.max(magZ)/1e3
	plt.grid()
#	plt.xlim(0,xmax), plt.ylim(0,ymax), plt.grid()
	plt.gca().set_xscale("log", nonposx='clip') 
	plt.gca().set_yscale("log", nonposy='clip')
	## save
	pathname  = savepath + '_magZ.pdf'
	plt.savefig(pathname,bbox_inches='tight',dpi=600)

def arg_plot(f,argZ,sigma_f,sigma_argZ,savepath):
	plt.figure(2,figsize=(6,6))
	## plot
	plt.errorbar(x=f/1e3,y=argZ,xerr=sigma_f/1e3,yerr=sigma_argZ,ls='none', marker='.',color='k')
	## format
	plt.title('Impedance: Phase vs. Frequency')
	plt.xlabel('frequency (kHz)'), plt.ylabel('Arg(z) (degrees)')
#	plt.xlim(0,xmax), plt.ylim(0,ymax), plt.grid()
	plt.gca().set_xscale("log", nonposx='clip') 
	plt.ylim(-95,95), plt.yticks([-90,-45,0,45,90])
	plt.grid()
	## save
	pathname  = savepath + '_argZ.pdf'
	plt.savefig(pathname,bbox_inches='tight',dpi=600)





def dd(filename = "temp.dat", directory="C:/electronics/vector_impedance_meter/datasets/temp/"):
	filepath = directory + filename
	allDATA   = np.genfromtxt(filepath,delimiter=', ',skip_header=2,unpack=True,autostrip=True)
	f, magZ, argZ = allDATA[0], allDATA[1], allDATA[2]
	V1, V2, phi = allDATA[3], allDATA[4], allDATA[5]	
	sigma_f, sigma_magZ, sigma_argZ = allDATA[6], allDATA[7], allDATA[8]
	sigma_V1, sigma_V2, sigma_phi = allDATA[9], allDATA[10], allDATA[11]
	Rtest, navg, ntrials = allDATA[12], allDATA[13], allDATA[14]
	dd = {'f':f, 'magZ':magZ, 'argZ':argZ, 'V1':V1, 'V2':V2, 'phi':phi,
		  'sigma_f':sigma_f, 'sigma_magZ':sigma_magZ, 'sigma_argZ':sigma_argZ,
		  'sigma_V1':sigma_V1, 'sigma_V2':sigma_V2, 'sigma_phi':sigma_phi,
		  'Rtest':Rtest, 'navg':navg, 'ntrials':ntrials}
	return dd




def meter(save_directory="C:/electronics/vector_impedance_meter/datasets/"):
	idno = get_idno()
	savedirec = save_directory + "%s/"%(idno)
	savepath = save_directory + "%s/%s"%(idno,idno)
	do_experiment(savedirec,savepath)
	make_plots(savepath)
	dd = dd(save_directory, "%s.dat"%(idno) )
	raw_input('THANK YOU COME AGAIN. ')
	return dd


