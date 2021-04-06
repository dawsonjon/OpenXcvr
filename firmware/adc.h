#ifndef __ADC_H
#define __ADC_H

#define CHAN_BATTERY 1
#define CHAN_MICROPHONE 7
#define CHAN_FWD 0
#define CHAN_REV 4
#define CHAN_PTT 2
#define CHAN_DIT 6
#define CHAN_DAH 3


int adc_values[8];
void read_adc_values(){
    unsigned int raw, i;
    for(i=0; i<10; i++){
        raw = fgetc(adc_in);
	adc_values[(raw>>16)-1] = raw & 0xffff;
    }
}

#endif
