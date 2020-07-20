#ifndef TRANSMIT_H
#define TRANSMIT_H
#define WAIT_100MS wait_clocks(5000000);

#include "adc.h"

unsigned check_ptt(){
    return PTT||DIT||DAH;
}

void transmit(){
    unsigned int hang_timer=0, vswr, start_time, frame, ratio,
    pk_fwd_voltage=0, pk_rev_voltage=0, rms_fwd_voltage, rms_rev_voltage, fwd_power, rev_power, p;

    //switch on the transmitter
    //need a check here that the transmit frequency is valid
    settings.tx = 1;
    apply_settings();
    start_time = timer_low();

    WAIT_100MS

    while(1){

	lcd_instruction(0x8b);
        lcd_write(" vYTYv "[frame++]);
	frame %= 7;

	//Add a hang time for partial break-in
	if(PTT||DIT||DAH){
            start_time = timer_low();
	}

	//if hang time is reached, leave transmit mode
	//this should be programmable say 30-3000ms
        if(timer_low() - start_time > 5000000) break;

	//leaky max hold to obtain peak voltage
	pk_fwd_voltage = MAX(FWD, pk_fwd_voltage*999/1000);
	pk_rev_voltage = MAX(REV, pk_rev_voltage*999/1000);

	//compensate for diode drop
	rms_fwd_voltage = pk_fwd_voltage + 150;
	rms_rev_voltage = pk_rev_voltage + 150;

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
	vswr = (1000+p)/(100-p);

	LCD_LINE2()
	lcd_write(126);
	lcd_print_decimal(fwd_power/100, 1, 1);
	lcd_write(' ');
	lcd_write(127);
	lcd_print_decimal(rev_power/100, 1, 1);
	lcd_write(' ');
	lcd_write('1');
	lcd_write(':');
	lcd_print_decimal(vswr, 1, 1);


	WAIT_100MS

    }

    lcd_instruction(0x8b);
    lcd_write(' ');

    settings.tx = 0;
    apply_settings();

}

#endif
