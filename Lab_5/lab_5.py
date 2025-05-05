import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import filtfilt, iirfilter

initialAmplitude = 1.0
initialFrequency = 1.0
initialPhase = 0.0
initialNoiseMean = 0.0
initialNoiseCovariance = 0.1
initialCutoffFrequency = 1.0
t = np.arange(0.0, 10.0, 0.01)
samplingFrequency = len(t) / (t[-1] - t[0])

def generateHarmonic(t, A, f, phi):
    return A * np.sin(2 * np.pi * f * t + phi)

def generateNoise(length, mean, cov):
    return np.random.normal(mean, np.sqrt(cov), size=length)

def applyLowPassFilter(sig, cutoff, fs, order=5):
    b, a = iirfilter(order, cutoff / (0.5 * fs), btype='low', ftype='butter')
    return filtfilt(b, a, sig)

plt.rcParams.update({
    'figure.facecolor': '#F9F9F9',
    'axes.facecolor': 'white',
    'grid.color': '#BBBBBB',
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
    'axes.edgecolor': '#444444',
    'font.size': 11
})

fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
plt.subplots_adjust(left=0.12, bottom=0.38, right=0.85, hspace=0.4)

axs[0].set_title('Гармоніка з шумом', fontsize=14, color='#333333')
axs[1].set_title('Низькочастотний фільтр', fontsize=14, color='#333333')
for ax in axs:
    ax.grid(True)
    ax.set_xlabel('Час, с')
    ax.set_ylabel('Амплітуда')

clean_line, = axs[0].plot(t, generateHarmonic(t, initialAmplitude, initialFrequency, initialPhase),
                          color='#1f77b4', linewidth=2, linestyle='-')
noise_line, = axs[0].plot(t, generateHarmonic(t, initialAmplitude, initialFrequency, initialPhase) + 
                          generateNoise(len(t), initialNoiseMean, initialNoiseCovariance),
                          color='#ff7f0e', linewidth=1.5, linestyle='--')
noise_line.set_visible(False) 
filtered_line, = axs[1].plot(t, generateHarmonic(t, initialAmplitude, initialFrequency, initialPhase),
                              color='#2ca02c', linewidth=2, linestyle=':')

widget_bg = '#EAEAF2'
ax_amp = plt.axes([0.12, 0.28, 0.6, 0.03], facecolor=widget_bg)
ax_freq = plt.axes([0.12, 0.24, 0.6, 0.03], facecolor=widget_bg)
ax_phase = plt.axes([0.12, 0.20, 0.6, 0.03], facecolor=widget_bg)
ax_nmean = plt.axes([0.12, 0.16, 0.6, 0.03], facecolor=widget_bg)
ax_ncov = plt.axes([0.12, 0.12, 0.6, 0.03], facecolor=widget_bg)
ax_cutoff = plt.axes([0.12, 0.08, 0.6, 0.03], facecolor=widget_bg)

s_amp = Slider(ax_amp, 'Amplitude', 0.1, 10.0, valinit=initialAmplitude, color='#1f77b4')
s_freq = Slider(ax_freq, 'Frequency', 0.1, 10.0, valinit=initialFrequency, color='#ff7f0e')
s_phase = Slider(ax_phase, 'Phase', 0.0, 2*np.pi, valinit=initialPhase, color='#2ca02c')
s_nmean = Slider(ax_nmean, 'Noise Mean', -1.0, 1.0, valinit=initialNoiseMean, color='#d62728')
s_ncov = Slider(ax_ncov, 'Noise Cov', 0.0, 1.0, valinit=initialNoiseCovariance, color='#9467bd')
s_cut = Slider(ax_cutoff, 'Cutoff Freq', 0.1, 5.0, valinit=initialCutoffFrequency, color='#8c564b')

ax_cb = plt.axes([0.76, 0.12, 0.12, 0.12], facecolor=widget_bg)
cb = CheckButtons(ax_cb, ['Show Noise'], [False])
ax_btn = plt.axes([0.76, 0.05, 0.12, 0.04], facecolor=widget_bg)
btn = Button(ax_btn, 'Reset')


def update(val):
    A, f, phi = s_amp.val, s_freq.val, s_phase.val
    m, cov = s_nmean.val, s_ncov.val
    cut = s_cut.val
    show = cb.get_status()[0]

    clean = generateHarmonic(t, A, f, phi)
    clean_line.set_ydata(clean)

    noise = generateNoise(len(t), m, cov)
    noisy = clean + noise if show else clean
    noise_line.set_ydata(noisy)
    noise_line.set_visible(show)

    filt = applyLowPassFilter(noisy, cut, samplingFrequency)
    filtered_line.set_ydata(filt)

    fig.canvas.draw_idle()

for widget in [s_amp, s_freq, s_phase, s_nmean, s_ncov, s_cut]:
    widget.on_changed(update)
cb.on_clicked(lambda _: update(None))
btn.on_clicked(lambda _: [w.reset() for w in [s_amp, s_freq, s_phase, s_nmean, s_ncov, s_cut]] + [update(None)])

plt.show()
