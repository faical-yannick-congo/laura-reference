import numpy as np
from scipy.interpolate import griddata
import glob, os
import re
from refdb.common.models import SetModel
from refdb.common.models import ReferenceModel
import matplotlib
import matplotlib.markers as mark
from matplotlib.markers import MarkerStyle
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import lines as plotline
from matplotlib.pyplot import show, plot, ion, figure
import random
from sklearn.metrics import mean_absolute_error

def htmlcolor(r, g, b):
    def _chkarg(a):
        if isinstance(a, int): # clamp to range 0--255
            if a < 0:
                a = 0
            elif a > 255:
                a = 255
        elif isinstance(a, float): # clamp to range 0.0--1.0 and convert to integer 0--255
            if a < 0.0:
                a = 0
            elif a > 1.0:
                a = 255
            else:
                a = int(round(a*255))
        else:
            raise ValueError('Arguments must be integers or floats.')
        return a
    r = _chkarg(r)
    g = _chkarg(g)
    b = _chkarg(b)
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)

class SetPlot:

    def __init__(self, set_id=None):
        self.set = SetModel.objects.with_id(set_id)

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        a1_r1 = []
        a1_r1.append(self.set.raw_pressure['aliq1']['run1'])
        a1_r1.append(self.set.raw_uptake['aliq1']['run1'])
        a1_r2 = []
        a1_r2.append(self.set.raw_pressure['aliq1']['run2'])
        a1_r2.append(self.set.raw_uptake['aliq1']['run2'])

        a2_r1 = []
        a2_r1.append(self.set.raw_pressure['aliq2']['run1'])
        a2_r1.append(self.set.raw_uptake['aliq2']['run1'])
        a2_r2 = []
        a2_r2.append(self.set.raw_pressure['aliq2']['run2'])
        a2_r2.append(self.set.raw_uptake['aliq2']['run2'])

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(a1_r1[0], a1_r1[1], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq1-run1')
        plt.plot(a1_r2[0], a1_r2[1], 'bs', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq1-run2')

        color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(a2_r1[0], a2_r1[1], 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq2-run1')
        plt.plot(a2_r2[0], a2_r2[1], 'bs', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('aliq2-run2')
        
        plt.axis([0, 1.2*max(a1_r1[0]+a1_r2[0]+a2_r1[0]+a2_r2[0]), 0, 1.2*max(a1_r1[1]+a1_r2[1]+a2_r1[1]+a2_r2[1])])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)

        self.set_path = 'plots/set-{0}.png'.format(str(self.set.id))
        plt.savefig(self.set_path)
        plt.close()


class Build:

    def __init__(self, ref=None):
        if ref:
            self.ref = ref
            self.sets = []
            for _set_id in self.ref.sets['sets']:
                _set = SetModel.objects.with_id(_set_id['id'])
                if _set:
                    self.sets.append(_set.info())
            self.average  = {'aliq1':{'pressure':[], 'uptake':[]}, 'aliq2':{'pressure':[], 'uptake':[]}}
            self.err_low = []
            self.err_up = []
            self.sizes = []

    def intervalls(self):
        pressure_a1 = {'min':self.sets[0]['raw-pressure']['aliq1']['run1'][0], 'max':self.sets[0]['raw-pressure']['aliq1']['run1'][-1]}

        pressure_a2 = {'min':self.sets[0]['raw-pressure']['aliq2']['run1'][0], 'max':self.sets[0]['raw-pressure']['aliq2']['run1'][-1]}
        
        uptake_a1 = {'min':self.sets[0]['raw-uptake']['aliq1']['run1'][0], 'max':self.sets[0]['raw-uptake']['aliq1']['run1'][-1]}

        uptake_a2 = {'min':self.sets[0]['raw-uptake']['aliq2']['run1'][0], 'max':self.sets[0]['raw-uptake']['aliq2']['run1'][-1]}

        for _set in self.sets:
            print str(_set)
            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure_a1['min'] >= a1_r1:
                    pressure_a1['min'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure_a1['min'] >= a1_r2:
                    pressure_a1['min'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure_a2['min'] >= a2_r1:
                    pressure_a2['min'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure_a2['min'] >= a2_r2:
                    pressure_a2['min'] = a2_r2


            for a1_r1 in _set['raw-pressure']['aliq1']['run1']:
                if pressure_a1['max'] <= a1_r1:
                    pressure_a1['max'] = a1_r1
            for a1_r2 in _set['raw-pressure']['aliq1']['run2']:
                if pressure_a1['max'] <= a1_r2:
                    pressure_a1['max'] = a1_r2

            for a2_r1 in _set['raw-pressure']['aliq2']['run1']:
                if pressure_a2['max'] <= a2_r1:
                    pressure_a2['max'] = a2_r1
            for a2_r2 in _set['raw-pressure']['aliq2']['run2']:
                if pressure_a2['max'] <= a2_r2:
                    pressure_a2['max'] = a2_r2

            ####
            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake_a1['min'] >= a1_r1:
                    uptake_a1['min'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake_a1['min'] >= a1_r2:
                    uptake_a1['min'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake_a2['min'] >= a2_r1:
                    uptake_a2['min'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake_a2['min'] >= a2_r2:
                    uptake_a2['min'] = a2_r2


            for a1_r1 in _set['raw-uptake']['aliq1']['run1']:
                if uptake_a1['max'] <= a1_r1:
                    uptake_a1['max'] = a1_r1
            for a1_r2 in _set['raw-uptake']['aliq1']['run2']:
                if uptake_a1['max'] <= a1_r2:
                    uptake_a1['max'] = a1_r2

            for a2_r1 in _set['raw-uptake']['aliq2']['run1']:
                if uptake_a2['max'] <= a2_r1:
                    uptake_a2['max'] = a2_r1
            for a2_r2 in _set['raw-uptake']['aliq2']['run2']:
                if uptake_a2['max'] <= a2_r2:
                    uptake_a2['max'] = a2_r2

        return [pressure_a1, uptake_a1, pressure_a2, uptake_a2]



    def compute(self):
        sizes = self.intervalls()
        fine_grid_a1 = np.linspace(0, sizes[0]['max'], num=int(sizes[0]['max']/0.1), endpoint=True)
        fine_grid_a2 = np.linspace(0, sizes[2]['max'], num=int(sizes[1]['max']/0.1), endpoint=True)

        #grid_p_a1, grid_u_a1 = np.mgrid[0:sizes[0]['max']:int(sizes[0]['max']/0.1), 0:sizes[1]['max']:int(sizes[1]['max']/0.1)]
        # grid_p_a2, grid_u_a2 = np.mgrid[0:sizes[2]['max']:int(sizes[2]['max']/0.1), 0:sizes[3]['max']:int(sizes[3]['max']/0.1)]

        av_a1 = np.zeros(len(fine_grid_a1))
        av_a2 = np.zeros(len(fine_grid_a2))
        a1_U = []
        a2_U = []
        for _set in self.sets:
            # average pressures
            print "Adding set: {0}".format(_set['filename'])
            _set['ref-pressure'] = {'aliq1':{'run1':fine_grid_a1, 'run2':fine_grid_a1}, 'aliq2':{'run1':fine_grid_a2, 'run2':fine_grid_a2}}
            _set['ref-uptake'] = {'aliq1':{'run1':[], 'run2':[]}, 'aliq2':{'run1':[], 'run2':[]}}
            
            if len(_set['raw-pressure']['aliq1']['run1']) >0:
                _set['ref-uptake']['aliq1']['run1'] = np.interp(_set['ref-pressure']['aliq1']['run1'], _set['raw-pressure']['aliq1']['run1'], _set['raw-uptake']['aliq1']['run1'], left=None, right=None, period=None)
                av_a1 = av_a1 + _set['ref-uptake']['aliq1']['run1']
                a1_U.append(_set['ref-uptake']['aliq1']['run1'])
            if len(_set['raw-pressure']['aliq1']['run2']) >0:
                _set['ref-uptake']['aliq1']['run2'] = np.interp(_set['ref-pressure']['aliq1']['run2'], _set['raw-pressure']['aliq1']['run2'], _set['raw-uptake']['aliq1']['run2'], left=None, right=None, period=None)
                av_a1 = av_a1 + _set['ref-uptake']['aliq1']['run2']
                a1_U.append(_set['ref-uptake']['aliq1']['run2'])

            if len(_set['raw-pressure']['aliq2']['run1']) >0:
                _set['ref-uptake']['aliq2']['run1'] = np.interp(_set['ref-pressure']['aliq2']['run1'], _set['raw-pressure']['aliq2']['run1'], _set['raw-uptake']['aliq2']['run1'], left=None, right=None, period=None)
                av_a2 = av_a2 + _set['ref-uptake']['aliq2']['run1']
                a2_U.append(_set['ref-uptake']['aliq2']['run1'])
            if len(_set['raw-pressure']['aliq2']['run2']) >0:
                _set['ref-uptake']['aliq2']['run2'] = np.interp(_set['ref-pressure']['aliq2']['run2'], _set['raw-pressure']['aliq2']['run2'], _set['raw-uptake']['aliq2']['run2'], left=None, right=None, period=None)
                av_a2 = av_a2 + _set['ref-uptake']['aliq2']['run2']
                a2_U.append(_set['ref-uptake']['aliq2']['run2'])


        # av_a1 = av_a1 / 2*len(self.sets)
        # av_a2 = av_a2 / 2*len(self.sets)

        av_a1 = np.average(a1_U, axis=0)
        av_a2 = np.average(a2_U, axis=0)

        mn_a1 = np.mean(a1_U, axis=0)
        mn_a2 = np.mean(a2_U, axis=0)

        md_a1 = np.median(a1_U, axis=0)
        md_a2 = np.median(a2_U, axis=0)

        sd_a1 = np.std(a1_U, axis=0)
        sd_a2 = np.std(a2_U, axis=0)


        self.ref.sd_uptake = {'aliq1':sd_a1, 'aliq2':sd_a2}
        self.ref.av_uptake = {'aliq1':av_a1, 'aliq2':av_a2}
        self.ref.mn_uptake = {'aliq1':mn_a1, 'aliq2':mn_a2}
        self.ref.md_uptake = {'aliq1':md_a1, 'aliq2':md_a2}
        self.ref.fit_pressure = {'aliq1':fine_grid_a1, 'aliq2':fine_grid_a2}
        self.ref.sizes = {'aliq1':{'pressure':sizes[0], 'uptake':sizes[1]}, 'aliq2':{'pressure':sizes[2], 'uptake':sizes[3]}}
        # Polynomial with 30 components is enough to fit the curb.
        z_1 = np.polyfit(fine_grid_a1, mn_a1, 30)
        z_2 = np.polyfit(fine_grid_a2, mn_a2, 30)
        self.ref.formula = {'aliq1':z_1.tolist(), 'aliq2':z_2.tolist()}
        self.ref.save()

    def plot_raw(self, aliq=1):
        _aliq = 'aliq{0}'.format(aliq)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        for _set in self.sets:
            run1 = []
            run1.append(_set['raw-pressure'][_aliq]['run1'])
            run1.append(_set['raw-uptake'][_aliq]['run1'])
            run2 = []
            run2.append(_set['raw-pressure'][_aliq]['run2'])
            run2.append(_set['raw-uptake'][_aliq]['run2'])

            color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            plt.plot(run1[0], run1[1], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            plt.plot(run2[0], run2[1], 'bs', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run2]'.format(_set['filename']))
        
        plt.axis([0, 1.2*self.ref.sizes['aliq1']['pressure']['max'], 0, 1.2*self.ref.sizes['aliq1']['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        # plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/ref-{0}-{1}.png'.format(str(self.ref.id), _aliq)
        plt.savefig(self.ref_path)
        plt.close()

    def plot_all(self):
        self.plot_raw(1)
        self.plot_raw(2)
        
    def plot_stats(self, aliq=1):
        _aliq = 'aliq{0}'.format(aliq)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.sd_uptake[_aliq], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('standard-deviation')

        color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.av_uptake[_aliq], 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('average')

        color3 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq], 'o', ms = float(5.0), color = color3, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('mean')

        color4 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.md_uptake[_aliq], 'o', ms = float(5.0), color = color4, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('median')
        
        plt.axis([0, 1.2*self.ref.sizes['aliq1']['pressure']['max'], 0, 1.2*self.ref.sizes['aliq1']['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/stats-ref-{0}-{1}.png'.format(str(self.ref.id), _aliq)
        plt.savefig(self.ref_path)
        plt.close()

    def plot_stat(self):
        self.plot_stats(1)
        self.plot_stats(2)

    def plot_error_bar(self, aliq=1):
        _aliq = 'aliq{0}'.format(aliq)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []
        for _set in self.sets:
            run1 = []
            run1.append(_set['raw-pressure'][_aliq]['run1'])
            run1.append(_set['raw-uptake'][_aliq]['run1'])
            run2 = []
            run2.append(_set['raw-pressure'][_aliq]['run2'])
            run2.append(_set['raw-uptake'][_aliq]['run2'])

            color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            plt.plot(run1[0], run1[1], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run1]'.format(_set['filename']))

            plt.plot(run2[0], run2[1], 'bs', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
            # legend.append('{0}[run2]'.format(_set['filename']))
        
        # color = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq], '^', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.fill_between(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq]+self.ref.sd_uptake[_aliq], self.ref.mn_uptake[_aliq]-self.ref.sd_uptake[_aliq], facecolor="red", alpha=0.5)

        p = np.poly1d(self.ref.formula[_aliq])
        plt.plot(self.ref.fit_pressure[_aliq], p(self.ref.fit_pressure[_aliq]), ms = float(5.0), color = "blue", mew = .25, ls = '--', lw = float(1.5), zorder = 3)
        
        plt.axis([0, 1.2*self.ref.sizes['aliq1']['pressure']['max'], 0, 1.2*self.ref.sizes['aliq1']['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        # plt.legend(legend, loc = 2, fontsize = 10)

        self.ref_path = 'plots/error-{0}-{1}.png'.format(str(self.ref.id), _aliq)
        plt.savefig(self.ref_path)
        plt.close()

    def plot_bars(self):
        self.plot_error_bar(1)
        self.plot_error_bar(2)


class Evaluation:
    def __init__(self, eval_id=None, reference=None, pressure=None, uptake=None):
        self.ref = reference
        self.eval_id = eval_id
        self.pressure = pressure
        self.uptake = uptake
        self.results = {}
        self.agrees = []

    def run(self):
        a1_U = []
        a2_U = []

        # g1_U = []
        # g2_U = []

        # Should i compare the runs with the mean by meaning them together?
        # Or mean the runs first and mean their mean with the reference mean.

        # average pressures
        # a1_U.append(self.ref.mn_uptake['aliq1'])
        if len(self.pressure['aliq1']['run1']) >0:
            ref1_a1 = np.interp(self.ref.fit_pressure['aliq1'], self.pressure['aliq1']['run1'], self.uptake['aliq1']['run1'], left=None, right=None, period=None)
            a1_U.append(ref1_a1)
        if len(self.pressure['aliq1']['run2']) >0:
            ref2_a1 = np.interp(self.ref.fit_pressure['aliq1'], self.pressure['aliq1']['run2'], self.uptake['aliq1']['run2'], left=None, right=None, period=None)
            a1_U.append(ref2_a1)

        # a2_U.append(self.ref.mn_uptake['aliq2'])
        if len(self.pressure['aliq2']['run1']) >0:
            ref1_a2 = np.interp(self.ref.fit_pressure['aliq2'], self.pressure['aliq2']['run1'], self.uptake['aliq2']['run1'], left=None, right=None, period=None)
            a2_U.append(ref1_a2)
        if len(self.pressure['aliq2']['run2']) >0:
            ref2_a2 = np.interp(self.ref.fit_pressure['aliq2'], self.pressure['aliq2']['run2'], self.uptake['aliq2']['run2'], left=None, right=None, period=None)
            a2_U.append(ref2_a2)

        av_a1 = np.average([np.mean(a1_U, axis=0), self.ref.mn_uptake['aliq1']], axis=0)
        av_a2 = np.average([np.mean(a2_U, axis=0), self.ref.mn_uptake['aliq2']], axis=0)

        mn_a1 = np.mean([np.mean(a1_U, axis=0), self.ref.mn_uptake['aliq1']], axis=0)
        mn_a2 = np.mean([np.mean(a2_U, axis=0), self.ref.mn_uptake['aliq2']], axis=0)

        md_a1 = np.median([np.mean(a1_U, axis=0), self.ref.mn_uptake['aliq1']], axis=0)
        md_a2 = np.median([np.mean(a2_U, axis=0), self.ref.mn_uptake['aliq2']], axis=0)

        sd_a1 = np.std([np.mean(a1_U, axis=0), self.ref.mn_uptake['aliq1']], axis=0)
        sd_a2 = np.std([np.mean(a2_U, axis=0), self.ref.mn_uptake['aliq2']], axis=0)

        self.results['std'] = {'aliq1':sd_a1.tolist(), 'aliq2':sd_a2.tolist()}
        self.results['av'] = {'aliq1':av_a1.tolist(), 'aliq2':av_a2.tolist()}
        self.results['mn'] = {'aliq1':mn_a1.tolist(), 'aliq2':mn_a2.tolist()}
        self.results['md'] = {'aliq1':md_a1.tolist(), 'aliq2':md_a2.tolist()}

        # The reference data set dispersion is bigger than the dispersion of the evaluated data set with the mean reference.
        # How is > working for lists.
        self.agrees = [self.ref.sd_uptake['aliq1'] > sd_a1.tolist(), self.ref.sd_uptake['aliq2'] > sd_a2.tolist()]

        macro_1 = mean_absolute_error(self.ref.mn_uptake['aliq1'], np.mean([ref1_a1, ref2_a1], axis=0).tolist())
        # micro_1 = f1_score(self.ref.mn_uptake['aliq1'], np.mean([ref1_a1, ref2_a1], axis=0).tolist(), average='micro')
        # weighted_1 = f1_score(self.ref.mn_uptake['aliq1'], np.mean([ref1_a1, ref2_a1], axis=0).tolist(), average='weighted')

        print "Macro Mean aliq1: {0}".format(str(macro_1))
        # print "Micro Mean aliq1: {0}".format(str(micro_1))
        # print "Weighted Mean aliq1: {0}".format(str(weighted_1))

        macro_2 = mean_absolute_error(self.ref.mn_uptake['aliq2'], np.mean([ref1_a2, ref2_a2], axis=0).tolist())
        # micro_2 = f1_score(self.ref.mn_uptake['aliq2'], np.mean([ref1_a2, ref2_a2], axis=0).tolist(), average='micro')
        # weighted_2 = f1_score(self.ref.mn_uptake['aliq2'], np.mean([ref1_a2, ref2_a2], axis=0).tolist(), average='weighted')

        print "Macro Mean aliq2: {0}".format(str(macro_2))
        # print "Micro Mean aliq2: {0}".format(str(micro_2))
        # print "Weighted Mean aliq2: {0}".format(str(weighted_2))
    def plot_result(self, _aliq="aliq1"):
        # _aliq = 'aliq{0}'.format(aliq)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        color1 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.results['std'][_aliq], 'o', ms = float(5.0), color = color1, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('standard-deviation')

        color2 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.results['av'][_aliq], 'o', ms = float(5.0), color = color2, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('average')

        color3 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.results['mn'][_aliq], 'o', ms = float(5.0), color = color3, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('mean')

        color4 = htmlcolor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        plt.plot(self.ref.fit_pressure[_aliq], self.results['md'][_aliq], 'o', ms = float(5.0), color = color4, mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        legend.append('median')
        
        plt.axis([0, 1.2*self.ref.sizes['aliq1']['pressure']['max'], 0, 1.2*self.ref.sizes['aliq1']['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.legend(legend, loc = 2, fontsize = 10)
        plt.draw()


    def plot(self, aliq="aliq1"):
        agree = "agreed"
        if aliq == "aliq1":
            if not self.agrees[0]:
                agree = "disagreed"
        if aliq == "aliq2":
            if not self.agrees[1]:
                agree = "disagreed"
        self.plot_result(aliq)
        ref_path = 'plots/tmp-eval-ref-{0}-{1}-{2}-{3}.png'.format(str(self.ref.id), aliq, self.eval_id.split('.')[0], agree)
        print ref_path
        plt.savefig(ref_path)
        plt.close()
        return ref_path

    def plot_error(self, _aliq="aliq1"):
        _aliq = 'aliq1'
        fig = plt.figure()
        ax = fig.add_subplot(111)
        legend = []

        # plt.errorbar(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq], xerr=self.ref.fit_pressure[_aliq], yerr=self.results['std'][_aliq], ls='-', color='red')
        plt.plot(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq], '^', ms = float(5.0), color = "red", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.plot(self.pressure[_aliq]['run1'], self.uptake[_aliq]['run1'], 'o', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        plt.plot(self.pressure[_aliq]['run2'], self.uptake[_aliq]['run2'], 'bs', ms = float(5.0), color = "yellow", mew = .25, ls = '-', lw = float(1.5), zorder = 3)

        plt.fill_between(self.ref.fit_pressure[_aliq], [mn_1 + sd1 for mn_1, sd1 in zip(self.ref.mn_uptake[_aliq],self.ref.sd_uptake[_aliq])], [mn_1 - sd1 for mn_1, sd1 in zip(self.ref.mn_uptake[_aliq],self.ref.sd_uptake[_aliq])], facecolor="red", alpha=0.5)
        plt.fill_between(self.ref.fit_pressure[_aliq], [mn_1 + sd1 for mn_1, sd1 in zip(self.ref.mn_uptake[_aliq],self.results['std'][_aliq])], [mn_1 - sd1 for mn_1, sd1 in zip(self.ref.mn_uptake[_aliq],self.results['std'][_aliq])], facecolor="green", alpha=0.5)

        # Plot with the new mean from the evaluated data.
        # plt.plot(self.ref.fit_pressure[_aliq], self.results['mn'][_aliq], '^', ms = float(5.0), color = "green", mew = .25, ls = '-', lw = float(1.5), zorder = 3)
        # plt.fill_between(self.ref.fit_pressure[_aliq], [mn_1 + sd1 for mn_1, sd1 in zip(self.results['mn'][_aliq],self.results['std'][_aliq])], [mn_1 - sd1 for mn_1, sd1 in zip(self.results['mn'][_aliq],self.results['std'][_aliq])], facecolor="green", alpha=0.5)
        
        # z = np.polyfit(self.ref.fit_pressure[_aliq], self.ref.mn_uptake[_aliq], 30)
        # print str(z)
        p = np.poly1d(self.ref.formula[_aliq])
        plt.plot(self.ref.fit_pressure[_aliq], p(self.ref.fit_pressure[_aliq]), ms = float(5.0), color = "blue", mew = .25, ls = '--', lw = float(1.5), zorder = 3)

        plt.axis([0, 1.2*self.ref.sizes['aliq1']['pressure']['max'], 0, 1.2*self.ref.sizes['aliq1']['uptake']['max']])
        plt.xlabel('Pressure (Bar)')
        plt.ylabel('Uptake (mmol/g)')
        plt.grid(b=True, which='major', color='k', linestyle='-')
        # plt.legend(legend, loc = 2, fontsize = 10)
        plt.draw()


    def error(self, aliq="aliq1"):
        agree = "agreed"
        if aliq == "aliq1":
            if not self.agrees[0]:
                agree = "disagreed"
        if aliq == "aliq2":
            if not self.agrees[1]:
                agree = "disagreed"
        self.plot_error(aliq)
        ref_path = 'plots/tmp-error-ref-{0}-{1}-{2}-{3}.png'.format(str(self.ref.id), aliq, self.eval_id.split('.')[0], agree)
        print ref_path
        plt.savefig(ref_path)
        plt.close()
        return ref_path























