# Open XCVR

A cheap open source radio transceiver based on the [MAX1000 FPGA module](https://shop.trenz-electronic.de/en/Products/Trenz-Electronic/MAX1000-Intel-MAX10/). 

# Introduction

There are many HF radio receivers based on a Tayloe mixer, this type of mixer can be made using a cheap analogue switch such as an [FST3253](https://www.onsemi.com/products/interfaces/analog-switches/fst3253). When combined with a Hi Fidelity Audio ADC, it is possible to realise a sensitive receiver with a high dynamic range.

The [soft-rock](http://www.wb5rvz.org/) and [qrp-labs](https://www.qrp-labs.com/receiver.html) receivers require a PC with a sound card to demodulate the I and Q outputs. [mcHF](http://www.m0nka.co.uk/) and the [Elekraft kx-3](https://elecraft.com/products/kx3-all-mode-160-6-m-transceiver) receivers have built-in Audio ADC and CPU, to replace the PC providing a stand-alone radio.

Projects such as [rpitx](https://github.com/F5OEO/rpitx) and [FPGA-TX](https://github.com/dawsonjon/FPGA-TX) also show that it is possible to build a flexible radio transmitter using a high speed digital IO pin. I have experimented building receivers using similar techniques, and while I have been successful in receiving some signals using these techniques, I have not been able to achieve sufficient dynamic range to build a useful receiver.

An inexpensive FPGA card such as the MAX1000 has sufficient capacity to implement:
- The ESP algorithms needed to demodulate I and Q outputs from a Tayloe mixer.
- A stripped down version (providing an HF capability) of the FPGA-TX project.
- A small CPU sufficient to implement a user interface with LCD display and rotary encoder.
- A Numerically Controlled Oscillator (NCO) with a 0-150MHz frequency range.
- A 1-bit DAC to drive speaker or headphones.
- The built-in ADC can be used to digitize the microphone input.

As a proof of concept, a prototype design has been built using a combination of kits and modules.
![Prototype](https://github.com/dawsonjon/OpenXcvr/blob/master/images/prototype.jpg?raw=true)

The aim of this project is a work in progress, to turn this prototype design into a fully featured, cheap, HF transceiver. This repository contains the FPGA firmware and PCB designs.

The main aims for this phase of the project are to:
- Create a simple design that can be built by a hobbyist without any special equipment.
- Reduce the cost.
- Achieve performance similar to or better than existing designs.

# Receiver Hardware Design

## BPF filters

The Tayloe mixer uses a square wave local oscillator and is therefore sensitive not only to the tuned frequency but also to odd harmonics, the strongest being the third harmonic (3x the tuned frequency). To prevent signals at the harmonic frequencies interfering with the signal of interest, a bandpass filter is placed in front of the receiver.

The entire HF spectrum is broken down into a number of bands each with a separate band pass filter. To prevent the third (and higher harmonics) from being received, the high cut-off frequency must not be greater than the 3x the lower cut-off frequency. In the real world, filters roll off slowly, so we ideally to allow some extra margin say 2x the lower cut-off frequency.

Using this approach, we can cover the whole HF spectrum from 3MHz to 30MHz with only four filters.

Band | f1 (MHz) |  f2 (MHz)
-|-|-
0 | 16 | 30
1 | 8 | 16
2 | 4 | 8
3 | 2 | 4

This technique is used in both the soft-rock (ensemble) and mcHF designs, using an analogue multiplexer to switch between bands. The qrp-labs design uses much narrower plug-in BPF modules which each pass on of the HF ham bands. The qrp-labs design does a better job of filtering out unwanted signals outside the ham bands, but a filter is needed for each band (which would be a lot of filters). The OpenXcvr design uses a 4 band filter to reduce cost, and allow a general coverage design that could also be used for Short Wave Listening (SWLing). 

In common with the mcHF design, wire-wound surface mount inductors are used. The surface mount inductors reduce cost and board area, but still provide a reasonably high Q factor.

The 2MHz lower frequency limit of band 3 will probably allow reasonable performance on the 1.8MHz (160m) band, due to the slow roll-off of the filter. To allow maximum flexibility, e.g. for comercial broadcast on LW and MW bands, a bypass option is also included. 

The resistor and inductor values were calculated using an [online calculator](https://rf-tools.com/lc-filter/). The filters are all 3rd order Chebyshev designs, the surface mount inductors are only available in a limited range of values, so the E6 range was chosen. Both the input and output impedance are 50 ohms.

## Tayloe Mixer
There a a few variations on the basic design that have been used in previous projects. The soft-rock receivers use a transformer to create positive and negative versions of the signal, and the analogue switch passes either the positive or negative signal to a single ended amplifier to achieve a mixing effect. The qrp-kits also uses a transformer to create a positive and negative version of the input signal, but both positive and negative versions of the signal are passed to a differential (instrumentation) amplifier.

To eliminate the hand-wound transformer, OpenXCVR uses a differential amplifier in combination with a single ended input. The input is connected to either the positive or negative input of the differential amplifier. The soft-rock uses a LT6231 op amp, whereas the qrp-labs design uses an LM4562 op amp. The LT6236 has better noise performance than the LM4562 but is more expensive. The prototype receiver used a qrp-labs receiver and this gave very good results. For this reason the less expensive LM4562 was chosen, but using an 8-pin SOIC package rather than a DIP package. The 2 devices are footprint compatible so it should be possible to substitute either device (although I haven't tried this).

## I/Q ADC

The MAX 10 device has an in-built 12-bit ADC, I did some experiments using the inbuilt ADC, but I didn't get very good results. I think that the 12-bit ADC just doesn't have sufficient dynamic range for this application. I considered using a programmable gain amplifier to drive the ADC, but rejected this idea because it would be more expensive than using a dedicated audio ADC and would not have performed as well. A number of modules using a 24-bit stereo [PCM1802 ADC](http://www.ti.com/lit/ds/symlink/pcm1802.pdf) are available cheaply on ebay, one of these modules was selected for the prototype and it worked well. These ADCs are inexpensive and provide more than more than adequate dynamic range. They also allow a decent sample rate of 96kS/s providing more than enough bandwidth for the modes used on HF ham bands. 

## 1-bit sigma-delta Audio DAC
The FPGA processes the I/Q signals provided by the PCM1802 ADC, producing a mono audio signal. This signal needs to be converted into a analogue signal to drive the headphone/speakers. This DAC doesn't need to be Hi-Fi grade, the audio output of the radio only has a limited dynamic range and bandwidth (3KHz is enough to reproduce intelligible speech). A sigma-delta modulator allows a DAC to be constructed using a single FPGA GPIO pin, followed by a simple RC filter with a cut-off frequency of ~3KHz. The sigma-delta DAC works on the principle that bandwidth can be traded for an improved signal to noise ratio (SNR). In this case the GPIO pin is toggled at a rate of 150MHz while highest frequency of interest is only 3KHz, this gives an oversampling ratio of 25000. Ordinarily an extra bits-worth of SNR is gained each time the sample rate is multiplied by 4, in this case giving about 7 bits. A sigma delta modulator provides noise shaping, this moves the majority of the quantisation noise out of the band of interest, where it is removed by the filter. For a first order sigma-delta modulator, we get approximately twice as many bits for the same oversampling ratio. This is equivalent to ~14 bits, which is plenty.

## Audio amplifier
The audio amplifier uses a LM386, with the minimum gain of 20x. This is still a bit more gain than is really needs, so additional attenutation is applied at the input. The FPGA provides a digital volume control, so a trim-pot is used only to set the maximum volume. There are better amplifiers available, but the LM386 is ubiquitous, so should be easy to get hold of.

## Microphone pre-amplifier

The prototype design used a max9814 based module with an electret condenser microphone. The max9814 gave enough gain to drive the 0-3v input of the FPGAs build in ADC, and the inbuilt AGC also worked well. The AGC also has the effect of amplifying background noise, which isn't really desirable for a communications transmitter. For this reason it was decided to use a simple operation amplifier with a fixed gain of up to 60dB. The FPGA has sufficient capacity to provide any additional gain control/compression that might be needed. The amplifier uses a very cheap MCP6002 dual op-amp. The other half of the amplifier is used to generate a 2.5v split supply rail to bias signals in the FST3253 bus switches.

## TX output

The FPGA uses a single GPIO pin with oversampling and dithering to generate the transmit output RF. The output swing is about 2v peak to peak, and the IO pin is capable of sourcing or sinking 8 mA of current. Which works out at about 5mW or 7dBm. The manufacturer doesn't really specify the output impedance. However the IO pin is specified to maintain a high output of 2.4v from a 3.3v supply when sourcing 8mA, indicating a voltage drop of less than 0.9v. Based on this, the resistance of the output must be less than 112 ohms. When driving low, the output is specified to be less than 0.8v when sinking 8 mA, this gives a resistance of less than 100 ohms. Based on this I assume that the output impedance is somewhere in the region of 100 ohms.

## RF PA

To build a QRP transceiver with a similar spec to the existing products, an HF power amplifier with an output of about 10 watts seems appropriate. In keeping with the low-cost theme, an amplifier based on BS170 and/or IRF510 mosfet transistors seems to be the way to go. The [linear amplifier](https://www.qrp-labs.com/linear.html) from qrp-kits seems to fit the bill. Rather than attempt to design an amplifier from scratch, I have opted to simply buy one of these kits.

## Low Pass Filter

Due to the dithering employed, the TX output should be relatively free from harmonics. The power in the harmonics is effectively converted into wideband noise. Most of this noise lies outside the HF band and is filtered away. However, the Power Amplifier may add additional harmonics and good practice dictates that a low pass filter should be employed after the Power Amplifier to prevent unwanted spurious emissions.

The low pass filter must handle 10 watts of RF power, so the inductors used in the low pass filter are hand-wound toroidal inductors. OpenXCVR uses a relay switched design similar in principal to [mcHF](http://www.m0nka.co.uk/) and [ubitx](https://ubitx.net/). This [article](https://www.qrp-labs.com/images/lpfkit/gqrplpf.pdf) provides the basic filter designs.

AXICOM d2n relays have been selected because they have been used successfully in other HF applications for example in [ubitx](http://ubitx.net/spectral-purity/) and [easy tr switch](https://www.qrpkits.com/ezseries.html#eztrsw).

## Transmit Receive Switching

The transmit receive switch simply uses a AXICOM d2n relay to switch the antenna connector between the RF input to the receiver and the RF output from the Power amplifier. A BS170 mosfet provides the active-low transmit enable signal used by the qrp-labs power amplifier to switch off the bias voltage when receiving.

## Power Meter and SWR meter

[This article](https://sites.google.com/view/kn9b/digital-swr-meter) describes the design of a QRP SWR meter using an Arduino and a Stockton Bridge. OpenXCVR uses the same basic design, but uses spare FPGA analogue inputs to measure the forward and reverse power.

# FPGA Firmware

![top level](https://github.com/dawsonjon/OpenXcvr/blob/master/images/firmware_top.png?raw=true)

The FPGA firmware consists of 2 main parts. The RF rate section works at a sample rate of 300MS/s with a clock speed of 150MHz, and the audio rate section works at a sampling rate of 100KS/s and a clock speed of 50MHz. 

In the RF rate section, two samples must be processed in each clock cycle, in general this is achieved by duplicating logic. This section includes a Numerically Controlled Oscillator[NCO], the transmuter i/Q mixer and the a 1-bit RF DAC.

In the audio rate section, things are a bit more relaxed, we have up to 500 clock cycles to generate each sample. The audio section includes the TX modulator, RX demodulator, RX AGC, DC removal and digital filter which is used in both the transmit and receive paths.

## Numerically Controlled Oscillator

![top level](https://github.com/dawsonjon/OpenXcvr/blob/master/images/NCO.png?raw=true)

A 32-bit phase counter forms the basis of the NCO. At 300MS/s this gives a frequency resolution of ~0.07 Hz. Normally, an NCO would be a simple counter representing the phase, each clock cycle the change in phase (better known as the frequency) is added to the phase. If the frequency value is large, the phase counter overflows quickly giving a high frequency. If the frequency value is small the phase counter takes a long time to overflow and the frequency is low. 

In this system, we need to generate 2 samples per clock cycle. To achieve this we add twice the phase to the counter each clock cycle. Even numbered samples are then derived directly from the counter, and odd samples are derived from the phase counter added to the frequency. Thus in cycle 0 the samples are 0 and 1x frequency, in the cycle 1 the outputs are 2x frequency and 3x frequency and so on. The NCO con only update the phase once per clock cycle, this results in a jitter of 3.333ns, but over a long period the average frequency averages out to the programmed value precisely. 

The most significant bits of the phase counter used as the address input into ROM lookup table containing sin and cosine values. Again two samples are generated per clock cycle, requiring two sin and two cosine lookup tables. The outputs from the table form the I and Q inputs to the TX mixer. The most significant bits of the I and Q are used to generate a square wave local oscillator output to drive the FST3253 in the RX mixer. A double data rate output register allows one sample to be output on the rising edge of the 150MHz clock, while the other sample is output on the falling edge.

## TX Mixer

The TX mixer consists of 4 multipliers, multiplying the I and Q values of the NCO by the transmit I and Q samples from the audio rate section. This effectively shifts the baseband signal to the local oscillator frequency.

## 1-bit RF DAC

The 1-bit DAC converts the output of the TX mixer into a 1-bit value to be output via a GPIO pin. This is achieved using dithering. Each sample, the signal which could be in the range -1.0 to +1.0 is compared to a random numer in the range -1.0 to +1.0, if the signal is greater than the random number, a 1 is output, otherwise a 0 is output. Thus, a number close to 1.0 is very likely to result in a 1. If the signal is close to 0, the output is likely to be a 0. If the signal is 0, the output is equally likely to be a 1 or a zero. Thus at any time, the probability of outputting a 1 is proportional to the value of the signal. The average value of the GPIO pin will follow the input signal.

![Dithering](https://github.com/dawsonjon/OpenXcvr/blob/master/images/dithering.png?raw=true)

This process is equivalent (or at lest very similar) to adding random noise to the signal. The signal itself has a very narrow bandwidth and lies inside the band of interest, whereas the noise is spread equally over the whole of the spectrum.

The random number is generated by combining the output of two different length [linear feedback shift registers](https://en.wikipedia.org/wiki/Linear-feedback_shift_register). This gives a random number with reasonably good statistical properties. Since two samples are generated each clock cycle, the DAC uses two independent random number sequences and two comparators. A double data rate output register is used to output one sample on the rising edge of the clock and the other sample on the falling edge.

## Downconverter

The I and Q outputs from the PCM1802 ADC are received at a sample rate of approximately 100kHz. The receiver hardware does not pass signals at DC, and in any case the local oscillator and other sources of noise make it desirable to use a small Intermediate Frequency (IF) within the bandwidth of the ADC. The IF signal is then down-converted to DC digitally using a complex mixer. When receiving therefore, the frequency of the NCO is set to the frequency of the received signal minus the IF frequency. The IF frequency is chosen to be exactly one quarter of the sampling frequency (FS/4). At this frequency, the I and Q components of the IF oscillator are either 0, 1, or -1. This greatly simplifies the design of the mixer which can then be built without using multipliers.

## Digital Filter

The filter is used in both the transmit and receive paths. The filter uses an Finite Impulse Response (FIR) design. The most demanding task the filter performs is in the transmission of single side-band. In single side-band mode, the filter passes positive frequencies and blocks negative frequencies (upper side-band) or passes negative frequencies and blocks positive frequencies (lower side-band). This type of filter is approximating a Hilbert transform and has an asymmetric frequency response. To realise a filter with an asymmetric response, a filter kernel with both real and imaginary components is required.

The filter uses two memories, one implements a complex circular buffer for the filter data, and the other implements a complex circular buffer for the filter kernel. A 255 pole filter is used to give a steep transition from the stopband to the passband. Each output sample is generated by multiplying each of the previous 255 input samples by the corresponding value in the filter kernel. All 255 products are accumulated into a single complex sum. In the audio section, 500 clock cycles are available to calculate each sample, so it is possible to calculate and accumulate 1 of the 255 products each clock cycle.

AM and FM modes require larger bandwidth symmetrical filters. The filter provides 4 programmable responses to accommodate SSB ~3KHz, AM ~6KHz, Narrowband FM ~9Khz and Wideband FM ~15KHz. The filter RAM is sized to allow 255 kernel elements for each RAM mode, the 2 most significant address bits select one of the four filter kernels. The single side-band filter can be used for both upper and lower side-band, this can be achieved simply by switching the I and Q components of the kernel effectively mirroring the frequency response.

![Filter](https://github.com/dawsonjon/OpenXcvr/blob/master/images/digital_filter_response.png?raw=true)

## Demodulator

The demodulator converts the I and Q outputs of the filter into a single real audio output. 

Single side-band is the simplest mode to demodulate. In this mode, the I component is selected and the Q component is discarded (effectively set to 0). This has the effect of adding back the missing sideband.

To demodulate AM and FM signals, the I and Q components are first converted into a magnitude and phase representation. An efficient way to implement this is using the [CORDIC](https://dspguru.com/dsp/faqs/cordic/) algorithm. The magnitude output of the CORDIC, provides a demodulated AM signal which still contains a large DC component. The phase output is used to demodulate FM signals. Since the frequency of a signal is the change in phase, the frequency can be calculated by subtracting the phase of the previous sample from the phase of the current signal.

## DC removal

A demodulated AM signal contains a large DC component which needs to be removed. The DC removal block uses a first order IIR low-pass filter. In this design, filter coefficients are chosen so that the "multiplies" can be achieved using a single shift thereby eliminating the need for multipliers. The low-pass filter provides an estimate of the DC present in the signal. The DC is removed by simply subtracting this value from the signal.

## Automatic Gain Control (AGC)

The size of an AM or SSB signal is dependent on the strength of the signal. Very weak signals are tiny compared with strong signals. The amplitude of FM signal is dependent not on the strength of the signal, but by the frequency deviation. Thus wideband FM signals will sound louder than narrowband FM signals. In all cases, the AGC scales the output to give a similar loudness regardless of the signal strength or bandwidth. 

This can be a little tricky, in speech there are gaps between words. If the AGC reacted too quickly, then the gain would be adjusted to amplify the noise during the gaps. Conversely if the AGC reacts too slowly, then sudden increases in volume will cause the output to saturate. [The UHSDR project](https://github.com/df8oe/UHSDR/wiki/Automatic-Gain-Control-(AGC)) has a good description, and the OpenXCVR design is based on similar principles.

The first stage of the AGC is to estimate the average magnitude of the signal. This is achieved using a leaky max hold circuit. When the input signal is larger than the magnitude estimate, the circuit reacts by quickly increasing the magnitude estimate (attack). When the input is smaller than the magnitude estimate waits for a period (the hang period) before responding. After the hang period has expired, the circuit responds by slowly reducing the magnitude estimate (decay). The attack period is always quite fast, but the hang and delay periods are programmable and are controlled by the AGC rate setting. The diagram shows, how the magnitude estimate responds to a changing input magnitude.

![magnitude estimation](https://github.com/dawsonjon/OpenXcvr/blob/master/images/magnitude_estimation.png?raw=true)

Having estimated the magnitude, the gain is calculated by dividing the desired magnitude by the estimated magnitude. We have plenty of clock cycles to calculate this so a slow (and small) non-restoring divide algorithm is used to calculate 1 bit of the gain per clock cycle.

Having calculated the gain, we simply multiply the signal by the gain to give an appropriately scaled output. on those occasions where the magnitude of the signal increases rapidly and the AGC does not have time to react, we need to prevent the signal from overflowing. This is achieved using a combination of soft and hard clipping. Signals above the soft clipping threshold are gradually reduced in size, signals above the hard clipping limit are clamped to the limit value.

## Modulator

The transmit modulator converts the real value input from the microphone into a complex waveform with I and Q components. This waveform is output vias the filter to the RF section, where it is up-converted to the transmit frequency. 

SSB signals are simple to modulate, the real valued signal is used to form the I component and the Q component is set to zero. This gives a dual side-band waveform with both positive and negative frequencies. The filter then removes either the positive or negative frequencies to give a single side-band signal.

AM signals are also simple to modulate. The signal is scaled by 0.5, and a DC value of 0.5 is added. This is then output into both the I and Q component. We could also have added it into either the I or the Q component, but this method give a more favourable scaling.

FM modulation is very similar to the operation of the NCO, except that the modulator is working at a much lower sampling rate. The audio samples (the frequency) are added to a phase counter. The phase and magnitude (always 1) are then converted to a rectangular I and Q representation. This is easily achieved using a lookup table of sin and cosine values. The plot shows how an audio tone is frequency modulated into I and Q components.

![FM Modulation](https://github.com/dawsonjon/OpenXcvr/blob/master/images/modulator_fm.png?raw=true)

## GPS Frequency Calibration

GPS modules can be obtained very cheaply, and provide an extremely accurate frequency reference. OpenXCVR can use the 1 pulse per second (1PPS) output from a GPS module to accurately calibrate the frequency. The firmware counts (using a 150MHz clock) the number of clock cycles between rising edges of the 1PPS input. If the oscillator were perfectly accurate we would expect 150,000,000 clocks. If the number is greater or smaller than this, the control software can work out how much faster or slower the oscillator is running. The software can then apply a correction to the frequency setting in the NCO.

## Self Test

One objective of this project is to enable the project to be build with minimal test equipment. It is unlikely that a hobbyist builder will be able to get hold of a spectrum/network analyser. While it is possible to measure the frequency response of a filter using more basic equipment, this can be a time consuming and difficult task.

To simplify the process, OpenXCVR is capable of generating a test tone in the receivers passband. With simple software it is then possible to use the OpenXCVR as a "poor man's" network analyser. The following measurements of the band-pass filter response were made using the prototype.

![analyser](https://github.com/dawsonjon/OpenXcvr/blob/master/images/analyser.png?raw=true)


































