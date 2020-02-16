# Open XCVR

A cheap open source radio transceiver based on the [MAX1000 FPGA module](https://shop.trenz-electronic.de/en/Products/Trenz-Electronic/MAX1000-Intel-MAX10/). 

# Introduction

There are many HF radio receivers based on a Tayloe mixer, this is allows a mixer to be made using a cheap analogue switch such as an [FST3253](https://www.onsemi.com/products/interfaces/analog-switches/fst3253). When combined with a Hi Fidelity Audio ADC, it is possible to realise a sensitive receiver with a high dynamic range.

The [soft-rock](http://www.wb5rvz.org/) and [qrp-labs](https://www.qrp-labs.com/receiver.html) receivers require a PC with a sound card to demodulate the I and Q outputs. [mchf](http://www.m0nka.co.uk/) and the [elekraft kx-3](https://elecraft.com/products/kx3-all-mode-160-6-m-transceiver) receivers have built-in Audio ADC and processors, to replace the PC providing a stand-alone radio.

Projects such as [rpitx](https://github.com/F5OEO/rpitx) and [FPGA-TX](https://github.com/dawsonjon/FPGA-TX) show that it is possible to build a flexible radio transmitter using a high speed digital IO pin. I have experimented building receivers using similar techniques, and while I have been successful in receiving some signals using these techniques, it is not possible to achieve sufficient dynamic range to build a useful receiver.

Even an inexpensive FPGA card such as the MAX1000 has sufficient capacity to implement:
- The ESP algorithms needed to demodulate I and Q outputs from a Tayloe mixer.
- A stripped down version (providing an HF capability) of the FPGA-TX project.
- A small CPU sufficient to implement a user interface with LCD display and rotary encoder.
- A Numerically controlled oscillator with a 0-150MHz frequency range.
- A 1-bit DAC to drive speaker or headphones.
- The built-in ADC to digitize the microphone input.

Thus it is possible to build fully featured HF transceiver using a MAX1000 FPGA and a minimum of external components. The main objectives of this project are to:

- Reduce the cost.
- Achieve performance similar to or better than existing designs.
- Come up with a design that can be built be a hobbyist without special equipment.

This repository contains the designfor the MAX1000 FPGA firmware and a collection of PCB designs for a low cost transceiver. The transceiver is a work in progress.



# Receiver Hardware Design

## BPF filters
The receiver design borrows from both the softrock, mchf and qrp-labs designs. The softrock (ensemble) and mchf designs use both switch between 4 bandpass filters each covering a portion of the HF spectrum, the qrp-labs design uses plug-in modules which are each centred on one of the HF ham bands. The qrp-labs design probably does a better job of filtering out unwanted signals outside the ham bands, this will give a supperior performance if the receiver is used exlusively on these bands. The four band design has the advantage of simplicity (only 4 filters are needed), and gives a general coverage reciever that can also be used for SWLing. The 4 band filter design gives reasonably good attenuation of the odd (especially the 3rd) harmonics that the Tayloe mixer is sensitive to.  The OpenXcvr design uses a 4 band filter, using wire-wound surface mount inductors similar to the mchf design. The filters are switched using a FST3253 switch. The surface mount inductors reduce cost and board area, but still provide a reasonbly high Q factor.

Band | f1 (MHz) |  f2 (MHz)    
-|-|-
0 | 16 | 30
1 | 8 | 16
2 | 4 | 8
3 | 2 | 4

The low limit of band 3 allows a reasonable performance on the 1.8MHz (160m) band, due to the slow roll-off of the filter. To allow maximum flexibility, e.g. for comercial broadcast on LW and MW bands, a bypass option is also included. The resistor and inductor values were calculated using an [online calculator](https://rf-tools.com/lc-filter/). The filters are all 3rd order chebychev designs, the surface mount inductors are only available in a limited range of values, so the E6 range was chosen. Both the input and output impedance are 50 ohms.

## Tayloe Mixer
There a a few vartiations on the basic design that have been used on previous projects. The softrock receivers use a transformer to create positive and negative versions of the signal, and the analogue switch passes either the positive or negative signal to a single ended amplifier to achieve a mixing effect. The qrp-kits also uses a transformer to create a positive and negative version of the input signal, but uses a differential (instrumentation) amplifier, at any one part of the cycle both the posive and negative versions of the signal are connected to one or other of the amplifiers.

To eliminate the tranformer, a differential amplifier is used in combination with a single ended input. The input is connected to either the positive or negative input of the differential amplifier. The softrock uses a LT6231 op amp, wheras the qrp-kits design uses an LM4562 op amp. The LT6236 has better noise performance the the LM4562 but is more expensive, the prototype for OpenXcvr used a qrp-kits receiver and this gave very good results. For this reason the less expensive LM4562 was chosen, but using an 8-pin SOIC package rather than a DIP package. The 2 devices are footprint compatible so it should be possible to substitute either device (although I haven't tried this).

## I/Q ADC

The MAX 10 device has an in-built 12-bit ADC, I did some experiments using the inbuilt ADC, but I didn't get very good results. I think that the 12-bit ADC just doesn't have sufficient dynamic range for this application. I considered using a programmable gain amplifier to drive the ADC, but rejected this idea because it would be more expensive than using a dedicated audio ADC and would not have performed as well. A number of modules using a 24-bit stereo [PCM1802 ADC](http://www.ti.com/lit/ds/symlink/pcm1802.pdf) are available cheaply on ebay, one of these modules was selected for the prototype and worked well. These ADCs are inexpensive and provide more than more than adequate dynamic range. They also allow a decent sample rate of 96-kS/s providing more than enough bandwidth for the modes used on HF ham bands. 

## 1-bit sigma-delta Audio DAC
The FPGA processes the I/Q signals provided by the PCM1802 ADC, producing a mono audio signal. This signal need to be converted into a analogue signal to drive the headphone/speakers. This DAC doesn't need to be Hi-Fi grade, the audio output of the radio only has a limited dynamic range and bandwidth (3KHz is enough to reproduce intelligible speech). A sigma-delta DAC allows a DAC to be constructed using a single FPGA GPIO pin, followed by a simple RC filter with a cutoff frequency of ~3KHz. The sigma-delta DAC works on the principle that bandwidth can be exchanged for quantisation noise. In this case the GPIO pin is toggled at a rate of 150MHz while the band of interest is only 3KHz wide, an oversampling ratio of 33333. Ordinarily an extra bits-worth of quantisation noise is gained each time the sample rate is multiplied by 4, in this case giving about 7 bits. A sigma delta modulator provides noise shaping, this moves the majority of the quantisation noise out of the band of interest, where it is removed by the filter. For a first order sigma-delta modulator, we get approximately twice as many bits for the same oversampling ratio. This gives 14-15 bits which is plenty.

## Audio amplifier
The audio amplifier uses a LM386, with the minimum gain of 20x. This is still a bit more gain than is really needs, so additional attenutation is applied at the input. The FPGA provides a digital volume control, so a trim-pot is used only to set the maximum voltage.

## Microphone pre-amplifier

The prototype design used a max9814 based module with an electret condenser microphone. The max9814 gave plenty of gain to drive the 0-3v input of the FPGAs build in ADC, and the inbuilt AGC worked well. The AGC also has the effect of amplifying background noise, which isn't really desirable for a communications transmitter. For this reason it was decided to use a simple operation amplifier with a fixed gain of up to 60dB. The FPGA has sufficient capacity to provide any additional gain control/compression that might be needed. The amplifier uses a very cheap MCP6002 dual op-amp. The other half of the amplifier is used to generate a 2.5v split supply rail to bias signals in the FST3253 bus switches.

## TX output

The FPGA uses a single GPIO pin with oversampling and dithering to generate the transmit output RF. The output swing is about 2v peak to peak, and the IO pin is capable of sourcing or sinking 8 mA of current. Which works out at about 5mW or 14dBm. The manufacturer doesn't really specifiy the output impedance. However the IO pin is specified to maintain a high output of 2.4v from a 3.3v supply when sourceing 8mA, indicating a voltage drop of less than 0.9v. Based on this, the resistance of the output must be less than 112 ohms. When driving low, the output is specified to be less than 0.8v when sinking 8 mA, this gives a resistance of less than 100 ohms. Based on this I assume that the output impedance is somewhere in the region of 100 ohms.

## RF PA

To build a QRP tranceiver with a similar spec to the existing products, an HF power amplifier with an output of about 10 watts seems appropriate. In keeping with the low-cost theme, an amplifier based on BS170 and/or IRF510 mosfet transistors seems to be the way to go. The [linear amplifier](https://www.qrp-labs.com/linear.html) from qrp-kits seems to fit the bill. Rather than attempt to design an amplifier from scratch, I have opted to simply buy one of these kits.

## Low Pass Filter

Due to the dithering employed, the TX output should be relatively free from harmonics. The power in the harmonics is effectively converted into noise, spread over a 300MHz band. Most of this noise lies outside the HF band and is filtered away. However, the Power Amplifier may add additional harmonics and good practice dicatates that a low pass filter should be employed after the Power Amplifier to prevent unwanted transmissions.

The low pass filter must handle 10 watts of RF power, the inductors used in the loww pass filter are hand-wound torroidal inductors. OpenXcvr uses a relay switched design similar in principal to [mchf](http://www.m0nka.co.uk/) and [ubitx](https://ubitx.net/). This [article](https://www.qrp-labs.com/images/lpfkit/gqrplpf.pdf) provides some basline component values.

AXICOM d2n relays have been selected because they have been used successfully in HF applications for example in [ubitx](http://ubitx.net/spectral-purity/) and [easy tr switch](https://www.qrpkits.com/ezseries.html#eztrsw).

## Transmit Receive Switching

The transmit receive swith simply uses a AXICOM d2n relay to switch the antenna connector between the RF input to the receiver and the RF output from the Power amplifier. A BS170 mosfet provides the active-low transmit enable signal used by the qrp-kits power amplifier to switch off the bias voltage when receiving.

## Power Meter and SWR meter

[This article](https://sites.google.com/view/kn9b/digital-swr-meter) describes the design of a QRP SWR meter using an arduino and a Stockton Bridge. OpenXcvr uses the same basic design, but uses spare FPGA analogue inputs to measure the forward and reverse power.

# FPGA Firmware

The FPGA firmware consists of 2 main parts. The RF rate section works at a sample rate of 300MS/s with a clock speed of 150MHz, and the audio rate section works at a sampling rate of 100KS/s and a clock speed of 50MHz. 

In the RF rate section, two samples must be processed in each clock cycle, in genaral this is achieved by duplicating logic. This section includes a numerically controlled oscillator, the transmiter i/Q mixer and the a 1-bit RF DAC.

In the audio rate section, things are a bit more relaxed, we have up to 500 clock cycles to generate each sample. The audio section includes the TX modulator, RX demodulator, RX AGC, DC removal and FIR filter which is used in both the transmit and receive paths.

## Numerically Controlled Osillator

A 32-bit phase counter forms the basis of the NCO. At 300MS/s this gives a frequency resolution of ~0.07 Hz. Normaly, an NCO would be a simple counter representing the phase, each clock cycle the change in phase (better known as the frequency) is added to the phase. If the frequency value is large, the phse counter overflows quickly giving a high frequency. If the frequency value is small the phase counter takes a long time to overflow and the frequency is low. 

In this system, we need to generate 2 samples per clock cycle. To achieve this we add twice the phase to the counter each clock cycle. Even numbered samples are then derrived directly from the counter, and odd samples are derived from the phase counter added to the frequency. Thus in cycle 0 the samples are 0 and 1xfrequency, in the second cycle the outputs are 2xfrequency and 3xfrequency and so on. The NCO con only update the phase once per clock cycle, this results in a jitter of 3.333ns, but over a long period the average frequency averages out to the programmed value precicely. 

The most significant bits of the phase counter used as the address input into ROM lookup table containing sin and cosine values. Again two samples are generated per clock cycle, requiring two sin and two cosine lookup tables. The outputs from the table form the I and Q inputs to the TX mixer. The most significant bits of the I and Q are used to generate a square wave local oscillator output to drive the FST3253 in the RX mixer. A double data rate output register allows one sample to be output on the rising edge of the 150MHz clock, while the other sample is output on the falling edge.

## TX Mixer

The TX mixer consists of 4 multipliers, multiplying the I and Q values of the NCO by the transmit I and Q samples from the audio rate section. This effectively shifts the basband signal to the local oscilator frequency.

## 1-bit RF DAC

The 1-bit DAC converts the output of the TX mixer into a 1-bit value to be output via a GPIO pin. This is achieved using dithering. Each sample, the signal which could be in the range -1.0 to +1.0 is compared to a random numer in the range -1.0 to +1.0, if the signal is greater than the random number, a 1 is output, otherwise a 0 is output. Thus, a number close to 1.0 is very likely to result in a 1. If the signal is close to 0, the output is likely to be a 0. If the signal is 0, the output is equly likely to be a 1 or a zero. Thus at any time, the probablity of outputing a 1 is proportional to the value of the signal. On average the GPIO pin value will follow the output signal. 
This process is equivilent (or at lest very similar) to adding random noise to the signal. The signal itself has a very narrow bandwidth and lies inside the band of interest, wheras the noise however is spread equally over the whole of the spectrum.
The random number is generated by conbining the output of two different length [linear feedback shift registers](https://en.wikipedia.org/wiki/Linear-feedback_shift_register). This gives a random number with reasonably good statistical properties. Since two samples are generated each clock cycle, the DAC uses two independent random number sequences and two comparators. A double data rate output register is used to output one sample on the rising edge of the clock and the other sample on the falling edge.

## Downconverter

The I and Q outputs from the PCM1802 ADC are received at a smple rate of approximately 100Khz. The receiver hardware does not pass signals at DC, and in any case the local oscillator and other sources of noise make it desirable to use a small Intermediate Frequency (IF) within the bandwidth of the ADC. The IF signal is then downconverted to DC digitally using a complex mixer. When receving therefore, the frequency of the NCO is set to the frequency of the recieved signal minus the IF frequency. The IF frequency is chosen to be exactly one quarter of the sampling frequency (FS/4). At this frequency, the I and Q components of the IF osillator are either 0, 1, or -1. This greatly simplfies the design of the mixer which can then be built without using multipliers.

## Filter

The filter is used in both the transmit and recieve paths. The filter uses an Finite Impulse Response (FIR) design. The most complex taks the filter performs is in the transmission of single sideband. In single sideband mode, the filter passes positive frequencies and blocks negative frequencies (USB) or passes negative frequencies and blocks positive frequencies (LSB). This type of filter is approximating a Hilbert transform and has an asymetric frequency response. To realise a filter with an asymetric response, a filter kernel with both real and imaginary components is required.

The filter uses two memories, one implements a complex circular buffer for the filter data, and the other implements a complex circular buffer for the filter kernel. A 255 pole filter is used to give a steep transition from the stopband to the passband. Each output sample is generated by multiplying each of the previous 255 input sammples by the corresponding value in the filter kernel. All 255 products are accumulated into a single complex sum. In the audio section, 500 clock cycles are avaiable to calculate each sample, so it is possible to calculate and accumulate 1 of the 255 products each clock cycle.

AM and FM modes require larger bandwidth symetrical filters. The filter provides 4 programable responses to accomodate SSB ~3KHz, AM ~6KHz, Narrow band FM ~9Khz and Wideband FM ~15KHz. The filter RAM is sized to allow 255 kernel elements for each RAM mode, the 2 most significant addess bits select the filter mode.

## Demodulator

The demodulator converts the I and Q outputs of the filter into a single real audio output. 

Single sideband is the simplest mode to demodulate. In this mode, the I component is selected and the Q component is discarded (effectively set to 0). This has the effect of adding back the missing sideband.

To demodulate AM and FM signals, the I and Q components are first converted into a magnitude and phase representation. An efficient way to implement this is using the [CORDIC](https://dspguru.com/dsp/faqs/cordic/) algorithm. The magnitude output of the cordic, provides a demodulated AM signal which still contains a large DC component. The phase output is used to demodulate FM signals. Since the frequency of a signal is the change in phase, the frequency can be calculated by subtracting the phase of the previous sample from the phase of the current signal.

## DC removal

A demodulated AM signal contains a large DC component which needs to be removed. The DC removal block uses a first order IIR low-pass filter. In this design, filter coeeficients are chosen so that the "multiplies" can be achieved using a single shift therby eliminating the need for multipliers. The low-pass filter provides an estimate of the DC present in the signal. The DC is removed by simply subtracting this value from the signal.

## Automatic Gain Control (AGC)

The size of an AM or SSB signal is dependent on the strength of the signal. Very weak signals are tiny conpared with strong signals. The amplitude of FM signal is dependent not on the strength of the signal, but by the frequency deviation. Thus wideband FM signals will sound louder than narrowband FM signals.

In all cases, the AGC scales the output to give a similar loudness regardless of the signal strength or bandwidth. The first stage of the AGC is to estimate the average magnitude of the signal. This is achieved using a leaky max hold circuit. When the input signal is larger than the magnitude estimate, the circuit reacts by quickly increasing the magnitude estimate (attack). When the input is smaller than the magnitude estimate waits for a period (the hang period) before responding. After the hang period has expired, the circuit responds by slowly reducing the magnitude estimate (decay). The attack period is always quite fast, but the hang and delay periods are programmable and are controlled by the AGC rate setting.

Having estimated the magnitude, the gain is caulculated by dividing the desired magnitude by the estimated magnitude. We have plenty of clock cycles to calculate this so a slow (and small) non-restoring divide algorithm is used to calculate 1 bit of the gain per clock cycle.

Having calculated the gain, we simply multiply the signal by the gain to give an appriopriately scaled output. on those occasions where the magnitude of the signal increases rapidly and the AGC does not have time to react, we need to prevent the signal from saturated. This is achieved using a combination of soft and hard clipping. Signals above the soft clipping threshold are gradually reduced in size, signals above the hard clipping limit are clamped to the limit value.

## Modulator

The transmit modulator converts the real value input from the microphe into a complex waveform with I and Q components. This waveform is output vias the filter to the RF section, where it is upconverted to the transmit frequency. 

SSB signals are simple to modulate, the real valued signal is used to form the I component and the Q component is set to zero. This gives a dual sideband waveform with both positive and negative frequencies. The filter then removes either the positive or negative frequencies to give a single sideband signal.

AM signals are also simple to modulate. The signal is scaled by 0.5, and a DC value of 0.5 is added. This is then output into both the I and Q component. We could also have added it into either the I or the Q component, but this method give a more favourable scaling.

FM modulation is very similar to the operation of the NCO, except that the modulator is working a t a much lower sampling rate. The audio samples (the frequency) are added to a phase counter. The phase and magnitude (always 1) are then converted to a rectangular I and Q representation. This is easliy achieved using a lookup table of sin and cosine values.
































