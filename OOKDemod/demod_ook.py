#!/usr/bin/env python
# coding: utf-8


import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import read, write
from scipy.fft import fftshift
from scipy import signal
from matplotlib.widgets import Cursor
import argparse


parser = argparse.ArgumentParser(description="demodulate input wav file as ook")
parser.add_argument("input_file",type=str, help = "input wav file to demodulate")
parser.add_argument("output_file",type=str, help = "output filename")

def bandpass_filter(sig, Fc: int, Fs: int): 
    Wcutoff = [2*(4.338e8 - Fc)/(Fs), 2*(4.340e8 - Fc)/(Fs)]
    b,a  = signal.butter(6, Wcutoff, btype="bandpass", analog=False)
    return signal.filtfilt(b, a, sig)

def am_demodulation(sig, Fc: int, Fs: int):
    # calculate envelope
    return  np.abs(signal.hilbert(sig))


def nice_plot(sig_filt, env_filt, tresh, Fc, Fs):
    sig_len = sig_filt.shape[0]
    t = np.arange(0, sig_len/Fs, 1/Fs)

    #create nice plot
    fig, ax = plt.subplots(3, 1, sharex=True)
    fig.set_size_inches(16, 10)
    fig.set_dpi(80)

    T1, T2 = 1.65, 1.673

    ax[0].plot(t, sig_filt)
    #ax[0].set_xlim(T1, T2)
    ax[0].set_title("Filtered signal")

    ax[1].plot(t, env_filt)
    #ax[1].set_xlim(T1, T2)
    ax[1].set_title("filtered env signal")


    ax[2].plot(t, tresh)
    #ax[2].set_xlim(T1, T2)
    ax[2].set_title("Threashold signal")

    plt.xlabel("Time[sec]")
    cursor = Cursor(ax[2], useblit=True, color='red', linewidth=2)

    plt.show()

def split_to_packets(sig, Fs):
    packets = []
    in_packet = False
    max_time_without_one = 11e-3
    print(max_time_without_one*Fs)
    for i in range(len(sig)):
        if not in_packet:
            if sig[i] == 1:
                print(f"start of packet {i}")
                start_packet_index = i
                in_packet = True

        if in_packet:
            if sig[i] == 1:
                last_one_index = i
            elif (i-last_one_index) > max_time_without_one*Fs:
                print(f'end of packet {i}')
                packets.append(sig[start_packet_index:i])
                in_packet = False

    return packets


            
    
def ook_manchester(sig):
    dif = abs(sig[:-1] ^sig[1:]) == 1
    change_indexes = np.where(dif)[0]
    bit_time_options = change_indexes[1:] - change_indexes[:-1]
    th = (np.max(bit_time_options) + np.min(bit_time_options))/2
    print(th)
    bit_time = np.average(bit_time_options[bit_time_options > th])/2 + np.average(bit_time_options[bit_time_options < th])
    bit_time = int(bit_time)
    bits = sig[int(bit_time/4)::bit_time]
    return bits.astype(int)
    
    

    
    
def main():
    args =parser.parse_args()

    a = read(args.input_file)
    Fs, sig = a
    Fc = int(args.input_file.split(sep='_')[-2][:-2]) 
    print("The Signal bandwidth is {} centered around {}".format(Fs, Fc))


    # Clean the signal

    #filter the signal
    sig_filt = bandpass_filter(sig[:,0], Fc, Fs)

    # calculate envelope
    env = am_demodulation(sig_filt, Fc, Fs)

    # filter envelope at 4kHz
    b,a  = signal.butter(6, 2*5e3/Fs, btype="lowpass", analog=False)
    env_filt = signal.filtfilt(b, a, env)

    # Tresholding
    tresh = env_filt > 110 #(np.max(env_filt)/2)

    # nice_plot(sig_filt, env_filt, tresh, Fc, Fs)

    packets_bits = []

    packets = split_to_packets(tresh, Fs)
    for packet in packets:
        bits = ook_manchester(packet) 
        packets_bits.append(bits)


    print(packets_bits)

    write(args.output_file, Fs,tresh.astype(np.uint8)*254)
    with open(args.output_file[:-3] + '.csv', 'w') as f:
        for bits in packets_bits:
            for bit in bits:
                f.write(f'{bit}, ')
            f.write('\n')
            

if __name__ == "__main__":
    main()

