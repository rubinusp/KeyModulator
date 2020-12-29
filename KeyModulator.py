# 1.Standard Modules
import datetime as dt
import getopt
import sys
import textwrap

# 2. Extension Modules
from matplotlib import pyplot as plt
import numpy as np
import scipy.io.wavfile as sp_io_wav
import scipy.fft as fft

USAGE = "KeyModulator.py [option] <inputfile> <outputfile> <shift>"


class KeyModulator:

    def __init__(self, frame_len, overlap, verbose=False):

        self.verbose = verbose

        self.audio = None
        self.sample_rate = -1
        self.n_samples = -1         # Number of multi-channel samples
        self.n_channels = -1        # 1: single channel; 2: two channels
        self.duration = -1          # in seconds

        self.frame_len = frame_len  # Number of samples per frame
        self.n_frames = -1          # Number of frames in an audio
        self.hop_size = int((1 - overlap) * frame_len)   # Number of sample hopped between two frames

        self.new_audio = None
        self.new_n_samples = -1

        self.freq_ratio = 2 ** (1/12)

    def shift(self, semitone):
        if self.verbose:
            print("Shifting semitones")

        # Semitone = 1, i.e. one semitone up
        # Semitone = 0, i.e. no shifting
        # Semitone = -1, i.e. one semitone down
        shift = self.freq_ratio ** semitone

        frames = self._create_frames()
        frames = self._apply_window(frames)
        # TODO: experiment FFT analysis and synthesize
        self.new_audio = self._synthesize(frames, shift)
        self.new_audio = self._resample()

    def _resample(self):
        if self.verbose:
            print("Resampling the synthesized audio to change the key")
            print()

        sam_x = np.linspace(0, self.new_n_samples, num=self.n_samples, endpoint=False)
        sam_y = np.interp(sam_x, [i for i in range(self.new_n_samples)], self.new_audio)
        return sam_y

    def _synthesize(self, frames, slow):
        if self.verbose:
            print("Synthesizing frames")

        self.new_n_samples = int(slow * self.n_samples)
        audio = np.zeros(self.new_n_samples)
        new_hop_size = int((self.new_n_samples - len(frames[-1])) / (self.n_frames - 1))
        new_duration = self.new_n_samples / self.sample_rate

        if self.verbose:
            print(f"New number of samples = {self.new_n_samples}")
            print(f"New duration = {new_duration} {str(dt.timedelta(seconds=new_duration))}")
            print(f"New hop size = {new_hop_size}")
            print()

        i = 0
        for frame in frames:
            audio[i:min(self.new_n_samples, i + len(frame))] += frame
            i += new_hop_size

        return audio

    def _apply_window(self, frames):
        if self.verbose:
            print("Applying Hanning window")
            print()

        windowed_frames = [frame * np.hanning(len(frame)) for frame in frames]
        return windowed_frames

    def _create_frames(self):
        if self.verbose:
            print("Creating frames")

        audio = self.audio[:, 0].ravel()
        frames = []
        i = 0
        while True:
            # Take samples from i to the beginning of the next frame
            frame = audio[i:min(self.n_samples, i + self.frame_len)]
            frames.append(frame)
            if i + self.frame_len >= self.n_samples:
                # The last frame has been created
                break
            i += self.hop_size

        self.n_frames = len(frames)
        # frame_len / 4 * (n_frames - 1) + last_frame_len = n_samples
        if self.verbose:
            print(f"Frame length = {self.frame_len}")
            print(f"Length of last frame = {len(frames[-1])}")
            print(f"Hop size = {self.hop_size}")
            print(f"Number of frames = {self.n_frames}")
            print()

        # Checking the frames overlap
        # print(frames[0][12000:12000+4])
        # print(frames[1][0:0+4])

        return frames

    def read(self, path):

        try:
            if self.verbose:
                print(f"Reading audio from {path}")

            self.sample_rate, self.audio = sp_io_wav.read(path)
            self.n_samples = len(self.audio)
            self.n_channels = self.audio.shape[1]
            self.duration = self.n_samples / self.sample_rate

            if self.verbose:
                print(f"Audio matrix = {self.audio}")
                print(f"Sample rate = {self.sample_rate}")
                print(f"Number of samples = {self.n_samples}")
                print(f"Number of channels = {self.n_channels}")
                print(f"Duration = {self.duration} {str(dt.timedelta(seconds=self.duration))}")
                print()
        except Exception as e:
            print(e)
            exit(-1)

    def write(self, path):
        if self.verbose:
            print(f"Writing audio to {path}")

        try:
            normalized_audio = np.int16((self.new_audio / self.new_audio.max()) * 32767)
            sp_io_wav.write(path, self.sample_rate, normalized_audio)
        except Exception as e:
            print(e)
            exit(-1)

    def plot(self):
        plot_rate = 100     # Number of plotted points per second

        x = np.linspace(0, self.duration, num=self.n_samples, endpoint=False)
        y = self.audio[:, 0].ravel()

        # Minimize points to display
        sim_x = np.linspace(0, self.duration, num=int(plot_rate*self.duration), endpoint=False)
        sim_y = np.interp(sim_x, x, y)

        plt.plot(sim_x, sim_y)
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()


def parse_argv(argv):

    try:
        opts, args = getopt.getopt(argv, "hv")

        verbose = False
        show_help = False
        for opt, val in opts:
            if opt == "-v":
                verbose = True
            if opt == "-h" or opt == "--help":
                show_help = True

        if show_help:
            # No audio processing
            return show_help, verbose, None, None, None

        if len(args) != 3:
            # Invalid arguments
            print(f"usage: {USAGE}")
            exit(-2)

        input = args[0]
        output = args[1]
        shift = args[2]
        return show_help, verbose, input, output, int(shift)
    except getopt.GetoptError:
        print(f"usage: {USAGE}")
        exit(-2)


def main(argv):
    show_help, verbose, input, output, shift = parse_argv(argv)

    if show_help:
        print(textwrap.dedent(f"""\
        usage: {USAGE}
        Options and arguments
        -h  : print this help message and exit
        -v  : verbose (trace algorithm stages and extracted properties from the audio)
        """))
        exit()

    ks = KeyModulator(frame_len=12000, overlap=0.75, verbose=verbose)
    ks.read(input)
    # 7 semitones up = 1.5
    # 7 semitones down = 0.67
    ks.shift(shift)
    ks.write(output)


if __name__ == "__main__":
    main(sys.argv[1:])