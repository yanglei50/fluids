# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2018 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from fluids import *
import numpy as np
from numpy.testing import assert_allclose
import pytest
from fluids.particle_size_distribution import *
import scipy.stats
from random import uniform
from scipy.integrate import quad


def test_ASTM_E11_sieves():
    sieves = ASTM_E11_sieves.values()
    tot = sum([i.d_wire for i in sieves])
    assert_allclose(tot, 0.105963384)
    
    tot = sum([i.opening for i in sieves])
    assert_allclose(tot, 0.9876439999999999)
    
    assert len(ASTM_E11_sieves) == 56

    # Test but do not validate these properties
    tot = 0.0
    for attr in ['Y_variation_avg', 'X_variation_max', 'max_opening', 'd_wire', 'd_wire_min', 'd_wire_max', 'opening', 'opening_inch']:
        tot += sum(getattr(i, attr) for i in sieves)

def test_ISO_3310_2_sieves():
    sieves = ISO_3310_1_sieves.values()
    tot = sum([i.d_wire for i in sieves])
    assert_allclose(tot, 0.17564599999999997)
    
    tot = sum([i.opening for i in sieves])
    assert_allclose(tot, 1.5205579999999994)
    
    assert len(ISO_3310_1_sieves) == 99

    # Test but do not validate these properties
    tot = 0.0
    for attr in ['Y_variation_avg', 'X_variation_max', 'd_wire', 'd_wire_min', 'd_wire_max', 'opening']:
        tot += sum(getattr(i, attr) for i in sieves)

    for l in [ISO_3310_1_R20_3, ISO_3310_1_R20, ISO_3310_1_R10, ISO_3310_1_R40_3]:
        for i in l:
            assert i.designation in ISO_3310_1_sieves



def test_ParticleSizeDistribution_basic():
    ds = [240, 360, 450, 562.5, 703, 878, 1097, 1371, 1713, 2141, 2676, 3345, 4181, 5226, 6532]
    numbers = [65, 119, 232, 410, 629, 849, 990, 981, 825, 579, 297, 111, 21, 1]
    dist = ParticleSizeDistribution(ds=ds, numbers=numbers)

    # this is calculated from (Ds, numbers)
    number_fractions = [0.010640039286298903, 0.01947945653953184, 0.03797675560648224, 0.06711409395973154, 0.102962841708954, 0.13897528237027337, 0.16205598297593715, 0.160582746767065, 0.13504665247994763, 0.09477819610410869, 0.048616794892781146, 0.01816991324275659, 0.0034375511540350305, 0.0001636929120969062]
    fractions = [4.8560356399310335e-05, 0.00021291794698947167, 0.0008107432330218852, 0.0027975134942445257, 0.00836789808490677, 0.02201901107895143, 0.05010399231412809, 0.0968727835386488, 0.15899879607747244, 0.2178784903712532, 0.21825921197532888, 0.159302671180342, 0.05885464261922434, 0.0054727677290887945]
    length_fractions = [0.0022265080273913248, 0.005405749400984079, 0.013173675010801534, 0.02909808308708846, 0.05576732372469186, 0.09403390879219536, 0.1370246122004729, 0.16966553692650058, 0.17831420382670332, 0.15641421494054603, 0.10028800800464328, 0.046849963047687335, 0.011078803825079166, 0.0006594091852147985]
    area_fractions = [0.0003643458522227456, 0.0011833425086503686, 0.0036047198267710797, 0.009951607879295004, 0.023826910138492176, 0.05018962198499494, 0.09139246506396961, 0.1414069073893575, 0.18572285033413602, 0.20362023102799823, 0.16318760564859225, 0.09528884410476045, 0.028165197280747324, 0.0020953509600122053]
    
    opts = [{'number_fractions': number_fractions},  
            {'numbers': numbers},
            {'fractions': fractions},
            {'length_fractions': length_fractions},
            {'area_fractions': area_fractions}]
    
    for opt in opts:
        asme_e799 = ParticleSizeDistribution(ds=ds, **opt)
        
        d10 = asme_e799.mean_size(1, 0)
        assert_allclose(d10, 1459.3725650679328)
        
        d21 = asme_e799.mean_size(2, 1)
        assert_allclose(d21, 1857.7888572055529)
        d20 = asme_e799.mean_size(2, 0)
        assert_allclose(d20, 1646.5740462835831)
        
        d32 = asme_e799.mean_size(3, 2)
        assert_allclose(d32, 2269.3210317450453)
        # This one is rounded to 2280 in ASME - weird
        
        d31 = asme_e799.mean_size(3, 1)
        assert_allclose(d31, 2053.2703977309357)
        # This one is rounded to 2060 in ASME - weird
        
        d30 = asme_e799.mean_size(3, 0)
        assert_allclose(d30, 1832.39665294744)
        
        d43 = asme_e799.mean_size(4, 3)
        assert_allclose(d43, 2670.751954612969)
        # The others are, rounded to the nearest 10, correct.
        # There's something weird about the end points of some intermediate values of
        #  D3 and D4. Likely just rounding issues.
        
        vol_percents_exp = [0.005, 0.021, 0.081, 0.280, 0.837, 2.202, 5.010, 9.687, 15.900, 21.788, 21.826, 15.930, 5.885, 0.547]
        assert vol_percents_exp == [round(i*100, 3) for i in asme_e799.fractions]
        
        assert_allclose(asme_e799.fractions, fractions)
        assert_allclose(asme_e799.number_fractions, number_fractions)
        
        # i, i distributions
        d00 = asme_e799.mean_size(0, 0)
        assert_allclose(d00, 1278.7057976023061)
        
        d11 = asme_e799.mean_size(1, 1)
        assert_allclose(d11, 1654.6665309027303)
        
        d22 = asme_e799.mean_size(2, 2)
        assert_allclose(d22, 2054.3809583432208)
        
        d33 = asme_e799.mean_size(3, 3)
        assert_allclose(d33, 2450.886241250387)
        
        d44 = asme_e799.mean_size(4, 4)
        assert_allclose(d44, 2826.0471682278476)


def test_pdf_lognormal():
    pdf = pdf_lognormal(d=1E-4, d_characteristic=1E-5, s=1.1)
    assert_allclose(pdf, 405.5420921156425, rtol=1E-12)
    
    pdf_sp = scipy.stats.lognorm.pdf(x=1E-4/1E-5, s=1.1)/1E-5
    assert_allclose(pdf_sp, pdf)
    
    assert 0.0 == pdf_lognormal(d=0, d_characteristic=1E-5, s=1.1)
    
    # Check we can get down almost to zero
    pdf = pdf_lognormal(d=3.7E-24, d_characteristic=1E-5, s=1.1)
    assert_allclose(pdf, 4.842842147909424e-301)
    
    
def test_cdf_lognormal():
    cdf = cdf_lognormal(d=1E-4, d_characteristic=1E-5, s=1.1)
    assert_allclose(cdf, 0.98183698757981763)
    
    cdf_sp = scipy.stats.lognorm.cdf(x=1E-4/1E-5, s=1.1)
    assert_allclose(cdf, cdf_sp)
    
    assert cdf_lognormal(d=1e300, d_characteristic=1E-5, s=1.1) == 1.0
    assert cdf_lognormal(d=0, d_characteristic=1E-5, s=1.1) == 0.0
    
    
def test_pdf_lognormal_basis_integral():
    ans = pdf_lognormal_basis_integral(d=1E-4, d_characteristic=1E-5, s=1.1, n=-2)
    assert_allclose(ans, 56228306549.263626)
    
    # Some things:
    ans = pdf_lognormal_basis_integral(d=1E-100, d_characteristic=1E-5, s=1.1, n=-2)
    ans2 = pdf_lognormal_basis_integral(d=1E-120, d_characteristic=1E-5, s=1.1, n=-2)
    assert_allclose(ans, ans2, rtol=1E-12)
    
    # Couldn't get the limit for pdf_lognormal_basis_integral when d = 0
    # # with Sympy Or wolfram
    
@pytest.mark.fuzz
@pytest.mark.slow
def test_pdf_lognormal_basis_integral_fuzz():
    # The actual integral testing
    analytical_vales = []
    numerical_values = []
    
    for n in [-3, -2, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
        # Errors at -2 (well, prevision loss anyway)
        for dmax in [1e-3, 1e-2, 2e-2, 3e-2, 4e-2, 5e-2, 6e-2, 7e-2, 8e-2, 1e-1]:
            dmax = dmax/100 # Make d smaller
            analytical = (pdf_lognormal_basis_integral(dmax, d_characteristic=1E-5, s=1.1, n=n)
                          - pdf_lognormal_basis_integral(1e-20, d_characteristic=1E-5, s=1.1, n=n))
    
            to_int = lambda d : d**n*pdf_lognormal(d, d_characteristic=1E-5, s=1.1)
            points = np.logspace(np.log10(dmax/1000), np.log10(dmax*.999), 40)
            numerical = quad(to_int, 1e-9, dmax, points=points)[0] # points=points
            analytical_vales.append(analytical)
            numerical_values.append(numerical)
    
    assert_allclose(analytical_vales, numerical_values, rtol=2E-6)


def test_cdf_Gates_Gaudin_Schuhman():
    '''
    d, dmax, n, m = symbols('d, dmax, n, m')
    expr = (d/dmax)**n
    pdf = diff(expr, d)
    '''
    cdf = cdf_Gates_Gaudin_Schuhman(d=2E-4, d_characteristic=1E-3, m=2.3)
    assert_allclose(cdf, 0.024681354508800397)
    
    cdf = cdf_Gates_Gaudin_Schuhman(d=1.01e-3, d_characteristic=1E-3, m=2.3)
    assert_allclose(cdf, 1)
    
    
def test_pdf_Gates_Gaudin_Schuhman():
    pdf = pdf_Gates_Gaudin_Schuhman(d=2E-4, d_characteristic=1E-3, m=2.3)
    assert_allclose(pdf, 283.8355768512045)
    
    pdf = pdf_Gates_Gaudin_Schuhman(d=2E-3, d_characteristic=1E-3, m=2.3)
    assert_allclose(pdf, 0)
    
    
def test_pdf_Gates_Gaudin_Schuhman_basis_integral():
    ans =  pdf_Gates_Gaudin_Schuhman_basis_integral(d=0, d_characteristic=1e-3, m=2.3, n=5)
    assert_allclose(ans, 0)
    
    ans = pdf_Gates_Gaudin_Schuhman_basis_integral(d=1e-3, d_characteristic=1e-3, m=2.3, n=5)
    assert_allclose(ans, 3.1506849315068495e-16)
    
    
@pytest.mark.slow
@pytest.mark.fuzz
def test_pdf_Gates_Gaudin_Schuhman_basis_integral_fuzz():
    '''Note: Test takes 10x longer with the quad/points.
    '''
    
    analytical_vales = []
    numerical_values = []
    
    for n in [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
        # Errors at -2 (well, prevision loss anyway)
        for dmax in [1e-3, 1e-2, 2e-2, 3e-2, 4e-2, 5e-2, 6e-2, 7e-2, 8e-2, 1e-1]:
            dmax = dmax/100 # d cannot be larger than dmax
            analytical = (pdf_Gates_Gaudin_Schuhman_basis_integral(dmax, 1E-3, 2.3, n)
                          - pdf_Gates_Gaudin_Schuhman_basis_integral(1E-20, 1E-3, 2.3, n))
    
            to_int = lambda d : d**n*pdf_Gates_Gaudin_Schuhman(d, 1E-3, 2.3)
#            points = np.logspace(np.log10(dmax/2000), np.log10(dmax*.999), 30)
            numerical = quad(to_int, 1E-20, dmax)[0] # points=points
            analytical_vales.append(analytical)
            numerical_values.append(numerical)
            # The precision here is amazing actually, 1e-14 passes
#            assert_allclose(analytical, numerical, rtol=1E-7)
    assert_allclose(analytical_vales, numerical_values, rtol=1E-7)
    
def test_cdf_Rosin_Rammler():
    cdf = cdf_Rosin_Rammler(5E-2, 200, 2)
    assert_allclose(cdf, 0.3934693402873667)
    
    
def test_pdf_Rosin_Rammler():
    '''
from sympy import *
d, k, n = symbols('d, k, n')
model = 1 - exp(-k*d**n)
print(latex(diff(model, d)))    '''
    pdf = pdf_Rosin_Rammler(1E-3, 200, 2)
    assert_allclose(pdf, 0.3999200079994667)
    
    # quad
    to_quad = lambda d: pdf_Rosin_Rammler(d, 200, 2)
    cdf_int = quad(to_quad, 0, 5e-2)[0]
    cdf_known = cdf_Rosin_Rammler(5E-2, 200, 2)
    assert_allclose(cdf_int, cdf_known)
    
    assert_allclose(1, quad(to_quad, 0, 5)[0])
    
    assert 0 == pdf_Rosin_Rammler(0, 200, 2)
    
    
def test_pdf_Rosin_Rammler_basis_integral():

    ans = pdf_Rosin_Rammler_basis_integral(5E-2, 200, 2, 3)
    assert_allclose(ans, -0.00045239898439007338)
    
    # Test no error
    pdf_Rosin_Rammler_basis_integral(0, 200, 2, 3)

@pytest.mark.slow
@pytest.mark.fuzz
def test_pdf_Rosin_Rammler_basis_integral_fuzz():
    for n in [1.0, 2.0, 3.0]:
        # Lower dmaxes have 
        for dmax in [ 1e-3, 1e-2, 2e-2, 3e-2, 4e-2, 5e-2, 6e-2, 7e-2, 8e-2, 1e-1]:
            analytical = (pdf_Rosin_Rammler_basis_integral(dmax, 200, 2, n)
                          - pdf_Rosin_Rammler_basis_integral(1E-20, 200, 2, n))
    
            to_int = lambda d : d**n*pdf_Rosin_Rammler(d, 200, 2)
            points = np.logspace(np.log10(dmax/2000), np.log10(dmax*.999), 30)
            numerical = quad(to_int, 1E-20, dmax, points=points)[0]
            assert_allclose(analytical, numerical, rtol=1E-5)


def testPSDLognormal_meshes():
    a = PSDLognormal(s=0.5, d_characteristic=5E-6)
    ds_expect = [5.011872336272722e-07, 6.309573444801932e-07, 7.943282347242815e-07, 1e-06]
    ds = a.ds_discrete(dmax=1e-6, method='R10', pts=4)
    assert_allclose(ds_expect, ds)
    
    ds = a.ds_discrete(dmin=1e-6, method='R10', pts=4)
    assert_allclose(ds, [1e-06, 1.2589254117941672e-06, 1.5848931924611134e-06, 1.9952623149688796e-06])


@pytest.mark.slow
def test_PSDLognormal_mean_sizes_numerical():
    '''Takes like 10 seconds.
    '''
    # ISO standard example, done numerically
    a = PSDLognormal(s=0.5, d_characteristic=5E-6)
    ds = a.ds_discrete(dmax=1, pts=1E5)
    fractions = a.fractions_discrete(ds)
    
    disc = ParticleSizeDistribution(ds=ds, fractions=fractions)
    d20 = disc.mean_size(2, 0)
    assert_allclose(d20, 3.033E-6, rtol=0, atol=1E-9)
    
    d10 = disc.mean_size(1, 0)
    assert_allclose(d10, 2.676E-6, rtol=0, atol=1E-9)
    
    d21 = disc.mean_size(2, 1)
    assert_allclose(d21, 3.436E-6, rtol=0, atol=1E-9)
    
    d32 = disc.mean_size(3, 2)
    # Does match, need 6E6 pts to get the last digit to round right
    assert_allclose(d32, 4.412E-6, rtol=0, atol=1E-9)
    
    d43 = disc.mean_size(4, 3)
    assert_allclose(d43, 5.666E-6, rtol=0, atol=1E-9)
    
    d33 = disc.mean_size(3.0, 3.0)
    assert_allclose(d33, 5.000E-6, rtol=0, atol=1E-9)
    
    d00 = disc.mean_size(0.0, 0.0)
    assert_allclose(d00, 2.362E-6, rtol=0, atol=1E-9)

@pytest.mark.slow
def test_PSDCustom_mean_sizes_numerical():
    distribution = scipy.stats.lognorm(s=0.5, scale=5E-6)
    disc = PSDCustom(distribution)
    
    d20 = disc.mean_size(2, 0)
    assert_allclose(d20, 3.0326532985631672e-06, rtol=1E-8)
    
    d10 = disc.mean_size(1, 0)
    assert_allclose(d10, 2.6763071425949508e-06, rtol=1E-8)
    
    d21 = disc.mean_size(2, 1)
    assert_allclose(d21, 3.4364463939548618e-06, rtol=1E-8)
    
    d32 = disc.mean_size(3, 2)
    assert_allclose(d32, 4.4124845129229773e-06, rtol=1E-8)
    
    d43 = disc.mean_size(4, 3)
    assert_allclose(d43, 5.6657422653341318e-06, rtol=1E-3)


def test_PSDLognormal_mean_sizes_analytical():
    disc = PSDLognormal(s=0.5, d_characteristic=5E-6)
    
    d20 = disc.mean_size(2, 0)
    assert_allclose(d20, 3.033E-6, rtol=0, atol=1E-9)
    assert_allclose(d20, 3.0326532985631672e-06, rtol=1E-12)
    assert_allclose(d20, disc.mean_size_ISO(2, 0), rtol=1E-12)


    d10 = disc.mean_size(1, 0)
    assert_allclose(d10, 2.676E-6, rtol=0, atol=1E-9)
    assert_allclose(d10, 2.6763071425949508e-06, rtol=1E-12)
    assert_allclose(d10, disc.mean_size_ISO(1, 0), rtol=1E-12)

    d21 = disc.mean_size(2, 1)
    assert_allclose(d21, 3.436E-6, rtol=0, atol=1E-9)
    assert_allclose(d21, 3.4364463939548618e-06, rtol=1E-12)
    assert_allclose(d21, disc.mean_size_ISO(1, 1), rtol=1E-12)


    d32 = disc.mean_size(3, 2)
    assert_allclose(d32, 4.412E-6, rtol=0, atol=1E-9)
    assert_allclose(d32, 4.4124845129229773e-06, rtol=1E-12)
    assert_allclose(d32, disc.mean_size_ISO(1, 2), rtol=1E-12)

    d43 = disc.mean_size(4, 3)
    assert_allclose(d43, 5.666E-6, rtol=0, atol=1E-9)
    assert_allclose(d43, 5.6657422653341318e-06, rtol=1E-12)
    assert_allclose(d43, disc.mean_size_ISO(1, 3), rtol=1E-12)

    # There guys - need more work
#    d33 = disc.mean_size(3.0, 3.0)
#    assert_allclose(d33, 5.000E-6, rtol=0, atol=1E-9)
#    
#    d00 = disc.mean_size(0.0, 0.0)
#    assert_allclose(d00, 2.362E-6, rtol=0, atol=1E-9)

def test_PSDLognormal_ds_discrete():
    ds_discrete_expect = [2.4920844782646124e-07, 5.870554386661556e-07, 1.3829149496067687e-06, 3.2577055451375563e-06, 7.674112874286059e-06, 1.8077756749742233e-05, 4.258541598963051e-05, 0.0001003176268004454]
    dist = PSDLognormal(s=0.5, d_characteristic=5E-6)
    # Test the defaults
    assert_allclose(dist.ds_discrete(pts=8), ds_discrete_expect, rtol=1e-4)
    
    ds_discrete_expect = [1e-07, 1.389495494373139e-07, 1.9306977288832497e-07, 2.6826957952797275e-07, 3.727593720314938e-07, 5.179474679231213e-07, 7.196856730011514e-07, 1e-06]
    # Test end and minimum points
    assert_allclose(dist.ds_discrete(dmin=1e-7, dmax=1e-6, pts=8), ds_discrete_expect, rtol=1e-12)


def test_PSDLognormal_ds_discrete():
    # Test the cdf discrete
    dist = PSDLognormal(s=0.5, d_characteristic=5E-6)
    ds = dist.ds_discrete(dmin=1e-7, dmax=1e-6, pts=8)
    ans = dist.fractions_discrete(ds)
    fractions_expect = [2.55351295663786e-15, 3.831379657981415e-13, 3.762157252396037e-11, 2.41392961175535e-09, 1.01281244724305e-07, 2.7813750147487326e-06, 5.004382447515443e-05, 0.00059054208024234]
    assert_allclose(fractions_expect, ans, rtol=1e-5)


def test_PSDLognormal_dn():
    disc = PSDLognormal(s=0.5, d_characteristic=5E-6)
    
    # Test input of 1
    ans = disc.dn(1)
    # The answer can vary quite a lot near the end, so it is safest just to 
    # compare with the reverse, plugging it back to cdf
    assert_allclose(disc.cdf(ans), 1, rtol=1E-12)
#    assert_allclose(ans, 0.0002964902595794474)
    
    # Test zero input
    assert_allclose(disc.dn(0), 0)
    
    # Test 50% input
    ans = disc.dn(.5)
    assert_allclose(ans,  5.0e-06, rtol=1E-6)
    
    with pytest.raises(Exception):
        disc.dn(1.5)
    with pytest.raises(Exception):
        disc.dn(-.5)
        
    # Other orders of n - there is no comparison data for this yet!!
    assert_allclose(disc.pdf(1E-5), disc.pdf(1E-5, 3))
    assert_allclose(disc.pdf(1E-5, 2), 13468.122877854335)
    assert_allclose(disc.pdf(1E-5, 1), 4628.2482296943508)
    assert_allclose(disc.pdf(1E-5, 0), 1238.6613794833427)
    
    # Some really large s tests - found some issues with this
    dist = PSDLognormal(s=4, d_characteristic=5E-6)
    assert_allclose(dist.dn(1e-15), 8.220922763476676e-20, rtol=1e-3)
    assert_allclose(dist.dn(.99999999), 28055.285560763594)
    
    assert_allclose(dist.dn(1e-9), 1.904197766691136e-16, rtol=1e-4)
    assert_allclose(dist.dn(1-1e-9), 131288.88851649483, rtol=1e-4)
    
        

def test_PSDLognormal_dn_order_0_1_2():
    '''Simple point to test where the order of n should be 0
    
    Yes, the integrals need this many points (which makes them slow) to get
    the right accuracy. They've been tested and reduced already quite a bit.
    '''
    # test 2, 0 -> 2, 0
    disc = PSDLognormal(s=0.5, d_characteristic=5E-6)
    to_int = lambda d: d**2*disc.pdf(d=d, n=0)
    points  = [5E-6*i for i in np.logspace(np.log10(.1), np.log10(50), 8)]
    
    ans_numerical = (quad(to_int, 1E-7, 5E-3, points=points)[0])**0.5
    ans_analytical = 3.0326532985631672e-06
    # The integral is able to give over to decimals!
    assert_allclose(ans_numerical, ans_analytical, rtol=1E-10)
       
    # test 2, 1 -> 1, 1 integrated pdf
    
    to_int = lambda d: d*disc.pdf(d=d, n=1)    
    ans_numerical = (quad(to_int, 1E-7, 5E-3, points=points)[0])**1
    ans_analytical = 3.4364463939548618e-06
    assert_allclose(ans_numerical, ans_analytical, rtol=1E-10)
    
    # test 3, 2 -> 1, 2 integrated pdf
    
    to_int = lambda d: d*disc.pdf(d=d, n=2)    
    ans_numerical = (quad(to_int, 1E-7, 5E-3, points=points)[0])**1
    ans_analytical = 4.4124845129229773e-06
    assert_allclose(ans_numerical, ans_analytical, rtol=1E-8)
    
    
def test_PSDLognormal_cdf_orders():
    # Test cdf of different orders a bunch
    disc = PSDLognormal(s=0.5, d_characteristic=5E-6)
    # 16 x 4 = 64 points
    # had 1e-7 here too as a diameter but too many numerical issues, too sensitive to rounding
    # errors
    ds = [2E-6, 3E-6, 4E-6, 5E-6, 6E-6, 7E-6, 1E-5, 2E-5, 3E-5, 5E-5, 7E-5, 1E-4, 2E-4, 4E-4, 1E-3]
    ans_expect = [[ 0.36972511868508068, 0.68379899882263917, 0.8539928088656249, 0.93319279873114203, 0.96888427729983861, 0.98510775165387254, 0.99805096305713792, 0.9999903391682271, 0.99999981474719135, 0.99999999948654394, 0.99999999999391231, 0.99999999999996592, 1.0, 1.0, 1.0], 
                  [ 0.20254040832522924, 0.49136307673913149, 0.71011232639847854, 0.84134474606854293, 0.91381737643345484, 0.95283088619207579, 0.99149043874391107, 0.99991921875653167, 0.99999771392273817, 0.99999998959747816, 0.99999999982864851, 0.99999999999863987, 1.0, 1.0, 1.0000000000000002],
                  [ 0.091334595732478097, 0.30095658738958564, 0.52141804648990697, 0.69146246127401301, 0.80638264936531323, 0.87959096325267294, 0.9703723506333426, 0.999467162897961, 0.99997782059383122, 0.99999983475152954, 0.99999999622288382, 0.99999999995749711, 0.99999999999999833, 1.0000000000000002, 1.0000000000000002], 
                  [ 0.033432418408916864, 0.15347299656473007, 0.3276949357115424, 0.5, 0.64231108623683952, 0.74950869138681098, 0.91717148099830148, 0.99721938213769046, 0.99983050191355338, 0.99999793935660408, 0.99999993474010451, 0.99999999896020164, 0.99999999999991951, 1.0, 1.0]]

    calc = []
    for n in range(0, 4):
        calc.append([disc.cdf(i, n=n) for i in ds])
    
    assert_allclose(ans_expect, calc, rtol=1E-9)    
    
    
def test_PSDLognormal_cdf_vs_pdf():
    
    # test PDF against CDF
    
    disc = PSDLognormal(s=0.5, d_characteristic=5E-6)
    ans_calc = []
    ans_expect = []
    for i in range(5):
        # Pick a random start
        start = uniform(0, 1)
        end = uniform(start, 1)
        d_start = disc.dn(start)
        d_end = disc.dn(end)
    
        delta = disc.cdf(d_end) - disc.cdf(d_start)
        delta_numerical = quad(disc.pdf, d_start, d_end)[0]
        ans_calc.append(delta_numerical)
        ans_expect.append(delta)
    assert_allclose(ans_calc, ans_expect)
    
@pytest.mark.slow
def test_PSD_PSDlognormal_area_length_count():
    '''Compare the average difference between the analytical values for a
    lognormal distribution with those of a discretized form of it.Note simply
    adding more points did not tend to help reduce the error.
    For the particle count case, 700 points has the lowest error.
    
    fractions_discrete is still the slowest part.
    '''
    dist = PSDLognormal(s=0.5, d_characteristic=5E-6)
    
    ds = dist.ds_discrete(pts=700, dmin=2E-7, dmax=1E-4)
    fractions = dist.fractions_discrete(ds)
    psd = ParticleSizeDistribution(ds=ds, fractions=fractions)
    # Trim a few at the start and end
    ans = np.array(psd.number_fractions)[5:-5]/np.array(dist.fractions_discrete(ds, n=0))[5:-5]
    avg_err = sum(np.abs(ans - 1.0))/len(ans)
    assert 5E-4 > avg_err
    
    ans = np.array(psd.length_fractions)[5:-5]/np.array(dist.fractions_discrete(ds, n=1))[5:-5]
    avg_err = sum(np.abs(ans - 1.0))/len(ans)
    assert 1E-4 > avg_err
    
    ans = np.array(psd.area_fractions)[5:-5]/np.array(dist.fractions_discrete(ds, n=2))[5:-5]
    avg_err = sum(np.abs(ans - 1.0))/len(ans)
    assert 1E-4 > avg_err
    
def test_PSDInterpolated_pchip():
    '''For this test, ds is the same length as fractions, and we begin the series with the zero point.
    
    Half the test is spend on the `dn` solver tests, and the other half is just
    that these tests are slow.
    '''
    ds = [360, 450, 562.5, 703, 878, 1097, 1371, 1713, 2141, 2676, 3345, 4181, 5226, 6532]
    ds = np.array(ds)/1e6
    numbers = [65, 119, 232, 410, 629, 849, 990, 981, 825, 579, 297, 111, 21, 1]
    dist = ParticleSizeDistribution(ds=ds, numbers=numbers)
    psd = PSDInterpolated(dist.Dis, dist.fractions)
    
    assert len(psd.fractions) == len(psd.ds)
    assert len(psd.fractions) == 15
    # test fractions_discrete vs input
    assert_allclose(psd.fractions_discrete(ds), dist.fractions)
    
    # test cdf_discrete
    assert_allclose(psd.cdf_discrete(ds), psd.cdf_fractions[1:])
    
    # test that dn solves backwards for exactly the right value
    cumulative_fractions = np.cumsum(dist.fractions)
    ds_for_fractions = np.array([psd.dn(f) for f in cumulative_fractions])
    assert_allclose(ds, ds_for_fractions)
    
    # test _pdf
    test_pdf = psd._pdf(1e-3)
    assert_allclose(test_pdf, 106.28284463095554)
    
    # test _cdf
    test_cdf = psd._cdf(1e-3)
    assert_allclose(test_cdf, 0.02278897476363087)
    
    # test _pdf_basis_integral
    test_int = psd._pdf_basis_integral(1e-3, 2)
    assert_allclose(test_int, 1.509707233427664e-08)
    
    # Check that the 0 point is created and the points and fractions are the same
    assert_allclose(psd.ds, [0] + ds.tolist())
    assert_allclose(psd.fractions, [0] + dist.fractions)
    
    # test mean_size
    test_mean = psd.mean_size(3, 2)
    assert_allclose(test_mean, 0.002211577679574544)    


def test_PSDInterpolated_discrete():
    ds = [360, 450, 562.5, 703, 878, 1097, 1371, 1713, 2141, 2676, 3345, 4181, 5226, 6532]
    ds = np.array(ds)/1e6
    numbers = [65, 119, 232, 410, 629, 849, 990, 981, 825, 579, 297, 111, 21, 1]
    psd = ParticleSizeDistribution(ds=ds, numbers=numbers)
    # test fractions_discrete vs input
    assert_allclose(psd.fractions_discrete(ds), psd.fractions)
    
    # test cdf_discrete
    assert_allclose(psd.cdf_discrete(ds), psd.interpolated.cdf_fractions[1:])
    # test that dn solves backwards for exactly the right value
    cumulative_fractions = np.cumsum(psd.fractions)
    ds_for_fractions = np.array([psd.dn(f) for f in cumulative_fractions])
    assert_allclose(ds, ds_for_fractions)
    
    
    # test _pdf
    test_pdf = psd.pdf(1e-3)
    assert_allclose(test_pdf, 106.28284463095554)
    
    # test _cdf
    test_cdf = psd.cdf(1e-3)
    assert_allclose(test_cdf, 0.02278897476363087)
    
    # test _pdf_basis_integral
    test_int = psd._pdf_basis_integral(1e-3, 2)
    assert_allclose(test_int, 1.509707233427664e-08)
    
    assert not np.isclose(psd.mean_size(3, 2), psd.interpolated.mean_size(3, 2))

    
def test_psd_spacing():
    ans_log = psd_spacing(dmin=1, dmax=10, pts=4, method='logarithmic')
    ans_log_expect = [1.0, 2.154434690031884, 4.641588833612778, 10.0]
    assert_allclose(ans_log, ans_log_expect)
    
    ans_lin = psd_spacing(dmin=0, dmax=10, pts=4, method='linear')
    ans_lin_expect = [0.0, 3.3333333333333335, 6.666666666666667, 10.0]
    assert_allclose(ans_lin, ans_lin_expect)
    
    with pytest.raises(Exception):
        psd_spacing(dmin=0, dmax=10, pts=8, method='R5')
        
    # This example from an iso standard, ISO 9276-2 2014
    ans_R5 = psd_spacing(dmax=25, pts=8, method='R5')
    ans_R5_expect = [0.9952679263837426, 1.5773933612004825, 2.499999999999999, 3.9622329811527823, 6.279716078773949, 9.95267926383743, 15.77393361200483, 25]
    assert_allclose(ans_R5, ans_R5_expect)
    ans_R5_reversed = psd_spacing(dmin=0.9952679263837426, pts=8, method='R5')
    assert_allclose(ans_R5_reversed, ans_R5_expect)
    
    ans_R5_float = psd_spacing(dmax=25, pts=8, method='R5.00000001')
    assert_allclose(ans_R5_float, ans_R5_expect)
    
    ans = psd_spacing(dmin=5e-5, dmax=1e-3, method='ISO 3310-1')
    ans_expect = [5e-05, 5.3e-05, 5.6e-05, 6.3e-05, 7.1e-05, 7.5e-05, 8e-05, 9e-05, 0.0001, 0.000106, 0.000112, 0.000125, 0.00014, 0.00015, 0.00016, 0.00018, 0.0002, 0.000212, 0.000224, 0.00025, 0.00028, 0.0003, 0.000315, 0.000355, 0.0004, 0.000425, 0.00045, 0.0005, 0.00056, 0.0006, 0.00063, 0.00071, 0.0008, 0.00085, 0.0009, 0.001]
    assert_allclose(ans, ans_expect)
    assert [] == psd_spacing(dmin=0, dmax=1e-6, method='ISO 3310-1')
    assert [] == psd_spacing(dmin=1, dmax=1e2, method='ISO 3310-1')
    
    assert psd_spacing(dmin=5e-5, dmax=1e-3, method='ISO 3310-1 R20')
    assert psd_spacing(dmin=5e-5, dmax=1e-3, method='ISO 3310-1 R20/3')
    assert psd_spacing(dmin=5e-5, dmax=1e-3, method='ISO 3310-1 R40/3')
    assert psd_spacing(dmin=0e-5, dmax=1e-3, method='ISO 3310-1 R10')
    
    ds = psd_spacing(dmin=1e-5, dmax=1e-4, method='ASTM E11')
    ds_expect = [2e-05, 2.5e-05, 3.2e-05, 3.8e-05, 4.5e-05, 5.3e-05, 6.3e-05, 7.5e-05, 9e-05]
    assert_allclose(ds, ds_expect)