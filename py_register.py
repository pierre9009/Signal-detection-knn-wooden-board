#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 

@author: Alexandre Constantin, Florent Chatelain
"""

import numpy as np
import matplotlib.pylab as plt

# Equivalent de fonctions Matlab en Python
def xcorr(y1, y2, maxlag = -1, scale = 'none'):
    """ "returns the cross-correlation of two discrete-time sequences.
         Cross-correlation measures the similarity
         between a vector x and shifted (lagged)
         copies of a vector y as a function of the lag.""

        Définition de 'xcorr' Matlab, cf.
        https://www.mathworks.com/help/matlab/ref/xcorr.html

    Entrées:
        y1, y2 : ndarray de même longueur.
                 les signaux
        maxlag : integer 
                la corrélation est calculée pour tous les retards 
                r dans -maxlag,...,maxlag.
                Par défaut, maxlag=-1 correspond au nombre total de points 
                dans le signal.
        scale : {'none', 'biased', 'unbiased'}, optional
            'none':
              Par défaut. Pour des signaux de longueur différente.
              Cross-correlation des signaux
            'biased':
              Pour chaque retard, la constante de 
              normalisation est la même : le nombre N d'échantillons
              dans le signal. Cela biaise vers 0 la corrélation estimée
              pour des grands retards.
            'unbiased':
              La constante de normalisation vaut N-|r| et  correspond 
              au nombre de produits croisés qui sont effectivement sommés pour
              chaque retard r.
    Sorties:
        xcorr: ndarray
               corrélations pour chaque retard dans -maxlag,...,maxlag
        lag:   ndarray 
               retards associés : -maxlag,...,maxlag
    """
    # Scaling?
    scale_from_option_dict = {'n': -1, 'b': 0,'u': 1}
    scale = scale_from_option_dict[scale.lower()[0]]

    l_ = len(y1)
    if scale != -1:
        if l_ != len(y2):
            raise ValueError('Les longueurs doivent être identiques.')
    

    # Do correlation
    corr = np.correlate(y1, y2, mode='full') # / np.sqrt(P_y1 * P_y2)
    
    if scale == 0:
        # The biased scaling factor is N (signal length)
        corr = corr / l_
    elif scale == 1:
        # The unbiased scaling factor is N - |r| where r is the lag
        # (i.e. the number of cross-terms to estime the correlation at lag r)
        unbiased_sample_size = np.correlate(np.ones(l_), np.ones(l_),
                                            mode='full')
        corr = corr / unbiased_sample_size
    
    shift = l_
    lags = np.arange(2*l_-1) - shift
    
    if maxlag != -1 and maxlag <= shift:
        corr = corr[max(0, shift-maxlag-1):min(2*l_-1, shift+maxlag)]
        lags = np.arange(2*maxlag + 1) - maxlag

    return corr, lags


# Register function
def register(xref, x, maxdelay = None):
    ''' "Register x onto xref. y is the registered version of x."

    Entrées:
        xref, x : ndarray de même longueur - signaux
        maxdelay : integer 
                   retard maximal considéré.
                   Par défaut, maxdelay=len(xref)/3.
    Sorties:
        y: ndarray
              Signal x registered.
    '''
    # If maxdelay is undefined
    if maxdelay is None:
        maxdelay = int(xref.shape[0] / 3)

    # Format data as centered column vectors
    xref = xref - xref.mean()
    x = x - x.mean()

    # Correlation function
    cc = xcorr(xref, x, maxlag = maxdelay, scale = 'u')

    # Find delay that maximizes the correlation
    delay = np.argmax(cc[0]) - maxdelay

    # Create registered x
    if delay == 0:
        y = np.copy(x)
    elif delay > 0:
        y = np.concatenate([np.zeros(delay), x[:(x.shape[0] - delay)]])
    else:
        y = np.concatenate([x[(-delay):], np.zeros(-delay)])

    return y


# Test code when register is executed by python as main
if __name__ == "__main__":
    # Define sin function
    Xref = np.sin(np.arange(1, 46))
    # Delay the sin by l samples (adding zeros)
    l = 4
    X = np.concatenate([np.zeros(l), np.sin(np.arange(1, 46 - l))])

    # Register x into y
    y = register(Xref, X)
    t=[0,1,2,3,4,5,6,7,8,9]
    print(Xref[:10])
    plt.plot(t,y[:10],label='y')
    plt.plot(t,Xref[:10],label='Xref')
    plt.legend()
    print(y[:10])
