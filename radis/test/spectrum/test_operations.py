# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 14:26:44 2018

@author: erwan
"""

from __future__ import print_function, absolute_import, division, unicode_literals
from radis.tools.database import load_spec
from radis.spectrum.operations import crop, Radiance_noslit, add_constant, multiply
from radis.test.utils import getTestFile
import pytest

@pytest.mark.fast
def test_crop(verbose=True, *args, **kwargs):
    ''' Test that update can correctly recompute missing quantities '''

    # 1) A crop example in the same unit as the one stored

    # Work with a Spectrum object that was generated by Specair
    s = load_spec(getTestFile('N2C_specair_380nm.spec'))
    # Focus on N2(C->B), v'=0, v''=2 band:
    s.crop(376, 381, 'nm')
    
    w = s.get_wavelength()
    assert w.min() >= 360
    assert w.max() <= 382
    
    # 2) A crop example in different unit as the one stored

    # Work with a Spectrum object that was generated by Specair
    s1 = load_spec(getTestFile('CO_Tgas1500K_mole_fraction0.01.spec'), binary=True)
    # Focus on N2(C->B), v'=0, v''=2 band:
    s1.crop(4530, 4533, 'nm')
    
    w = s1.get_wavelength()
    assert w.min() >= 4530
    assert w.max() <= 4533
    
    return True


@pytest.mark.fast
def test_cut_recombine(verbose=True, *args, **kwargs):
    ''' 
    Use :func:`~radis.spectrum.operations.crop` and :func:`~radis.los.slabs.MergeSlabs`
    to cut a Spectrum and recombine it
    
    Assert we still get the same spectrum at the end
    '''
    from radis import MergeSlabs

    s = load_spec(getTestFile('CO_Tgas1500K_mole_fraction0.01.spec'), binary=True)
    # Cut in half
    cut = 2177
    s1 = crop(s, 2000, cut, 'cm-1', inplace=False)
    s2 = crop(s, cut, 2300, 'cm-1', inplace=False)

    # Recombine
    s_new = MergeSlabs(s1, s2, resample='full', out='transparent')
    
    # Compare
    assert s.compare_with(s_new, spectra_only=True, plot=False, verbose=verbose)
    
@pytest.mark.fast
def test_invariants(*args, **kwargs):
    ''' Ensures adding 0 or multiplying by 1 does not change the spectra '''
    from radis import load_spec
    from radis.test.utils import getTestFile
    
    s = load_spec(getTestFile("CO_Tgas1500K_mole_fraction0.01.spec"))
    s.update()
    s = Radiance_noslit(s)

    assert s.compare_with(add_constant(s, 0, 'W/cm2/sr/nm'), 
                          plot=False, spectra_only='radiance_noslit')
    assert s.compare_with(multiply(s, 1), 
                          plot=False, spectra_only='radiance_noslit')
    
    assert 3*s/3 == s
    assert (1+s)-1 == s
    

@pytest.mark.fast
def test_operations_inplace(verbose=True, *args, **kwargs):
    
    from radis.spectrum.operations import Radiance_noslit

    s = load_spec(getTestFile('CO_Tgas1500K_mole_fraction0.01.spec'), binary=True)
    s.update('radiance_noslit', verbose=False)
    s = Radiance_noslit(s)
    
    # Add 1, make sure it worked
    I_max = s.get('radiance_noslit')[1].max()    
    s += 1
    assert s.get('radiance_noslit')[1].max() == I_max + 1
    if verbose:
        print('test_operations: s += 1: OK')
    
    # Multiply, make sure it worked
    I_max = s.get('radiance_noslit')[1].max()    
    s *= 10
    assert s.get('radiance_noslit')[1].max() == 10*I_max
    if verbose:
        print('test_operations: s *= 10: OK')
    
def _run_testcases(verbose=True, *args, **kwargs):
    ''' Test procedures
    '''

    test_crop(verbose=verbose, *args, **kwargs)
    test_cut_recombine(verbose=verbose, *args, **kwargs)
    test_invariants(verbose=verbose, *args, **kwargs)
    test_operations_inplace(verbose=verbose, *args, **kwargs)
    
    return True

if __name__ == '__main__':
    
    _run_testcases()
    