from copy import copy
from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as sp_io_wav
import scipy.fft as fft

SAMPLE_RATE = 44100     # Hertz
DURATION = 5            # Seconds

""" Generating Simple Sine Wave """

def generate_sine_wave(freq, sample_rate, duration):
    # Create a time series of samples, e.g. 44100Hz * 3 sec = 132300 samples
    # It does not include the endpoint
    x = np.linspace(0, duration, num=sample_rate*duration, endpoint=False)

    # Create the corresponding series of amplitudes
    y = np.sin(2 * np.pi * freq * x)
    return x, y


# x, y = generate_sine_wave(4, SAMPLE_RATE, DURATION)
# plt.plot(x, y)
# plt.show()

""" Generating Sine Wave with Noise """

_, nice_tone = generate_sine_wave(400, SAMPLE_RATE, DURATION)
_, noise_tone = generate_sine_wave(4000, SAMPLE_RATE, DURATION)

# Numpy makes addition of frequencies as simple as array
mixed_tone = nice_tone + noise_tone * 0.3

# Normalize and convert the tone to int26 for exporting WAV file
normalized_tone = np.int16((mixed_tone / mixed_tone.max()) * 32767)

# plt.plot(normalized_tone[:1000])
# plt.show()

# Export WAV file
# sp_io_wav.write("tone_with_noise.wav", SAMPLE_RATE, normalized_tone)

""" Performing FFT on the audio """

sample_rate, audio = sp_io_wav.read("tone_with_noise.wav")

n_samples = len(audio)
yf = fft.fft(audio)
# print(f"len of yf = {len(np.abs(yf))}")
# print(np.abs(yf).max()) # Maximum amplitude
# print(np.abs(yf).min()) # Minimum amplitude
# window length, sample spacing
xf = fft.fftfreq(n_samples, 1 / sample_rate)

# plt.plot(xf, np.abs(yf))
# plt.show()

""" Performing FFT For Real Sequence to Improve Efficiency """

yf = fft.rfft(audio)
xf = fft.rfftfreq(n_samples, 1 / sample_rate)

print(f"Maximum amplitude = {np.abs(yf).max()}")
print(f"Minimum amplitude = {np.abs(yf).min()}")
print(f"Number of frequency bins = {len(np.abs(xf))}")
print(f"Maximum frequency = {xf.max()}")
print(f"Minimum frequency = {xf.min()}")
print(f"Frequency resolution = {xf[2] - xf[1]}")
print()

# Absolute for yf is required because the output is complex
# plt.plot(xf, np.abs(yf))
# plt.show()

""" Filtering noise from the audio """

# idx of the 400Hz, which has the highest amplitude
# Equivalent to 400Hz * frequency resolution (i.e. 0.2)
highest_freq_i = np.argmax(np.abs(yf))

# Since there is no spectrum leakage, the frequencies around the peaks are significantly attenuated
print("Frequencies around the highest frequency bin")
print(np.abs(yf)[highest_freq_i-1:highest_freq_i+2])

# Set the highest frequency to zero so that we can find the second highest frequency
yf_no_highest = copy(np.abs(yf))
yf_no_highest[highest_freq_i] = 0

# idx of the 4000Hz noise, which has the second highest amplitude
# Equivalent to 400Hz * frequency resolution (i.e. 0.2)
second_highest_freq_i = np.argmax(yf_no_highest)
yf[second_highest_freq_i - 1: second_highest_freq_i + 2] = 0

# plt.plot(xf, np.abs(yf))
# plt.show()

""" Applying the Inverse FFT """

clean_tone = fft.irfft(yf)

# plt.plot(clean_tone[:1000])
# plt.show()

# Normalize and convert the tone to int26 for exporting WAV file
normalized_tone = np.int16((clean_tone / clean_tone.max()) * 32767)

# Export WAV file
sp_io_wav.write("clean_tone.wav", SAMPLE_RATE, normalized_tone)