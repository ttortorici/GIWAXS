import pyFAI
import numpy as np

def getAI(fname='pyfai.poni'): return pyFAI.load(fname)

def azimuthal_smoothing(img,ai,npt=1000,method=np.ma.median,mask=None,threshold=5,error_model=np.ma.std):
  # make sure it is float (and create a copy even if is float)
  img = img.astype(np.float);
  img = np.ma.MaskedArray( data = img, mask = mask, copy = False )

  if 'q_center' not in ai._cached_array: ai.integrate1d(img,npt)
  if ai.get_darkcurrent() is not None: img -= ai.get_darkcurrent()
  if ai._polarization is not None:     img /= ai._polarization
  if ai._dssa is not None:             img /= ai._dssa
  qarray = ai._cached_array['q_center']
  if 'azimuthal_smoothing' not in ai._cached_array:
    # make bins
    q      = np.sort( qarray.ravel() )
    delta_q = np.min( np.diff(q) )
    bins = np.linspace(  q[0]-delta_q, q[-1] + delta_q,num=npt)
    idx = np.digitize( qarray, bins )
    ai._cached_array['azimuthal_smoothing'] = idx
  idx = ai._cached_array['azimuthal_smoothing']; # avoid typing ...
  for ibin in range(idx.max()):
    pixels_in_bin = idx == ibin
    values_in_bin = img[pixels_in_bin]
    if values_in_bin.size == 0 or np.all(values_in_bin.mask): continue
    indices_1d = np.argwhere(pixels_in_bin.ravel())
    # average/median
    reference  = method( values_in_bin )
    error      = error_model( values_in_bin )
    to_remove  = values_in_bin > reference + threshold*error
    indices_1d = np.argwhere(pixels_in_bin.ravel())[to_remove]
    img.ravel()[indices_1d] = reference
  if ai._dssa is not None:             img *= ai._dssa
  if ai._polarization is not None:     img *= ai._polarization
  if ai.get_darkcurrent() is not None: img += ai.get_darkcurrent()
  return img

def test(npt=1000):
  import matplotlib.pyplot as plt
  ai = getAI()
  imgs = np.load('imgs_with_zinger.npy')[:5]
  mask = np.load('mask.npy')
  fig,ax=plt.subplots(2,len(imgs))
  for iimg,img in enumerate(imgs):
    q,i=ai.integrate1d(img,npt,unit="q_A^-1",mask=mask)
    #ax[iimg].plot(q,i1)
    img_d= azimuthal_smoothing(img,ai,npt=npt,mask=mask)
    q,i_d=ai.integrate1d(img_d,npt,unit="q_A^-1",mask=mask)
    ax[0,iimg].plot(q,i-i_d)
    ax[1,iimg].imshow(img-img_d,clim=(0,10),aspect='auto')

if __name__ == '__main__':
  test()
