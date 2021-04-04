######################################################
######################################################
######################################################

import numpy as np
import matplotlib.pyplot as plt
import visa	
import time

######################################################
######################################################
######################################################

def setup():
	global scope
	scope = scope_init()

def scope_init():
	### initialize scope as visa object to initiate scope communication
	### if not communicating, try unplug plug usb
	lib_path = 'C:\\Windows\\SysWOW64\\visa32.dll'
	rm = visa.ResourceManager(lib_path)
	reslist = rm.list_resources()
	scope = rm.open_resource(u'USB0::0x0699::0x03A0::C040207::INSTR')
	IDN = scope.query('*IDN?')
	message = 'Now communicating with\n%s'%IDN
	print message
	return scope

### utility
def setget2(cmd,qry):
	scope.write(cmd)
	print qry
	print scope.query(qry)

def setget(cmd):
	qry = (cmd.split(' '))[0] + '?'
	setget2(cmd,qry)

def setgetDD(cmd_dict,ref):
	for key in cmd_dict.keys():
		cmd = ref[key] + ' ' + str(cmd_dict[key])
		qry = ref[key] + '?'
		setget2(cmd,qry)

def ask(qry):
	if not qry[-1] == '?':
		qry = qry + '?'
	out = scope.query(qry)
	print qry
	print out
	return out

def scale(unit):
	unit = unit[0]
	scale_dict = {'m':1e-3,'u':1e-6,'n':1e-9,'k':1e3,'M':1e6,'G':1e9}
	if unit in scale_dict.keys():
		scale = scale_dict[unit]
	else:
		scale = 1.0
	return scale

def reset_all():
	reset_ch2()
	reset_ch1()
	reset_trig()
	set_hfreq(float( scope.query('TRIG:MAIN:FREQ?') ))
	reset_aqmode()
	set_hpos(0.0)


### synchronization
def isbusy():
	## int 1 if busy, int 0 if not
	return int(scope.query('BUSY?')[0])

def waitloop():
	dt = .01
	waittime = 0.0
	while isbusy() == 1:
		time.sleep(dt)
		waittime += dt
	print 'WAITLOOP %s ms\n'%(waittime*1e3)


### vertical
def set_vscale(ch=1,volts=1.0):
	cmd = 'CH%s:SCALE %s'%(int(ch),volts)
	qry = 'CH%s:SCALE?'%(int(ch))
	setget2(cmd,qry)

def set_vpos(ch=1,divs=0.0):
	cmd = 'CH%s:POS %s'%(int(ch),divs)
	qry = 'CH%s:POS?'%(int(ch))
	setget2(cmd,qry)


### horizontal
def set_hscale(val=1.0,unit='s'):
	sec = val * scale(unit)
	cmd = 'HOR:MAIN:SCALE %s'%(sec)
	qry = 'HOR:MAIN:SCALE?'
	setget2(cmd,qry)

def set_hfreq(val=1.0,unit='Hz'):
	Hz = val * scale(unit)
	sec = 1./Hz
	set_hscale(sec)

def set_hpos(divs=0.0):
	hscale = float(scope.query('HOR:MAIN:SCALE?'))
	sec =  - divs * hscale
	cmd = 'HOR:MAIN:POS %s'%(sec)
	qry = 'HOR:MAIN:POS?'
	setget2(cmd,qry)


### trigger
def set_trig(trig_dict={}):
	trig_ref = {'mode':'TRIG:MAIN:MODE', 'source':'TRIG:MAIN:EDGE:SOURCE', 'volts':'TRIG:MAIN:LEVEL',
				'slope':'TRIG:MAIN:EDGE:SLOPE', 'holdoff':'TRIG:MAIN:HOLDOFF', 'coupling':'TRIG:MAIN:EDGE:COUP'}
	setgetDD(trig_dict,trig_ref)

def reset_trig():
	td = {'mode':'AUTO','source':'EXT','volts':0.0,'slope':'RISE','coupling':'DC','holdoff':0.0}
	set_trig(td)


### ch1
def set_ch1(vert_dict={}):
	vert_ref = {'coupling':'CH1:COUP', 'volts':'CH1:SCALE', 'probe':'CH1:PROBE', 
				'invert':'CH1:INVERT', 'select':'SEL:CH1'}
	setgetDD(vert_dict,vert_ref)

def reset_ch1():
	vd = {'coupling':'DC', 'volts':1.0, 'probe':'1', 'invert':'OFF', 'select':'ON'}
	set_ch1(vd)


### ch2
def set_ch2(vert_dict={}):
	vert_ref = {'coupling':'CH2:COUP', 'volts':'CH2:SCALE', 'probe':'CH2:PROBE', 
				'invert':'CH2:INVERT', 'select':'SEL:CH2'}
	setgetDD(vert_dict,vert_ref)

def reset_ch2():
	vd = {'coupling':'DC', 'volts':1.0, 'probe':'1', 'invert':'OFF', 'select':'ON'}
	set_ch2(vd)


### measure
def clear_meas():
	for i in [1,2,3,4,5]:
		cmd = 'MEASU:MEAS%s:TYPE NONE'%(i)
		setget(cmd)

def meas_check():
	err   = scope.query('*ESR?')
	if not int(err.strip()) == 0:
		print 'WARNING!! MEASUREMENT ERROR ' + '-' * 22
		print '*ESR?'
		print err.strip()
		print 'ALLEV?'
		print scope.query('ALLEV?').strip()
		print '-' * 50 + '\n'
		return 1
	else:
		return 0

def meas_immed():
	ask('MEASU:IMM?')
	val = float(ask('MEASU:IMM:VAL?')[:-1])
	err = meas_check()
	if err == 0:
		return val
	else:
		return np.nan

def meas_freq1():
	scope.write('MEASU:IMM:TYPE FREQ')
	scope.write('MEASU:IMM:SOURCE1 CH1')
	return meas_immed()

def meas_freq2():
	scope.write('MEASU:IMM:TYPE FREQ')
	scope.write('MEASU:IMM:SOURCE1 CH2')
	return meas_immed()

def meas_tfreq():
	return float(ask('TRIG:MAIN:FREQ?').strip())

def meas_rms1():
	scope.write('MEASU:IMM:TYPE RMS')
	scope.write('MEASU:IMM:SOURCE1 CH1')
	return meas_immed()

def meas_rms2():
	scope.write('MEASU:IMM:TYPE RMS')
	scope.write('MEASU:IMM:SOURCE1 CH2')
	return meas_immed()

def meas_phi12():
	scope.write('MEASU:IMM:TYPE PHASE')
	scope.write('MEASU:IMM:SOURCE1 CH1')
	scope.write('MEASU:IMM:SOURCE2 CH2')
	return meas_immed()

### acquire
def set_aq(cmd='', navg=0):
	ref = {'single':'ACQ:STOPA SEQ', 'runstop':'ACQ:STOPA RUNST',
		   'sample':'ACQ:MODE SAM', 'avg':'ACQ:MODE AVE',
		   'on':'ACQ:STATE ON', 'off':'ACQ:STATE OFF'}
	if cmd == 'avg' and not navg == 0:
		set_numav(navg)
	setget(ref[cmd])

def reset_aqmode():
	set_aq('sample')
	set_aq('runstop')
	set_aq('on')

def set_numav(numav=16):
	cmd = 'ACQ:NUMAV %s'%(numav)
	setget(cmd)

def aq1():
	set_aq('on')
	waitloop()


### frame
def frame_param(ch=1):
	if ch==1:
		amp  = np.sqrt(2) * meas_rms1()
		freq = meas_tfreq()
		isgood = True
		if not np.isfinite(amp):
			amp = 4.*(4.*float(ask('CH1:SCALE?').strip()))
			isgood = False
	if ch==2:
		amp  = np.sqrt(2) * meas_rms2()
		freq = meas_tfreq()
		isgood = True
		if not np.isfinite(amp):
			amp = 4.*(4.*float(ask('CH2:SCALE?').strip()))
			isgood = False
	return amp, freq, isgood

def frame1():
	amp, freq, isgood = frame_param(ch=1)
	vscale = 1.2 * ( amp / 4. )
	hfreq  = 3.0 * freq
	set_vscale(ch=1,volts=vscale)
	set_hfreq(hfreq)
	if not isgood:
		print 'ISGOOD = FALSE\n'
		aq1()
		frame1()


def frame2():
	amp, freq, isgood = frame_param(ch=2)
	vscale = 1.2 * ( amp / 4. )
	hfreq  = 3.0 * freq
	set_vscale(ch=2,volts=vscale)
	set_hfreq(hfreq)
	if not isgood:
		print 'ISGOOD = FALSE\n'
		aq1()
		frame2()


def frame():
	frame2()
	frame1()








######################################################
######################################################
######################################################

setup()

######################################################
######################################################
######################################################
