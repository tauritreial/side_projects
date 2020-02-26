#Year 3 PHY3054 Research Techniques in Astronomy Mid-Term Coursework
#Tauri Treial, URN:6375357, email: tt00191@surrey.ac.uk

import pylab as plt
import numpy as np
from astropy.io import fits
from matplotlib.image import imread
from scipy.ndimage import interpolation	
'''
#PROBLEM 1 - Bessel functions
print ('################## TASK 1 ##################')

x = np.linspace(0, 20, 100)

def safe_zero(x, minval=0.0000000000001):
	return x.clip(min=minval)

J0 = np.sin(x)/x
J1 = (np.sin(x)/x**2) - (np.cos(x)/x)
J2 = ((3/x**2)-1)*np.sin(x)/x - (3*np.cos(x)/x**2)

#print J0, J1, J2 

plt.plot(x, J0, color="red", label="Zeroth order")
plt.plot(x, J1, color="blue", linestyle="--", label="First order")
plt.plot(x, J2, color="green", linestyle="-.", label="Second order")
plt.title('The first 3 spherical Bessel functions for 0 $\leq\ x \leq$ 20')
plt.xlabel('x value')
plt.ylabel('Value of the fuction')
plt.legend(loc=1)
plt.savefig("Bessel.png")
plt.show()

print ('This will calculate the first 3 spherical Bessel functions.')
print ('Plots and saves the functions into a file called')
print ('Bessel.png.')


#PROBLEM 2 - 67P
print ('################## TASK 2 ##################')
print ('This will determine the parameters of 67P comet.')
A = 3.46 #AU
a = A*1.496E13 #cm 
e = 0.64
G = 6.67428E-8 #cm3g-1s-2
M_Sun =1.989E33 #g
print ('The semi-major axis is %3.2f'%(A),'AU and eccentricity %3.2f'%(e))

P = 2*np.pi*a**1.5/(G*M_Sun)**0.5 #Period in seconds
p = P/3600/24/365.25 #Period in years
r_p = A*(1-e) #Perihelion in AU
r_a = A*(1+e) #Apohelion in AU

print ('The orbital period of 67P is  %3.2f'%(p),'years.')
print ('Perihelion and apohelion are  %3.2f'%(r_p),'AU and  %3.2f'%(r_a),'AU respectively.')

M_67P = 9.982E15 #g, taken from Wikipedia

E = -(G*M_Sun)/(2*a) #erg
L =np.sqrt(G*M_Sun*a*(1-e**2)) #erg*s

print ('The energy of the comet is  %3.3E'%(E),'erg.')
print ('The angular momentum of the comet is  %3.3E'%(L),'erg*s.')

'''

#PROBLEM 3 - Yale La Silla-QUEST
print ('################## TASK 3 ##################')
print ('The code will calibrate astronomical images')
print ('and saves reduced fits images.')

		#Bias Correction

fakeData = np.zeros((640, 2400), dtype='float')
#print fakeData.shape

biasPerRow=np.median(fakeData[:, 600:640], axis=1)
#print biasPerRow.shape

dataNew=fakeData[0:600,:]
#print dataNew.shape

for i in range(639):
	dataNew[:,i]-=biasPerRow[i]



		#Dark images
	
darkData = []

header1 = fits.getheader('dark_10.C22.fits')
header2 = fits.getheader('dark_180.C22.fits')
	
darkRaw1 = fits.getdata("dark_10.C22.fits")
darkRaw2 = fits.getdata("dark_180.C22.fits")
	#Dark images are already bias corrected
#print(header1['EXPTIME'])
#print(header1['IMAGETYP'])
#print(header2['EXPTIME'])
#print(header2['IMAGETYP'])




		#Flat images

ExpIde = [1708, 1759, 1853, 1944, 2035, 2127, 2217, 2309, 2401]	

flatList1 = []
for expId in ExpIde:
	header = fits.getheader("2013091023%04de.C22.fits" % expId)
	flatRaw = fits.getdata("2013091023%04de.C22.fits" % expId)
	flat1 = flatRaw - biasPerRow[i]
	flatList1.append(flat1)
	#print(header['EXPTIME'])
	#print(header['IMAGETYP'])

ExpIdm = [5457, 5548, 5641, 5732, 5822, 5915]

flatList2 = []
for expId in ExpIdm:
	header = fits.getheader("2013091109%04dm.C22.fits" % expId)
	flatRaw = fits.getdata("2013091109%04dm.C22.fits" % expId)
	flat2 = flatRaw - biasPerRow[i] #bias correcting the flat images
	flatList2.append(flat2)
	#print(header['EXPTIME'])
	#print(header['IMAGETYP'])

flatList = flatList1+flatList2 

	#Creating master flat
	
#Exposure time of 180s is for science(2) and 10s is for flat images(1)
#flatCorrect = flatList - darkRaw1
mFlat = np.median(np.array(flatList), axis=0)
nFlat = mFlat/np.median(mFlat.flatten())
hdu = fits.PrimaryHDU(nFlat)
hdu.header.add_comment("Normalised median of flat field exposures")
fits.writeto("masterFlat.fits", hdu.data, hdu.header)

	#calculating average for plotting
average =sum(nFlat)/float(len(nFlat))	
plt.hist(average, 1000)
plt.title('Average pixel values for normalised masterFlat frame')
plt.xlabel('Pixel value')
plt.ylabel('Frequency')
plt.axis([0.8, 1.2, 0, 350])
plt.savefig("Average_pixel.png")
plt.show()



	#Science images
		
ExpIds = [10234901, 11020246, 11040543]

sciData = np.array([fits.getdata("201309%08ds.C22.fits" % expID) for expID in ExpIds])
sciHeader = []
for expID in ExpIds:
	header = fits.getheader("201309%08ds.C22.fits" % expID)
	#print(header['EXPTIME'])
	sciHeader.append(header)
	
	
	
	#Calibrating science images

sciMbd = sciData - biasPerRow[i] - darkRaw2
#sciFlat = sciMbd/(nFlat)
sciFlat = sciMbd/(nFlat+1e-9)

	#Sky-subtracting science images
	
minpix = min(sciFlat.flatten())
maxpix = max(sciFlat.flatten())



#print maxpix
#print minpix
rng = int(maxpix - minpix)
#print (rng)
sciSky = []
for i in range(3):
	expId = i + 1
	
	
	
	#hf = np.histogram(sciFlat[i].flatten(), bins=rng, range=(minpix,maxpix))
	hf = np.histogram(sciFlat[i].flatten(), bins=rng // 10000, range=(minpix,maxpix))
	
	skyval = hf[1] [np.where(hf[0] == hf[0].max())] #in P2.7
	#skyval = hf[1][hf[0]==max(hf[0])] #in P3.0
	#modeval = hf[0] == max(hf[0])
	#skyval = hf[1][modeval]
	#print skyval
	skySub = sciFlat[i] - skyval
	sciSky.append(skySub)
	
#print sciSky

	#Saving the images
	
for i in range(3):
	expId = i + 1
	fits.writeto("QUESTdata-%03dL-redux.fits" % expId, sciSky[i], sciHeader[i], output_verify='ignore')



	#Shifting the images

refFile = fits.getdata('QUESTdata-001L-redux.fits')
shiftFile1 = fits.getdata('QUESTdata-002L-redux.fits')
shiftFile2 = fits.getdata('QUESTdata-003L-redux.fits')

newShift1 = interpolation.shift(shiftFile1, (17.132, -3.9655))
newShift2 = interpolation.shift(shiftFile2, (39.82, -6.847))

fits.writeto("Reference-001L.fits",refFile,output_verify='ignore')
fits.writeto("Shifted-002L.fits",newShift1,output_verify='ignore')
fits.writeto("Shifted-003L.fits",newShift2,output_verify='ignore')



	#Combining the images
	
combine = refFile + newShift1 + newShift2
fits.writeto("Combined-QuestData.fits", combine, output_verify = 'ignore')

	
quit() #exit python















