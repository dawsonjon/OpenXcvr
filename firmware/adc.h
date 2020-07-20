#ifndef __ADC_H
#define __ADC_H

#define CHAN_BATTERY 2
#define CHAN_MICROPHONE 8
#define CHAN_FWD 1
#define CHAN_REV 5
#define CHAN_PTT 3
#define CHAN_DIT 7
#define CHAN_DAH 4

unsigned read_adc_chan(unsigned chan){
    unsigned int raw;
    while(1){
        raw = fgetc(adc_in);
        if(raw >> 16 == chan) return raw & 0xffff;
    }
}

#define FWD read_adc_chan(CHAN_FWD)*3300/4096
#define REV read_adc_chan(CHAN_REV)*3300/4096
#define PTT read_adc_chan(CHAN_PTT)<0x7ff
#define DIT read_adc_chan(CHAN_DIT)<0x7ff
#define DAH read_adc_chan(CHAN_DAH)<0x7ff
#define BATTERY read_adc_chan(CHAN_BATTERY)
#define MIC read_adc_chan(CHAN_MICROPHONE)

#endif
