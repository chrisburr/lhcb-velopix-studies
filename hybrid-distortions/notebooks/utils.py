from glob import glob
from itertools import tee
from functools import wraps
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from joblib import delayed, Parallel

D0_mass = 1864.84
speed_of_light = 299792458

# Change the default settings for plotting
# os.environ['PATH'] = '/pc2014-data3/cburr/texlive/2016/bin/x86_64-linux/:' + os.environ['PATH']
# plt.rcParams['figure.dpi'] = 100
# plt.rcParams['figure.figsize'] = [9.0, 6.0]
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['text.usetex'] = True
# plt.rcParams['text.latex.unicode'] = True
# plt.rcParams['text.latex.preamble'] = r"""
# \usepackage[T1]{fontenc}
# \usepackage{amsmath}
# \usepackage{amsfonts}
# \usepackage{amssymb}
# \usepackage{tgheros}
# \usepackage[tx]{sfmath}
# \usepackage{siunitx}
# """

# Do some monkey patching to fix pandas/#15296
if not hasattr(pd.read_msgpack, 'read_msgpack'):
    @wraps(pd.read_msgpack)
    def read_msgpack(*args, **kwargs):
        df = read_msgpack.read_msgpack(*args, **kwargs)
        if isinstance(df, list):
            df = pd.concat(df)
        df.columns = [c.decode('utf-8') for c in df.columns]
        return df

    read_msgpack.read_msgpack = pd.read_msgpack
    pd.read_msgpack = read_msgpack

# Helpful function
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def _load(df_name, scenarios, n_files):
    dfs = []
    for scenario in scenarios:
        valid = False
        for i in range(n_files):
            fn = f'output/scenarios/{scenario}/{df_name}_{i}.msg'
            if os.path.isfile(fn):
                print('Found', fn)
                df = pd.read_msgpack(fn)
                df['scenario'] = pd.Categorical([scenario]*len(df), categories=scenarios)
                dfs.append(df)
                valid = True
            else:
                print('Skipping', fn)
        if not valid:
            raise ValueError(scenario, df_name)
    return df_name, pd.concat(dfs)

def load(scenarios=None, names=['clusters', 'tracks', 'residuals', 'particles'], fast=False):
    if scenarios is None:
        scenarios = []
        for scenario in glob('output/scenarios/*/particles_0.msg'):
            scenarios.append(scenario[len('output/scenarios/'):-len('/particles_0.msg')])

    data = Parallel(n_jobs=4, backend='threading')(
        delayed(_load)(n, scenarios, [10, 1][fast]) for n in names
    )
    data = dict(data)

    if 'residuals' in names:
        data['residuals']['station'] = np.floor_divide(data['residuals'].module, 2)
        data['residuals']['station'] = data['residuals']['station'].astype('category')
        data['residuals'] = {k: v for k, v in data['residuals'].groupby('scenario')}

    if 'tracks' in names:
        data['tracks'].track_type = list(map(lambda s: s.decode('utf-8'), data['tracks'].track_type))
        data['tracks'].track_type = data['tracks'].track_type.astype('category')

        data['tracks'].eval('p = sqrt(px**2 + py**2 + pz**2)', inplace=True)
        data['tracks'].eval('pt = sqrt(px**2 + py**2)', inplace=True)
        data['tracks'].eval('true_p = sqrt(true_px**2 + true_py**2 + true_pz**2)', inplace=True)
        data['tracks'].eval('true_pt = sqrt(true_px**2 + true_py**2)', inplace=True)

    if 'particles' in names:
        data['particles'].eval('fd = sqrt('
            '(vertex_x - pv_x)**2 + '
            '(vertex_y - pv_y)**2 + '
            '(vertex_z - pv_z)**2'
        ')', inplace=True)

        data['particles'].eval('half_true_fd = sqrt('
            '(vertex_x - true_dst_vertex_x)**2 + '
            '(vertex_y - true_dst_vertex_y)**2 + '
            '(vertex_z - true_dst_vertex_z)**2'
        ')', inplace=True)

        data['particles'].eval('true_fd = sqrt('
            '(true_d0_vertex_x - true_dst_vertex_x)**2 + '
            '(true_d0_vertex_y - true_dst_vertex_y)**2 + '
            '(true_d0_vertex_z - true_dst_vertex_z)**2'
        ')', inplace=True)
        data['particles'].eval('D0_p = sqrt(D0_p_x**2 + D0_p_y**2 + D0_p_z**2)', inplace=True)
        data['particles'].eval(f'D0_gamma = 1/sqrt(1 + D0_p**2/{D0_mass**2})', inplace=True)


    return tuple([data[k] for k in names])

def format_label(s):
    if s == 'Original_DB' or s == 'Nominal':
        return 'Nominal'
    elif s.startswith('tip_x=0um_y='):
        s = s[len('tip_x=0um_y='):]
        s = s.split('_sigma=')
        if len(s) == 2:
            mu, sigma = s
            sigma = f' $\sigma$ = {sigma}$\mu$m'
        else:
            mu, = s
            sigma = ''
        return f'$\mu$ = {mu[:-2]}$\mu$m{sigma}'
    else:
        raise ValueError(s)