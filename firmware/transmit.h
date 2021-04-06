#ifndef TRANSMIT_H
#define TRANSMIT_H
#include "adc.h"


unsigned tx_on = 0;
unsigned tx_frame = 0;
unsigned tx_pk_fwd_voltage = 0;
unsigned tx_pk_rev_voltage = 0;
unsigned tx_timer = 0;
unsigned tx_update = 0;
unsigned hang_time_ms = 500;

void check_ptt(){
    read_adc_values();
    if( (adc_values[CHAN_PTT] < 0x7ff) || (adc_values[CHAN_DIT] < 0x7ff) || (adc_values[CHAN_DAH] < 0x7ff) || settings[idx_tx] ){
	tx_timer = timer_low(); //hang time in 10 ms steps (100=1 second)
    	tx_on = 1;
        apply_settings();
    }
}

//gets called approx once every 10 ms
void transmit(){
    unsigned int vswr, ratio, rms_fwd_voltage, rms_rev_voltage, fwd_power, rev_power, p;

    if( (adc_values[CHAN_PTT] < 0x7ff) || (adc_values[CHAN_DIT] < 0x7ff) || (adc_values[CHAN_DAH] < 0x7ff) || settings[idx_tx] ){
	tx_timer = timer_low(); //hang time in 10 ms steps (100=1 second)
    }

    //if hang time is reached, leave transmit mode
    //this should be programmable say 30-3000ms
    if((timer_low() - tx_timer) > (hang_time_ms*50000)){
	tx_on = 0;
	apply_settings();
	return;
    }

    //1 in 10 calls refresh lcd, giving an update rate of 10fps
    if(tx_update-- == 0){
	    tx_update = 9;

	    //update display
	    lcd_instruction(0x8b);
	    lcd_write(" vYTYv "[tx_frame++]);
	    tx_frame %= 7;

	    read_adc_values();

	    //leaky max hold to obtain peak voltage
	    tx_pk_fwd_voltage = max(adc_values[CHAN_FWD]*3300/4096, tx_pk_fwd_voltage*999/1000);
	    tx_pk_rev_voltage = max(adc_values[CHAN_REV]*3300/4096, tx_pk_rev_voltage*999/1000);

	    //compensate for diode drop
	    rms_fwd_voltage = tx_pk_fwd_voltage + 150;
	    rms_rev_voltage = tx_pk_rev_voltage + 150;

	    //multiply by transformer turns ratio
	    rms_fwd_voltage *= 10;
	    rms_rev_voltage *= 10;

	    //divide by sqrt(2) to get rms
	    rms_fwd_voltage *= 7071;
	    rms_rev_voltage *= 7071;
	    rms_fwd_voltage /= 10000;
	    rms_rev_voltage /= 10000;

	    //calculate vswr
	    fwd_power = rms_fwd_voltage * rms_fwd_voltage / 50000;
	    rev_power = rms_rev_voltage * rms_rev_voltage / 50000;
	    ratio = 10000*rev_power/fwd_power;
	    p = 0;
	    while(p*p < ratio){
		p++;
	    }
	    vswr = clamp((1000+p)/(100-p), 10, 99);

	    LCD_LINE2()
	    lcd_write(126);
	    lcd_print_decimal(fwd_power/100, 1, 1);
	    lcd_write(' ');
	    lcd_write(127);
	    lcd_print_decimal(rev_power/100, 1, 1);
	    lcd_write(' ');
	    lcd_write(' ');
	    lcd_write('1');
	    lcd_write(':');
	    lcd_print_decimal(vswr, 1, 1);
   }

}

#endif
