# ┌─────────────────────────
# │ signal
# └─────────────────────────

import numpy.fft as fft
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def Nfft():
    return 2**14

def FreqVec(t, x, **kwargs):
    freq = [ i*1e-6 for i in np.arange(len(x))*1.0/t[-1] ]
    nfft = kwargs.get('Nfft', Nfft())
    return np.linspace(freq[0], freq[-1], nfft)


def ComputeSpectre(t, x, **kwargs):
    nfft = kwargs.get('Nfft', Nfft())
    return (fft.fft(x, nfft))*2/nfft


def AttenuationCoeff(X_ref, X_ech, d):
    """
    """
    if np.diff(d)==0:
        d = d[0]
    else:
        d = d[1]-d[0]
    alphacoeff = -1/d*np.log( np.abs(X_ech/X_ref) )

    return alphacoeff

def PhaseVelocity(X_ref, X_ech, freqs, d, c0=None):
    """
    """

    # maximum amplitude of fft
    Xmax = max(abs(X_ech))
    fmax = freqs[np.where(abs(X_ech)==Xmax)[0][0]]

    # phase difference
    X = X_ech/X_ref
    argX = np.unwrap(np.angle(X))
    argX[argX==0]=None

    # velocity equation
    if (d[1]-d[0])==0:
    # -- case where REF and ECH have same thickness
    #    but velocity are differents (different wave number)
    #    and the velocity of REF is known
        x = d[1]
        c = lambda n: 1/( 1/c0 - (argX+n*2*np.pi)/(2*np.pi*x*freqs) )
    else:
    # -- case where REF and ECH have different thicknesses
    #    but the velocity is the same (same wave number)
        x = d[0]-d[1]
        c = lambda n: 2*np.pi*x*freqs/(argX+n*2*np.pi)

    # we compute velocity [n·2·pi]
    n = [-2,-1,0,1,2]
    fig = plt.figure()
    line = [[]]*len(n)
    for i in range(len(n)):
        line[i] = plt.plot(freqs, c(n[i]))[0]
    plt.ylim(bottom=0, top=4)
    plt.xlim(left=0, right=3*fmax)
    plt.legend(tuple(line), tuple([str(i+1) for i in range(len(n))]))
    plt.show(block=False)

    # we ask to choose one value of n
    print("Please choose a velocity. Enter a number: ")
    i = input()

    plt.close(fig)

    return c(n[int(i)-1])



def DefWindow(time, signal, window=True, **kwargs):

    win = np.zeros([len(signal)])

    if window in ['auto', 'default']:
        from scipy.signal import hilbert
        sig = np.abs(hilbert(signal))
        i = 0

        threshold = kwargs.get('threshold', 0.08)
        win = np.zeros([len(sig)])
        idx = np.where( abs(sig)/max(abs(sig)) > threshold )[0]
        win[idx]=1

        idx = np.where( abs(win[1:]-win[:-1]) > 0)[0] + 1
        idx = idx.tolist()
        for i in range(int(len(idx)/2)):
            u = sig[idx[2*i]:idx[2*i+1]]
            if max(sig)==max(u):
                idx = [idx[2*i],idx[2*i+1]]
                break

    elif window in ['manual', True]:
        fig = plt.figure()
        axes = plt.plot(time*1e6,signal/max(signal), )
        plt.xlabel("Time (µs)")
        plt.ylabel("Amplitude (1)")
        plt.show(block=False)
        pos = plt.ginput(2)
        idx1 = np.where( time>pos[0][0]*1e-6 )[0][0]
        idx2 = np.where( time>pos[1][0]*1e-6 )[0][0]
        idx = np.sort([ idx1, idx2 ]).tolist()
        plt.close(fig)

    elif type(window)==list and len(window)==2:
        idx = [ np.where( time>window[i]*1e-6 )[0][0] for i in [0,1] ]

    win[idx[0]:idx[-1]] = 1
    N = int(idx[-1]-idx[0])
    N = N/2
    N = N - np.mod(N,2)
    N = 4
    win[int(idx[0]-N/2):idx[0]] = np.hanning(N)[:int(N/2)]
    win[idx[1]:int(idx[1]+N/2)] = np.hanning(N)[int(N/2):]

    print(
        'Windowed between {} and {} µs.' . format(time[idx[0]]*1e6, time[idx[1]]*1e6)
    )

    return win, idx



def _butter_lowpass(cutoff, fs, order=5):
    from scipy.signal import butter
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    from scipy.signal import filtfilt, lfilter_zi, lfilter
    b, a = _butter_lowpass(cutoff, fs, order=order)
    print(a,b)
    zi = lfilter_zi(b, a)
    z, _ = lfilter(b, a, data, zi=zi*data[0])
    z2, _ = lfilter(b, a, z, zi=zi*z[0])
    # y = lfilter(b, a, data)
    y = filtfilt(b, a, data)
    return y

