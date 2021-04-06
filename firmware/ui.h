#include "lcd.h"
#include "adc.h"
#include "utils.h"
unsigned check_button(unsigned button);
unsigned get_button(unsigned button);
unsigned cat_mode = 0;
#include "cat.h"

#define WAIT_10MS wait_clocks(500000);
#define WAIT_100MS wait_clocks(5000000);
#define WAIT_500MS wait_clocks(25000000);

#define SMETER "s0#s1-|#s2--|#s3---|#s4----|#s5-----|#s6------|#s7-------|#s8--------|#s9---------|#s9---------+10dB#s9---------+20dB#s9---------+30dB#"
#define MODES "AM#NFM#FM#LSB#USB#CW"

////////////////////////////////////////////////////////////////////////////////
// Interrogate buttons and encoder
////////////////////////////////////////////////////////////////////////////////

int position;
int get_position_change(){
    int new_position = fgetc(position_in);
    int change = new_position - position;
    position = new_position;
    return change;
}
int encoder_control(int *value, int min, int max){
	int position_change = get_position_change();
	*value += position_change;
	if(*value > max) *value = min;
	if(*value < min) *value = max;
	return position_change;
}
unsigned get_button(unsigned button){
	if(~fgetc(push_button_in) & button){
		while(~fgetc(push_button_in) & button){}
		WAIT_10MS
		return 1;
	}
	WAIT_10MS
	return 0;
}
unsigned check_button(unsigned button){
	return ~fgetc(push_button_in) & button;
}

////////////////////////////////////////////////////////////////////////////////
// Generic menu item for an enumerated list of options
////////////////////////////////////////////////////////////////////////////////

void print_option(char * options, int option){

    char x;
    int i, idx=0;

    //find nth substring
    for(i=0; i<option; i++){ 
	while(options[idx++]!='#'){}
    }

    //print substring
    while(1){
        x = options[idx];
	if(x==0 || x=='#') return;
        lcd_write(x);
	idx++;
    }
}


int get_enum(char * title, char * options, int max, int *value){

    int select=*value;

    while(1){
	encoder_control(&select, 0, max);

	//print selected menu item
	LCD_CLEAR()
	lcd_print(title);
	LCD_LINE2()
	print_option(options, select);

	//select menu item
	if(get_button(1)){
		*value = select;
		return 1;
	}

	//cancel
	if(get_button(2)){
		return 0;
	}

	WAIT_100MS

    }
}

////////////////////////////////////////////////////////////////////////////////
//  Load settings from memory
////////////////////////////////////////////////////////////////////////////////

int load_memory(){

    int page=1;
    unsigned buffer[16];
    unsigned i;

    //store current settings
    store_settings(&bus, 0);

    //temporarily load setting
    load_settings(&bus, page);
    apply_settings();

    while(1){
	if(encoder_control(&page, 1, 499)){
		//temporarily load setting
		load_settings(&bus, page);
		apply_settings();
	}

	//read the page into memory
	eeprom_page_read(&bus, page, buffer);

	//print memory content
	LCD_CLEAR()
	lcd_print("memory load: ");
	lcd_print_udecimal(page, 3);
	LCD_LINE2()

	if(buffer[15]==0){
		for(i=11; i<15; i++){
			lcd_write(buffer[i]);
			lcd_write(buffer[i]>>8);
			lcd_write(buffer[i]>>16);
			lcd_write(buffer[i]>>24);
		}

		//OK
		if(get_button(1)){
			return 1;
		}

	} else {
		lcd_print("empty");
	}



	//cancel
	if(get_button(2)){
		load_settings(&bus, 0);
		return 0;
	}

	WAIT_100MS

    }
}

////////////////////////////////////////////////////////////////////////////////
// Frequency menu item (digit by digit)
////////////////////////////////////////////////////////////////////////////////

int get_frequency(){

    int digit=0;
    int digits[8];
    int i, digit_val;
    int edit_mode = 0;
    unsigned frequency;

    //convert to binary representation
    frequency = settings[idx_frequency];
    digit_val = 10000000;
    for(i=0; i<8; i++){
        digits[i] = frequency / digit_val;
	frequency %= digit_val;
        digit_val /= 10;
    }

    while(1){

	if(edit_mode){
	    encoder_control(&digits[digit], 0, 9);
	} else {
	    encoder_control(&digit, 0, 9);
	}

	LCD_CLEAR()

	//write frequency to lcd
	LCD_LINE1()
        for(i=0; i<8; i++){
	    lcd_write(digits[i] + '0');
 	    if(i==1||i==4) lcd_write('.');
        }
	lcd_print(" Y N");

	//print cursor
	LCD_LINE2()
	for(i=0; i<16; i++){
	    if(i==digit){
		if(edit_mode){
			lcd_write('X');
		} else {
			lcd_write('^');
		}
	    } else {
		lcd_write(' ');
	    }
 	    if(i==1||i==4||i==7|i==8) lcd_write(' ');
	}

	//select menu item
	if(get_button(1)){
	    edit_mode = !edit_mode;
	    if(digit==8){
	        digit_val = 10000000;

		//convert back to a binary representation
		settings[idx_frequency] = 0;
		for(i=0; i<8; i++){
	            settings[idx_frequency] += (digits[i] * digit_val);
		    digit_val /= 10;
		}
		return 1;

	    }
	    if(digit==9) return 0;
	}

	//cancel
	if(get_button(2)){
		return 0;
	}

    }

}

////////////////////////////////////////////////////////////////////////////////
// Generic Menu item for a single digit parameter
////////////////////////////////////////////////////////////////////////////////
int get_digit(char * title, int max, int *value){
    return get_enum(title, "0#1#2#3#4#5#6#7#8#9#", max, value);
}

////////////////////////////////////////////////////////////////////////////////
// Procedure to read and display battery voltage
////////////////////////////////////////////////////////////////////////////////
void battery_voltage(){
    unsigned int i, voltage, raw_voltage=0;
    LCD_CLEAR()
    lcd_print("battery voltage");
    while(1){
	LCD_LINE2()
	read_adc_values();
	raw_voltage = (raw_voltage*9 + adc_values[CHAN_BATTERY])/10;
        voltage = (raw_voltage*33*11)/(4096);
	lcd_print_decimal(voltage, 2, 1);
	lcd_write('V');
	if(get_button(3)){
		return;
	}
	WAIT_100MS
    }
}

////////////////////////////////////////////////////////////////////////////////
// Procedure to set microphone gain and display live level indicator
////////////////////////////////////////////////////////////////////////////////

void mic_level(){
    int raw, amplitude, max = 0, min=4095, level;
    int gain=settings[idx_mic_gain], i;

    LCD_CLEAR()
    lcd_print("mic level");
    while(1){

	encoder_control(&gain, 0, 9);
	read_adc_values();
	raw = adc_values[CHAN_MICROPHONE]-2048;
	if(raw > max){
		max = raw;
	} else {
		max = max*4/5;
	}
	if(raw < min){
	    min = raw;
	} else {
	    min = min*4/5;
	}
	amplitude = (max-min)/2;
	
	level = (to_dB(amplitude)/6)-3;
	level += gain;
	level = clamp(level, 0, 12);

	LCD_LINE2()
	lcd_write('<');
	lcd_write('0'+gain);
	lcd_write('>');
	lcd_write(' ');
	if(level>9){
		lcd_write('X');
	} else {
		lcd_write('0'+level);
	}
	for(i=1; i<12; i++){
		if(i==9||i==level){
			lcd_write('|');
		} else if(i<level){
			lcd_write('-');
		} else {
			lcd_write(' ');
		}
	}
	if(get_button(3)){
		settings[idx_mic_gain]=gain;
		return;
	}
	WAIT_100MS
    }
}

////////////////////////////////////////////////////////////////////////////////
// This is the main UI loop. Should get called about 100 times/second
////////////////////////////////////////////////////////////////////////////////

int step_sizes[10] = {10, 50, 100, 1000, 5000, 10000, 12500, 25000, 50000, 100000};

int do_ui(){

    //If button is pressed enter menu
    if(!check_button(1)) return 0;
    get_button(1);

    //top level menu
    char unsigned buttons;
    unsigned setting = 0;
    unsigned pps_count, ppm;
    if(!get_enum("menu:", "frequency#volume#load memory#mode#AGC#squelch#step#check battery#mic level#CW speed#calibrate#cat#factory reset#", 12, &setting)) return 1;

    switch(setting){
	case 0 : get_frequency();
		 return 1;

	case 1 : get_digit("volume", 9, &settings[idx_volume]);
		 return 1;

	case 2 : 
		load_memory();
		return 1;

	case 3 : 
		get_enum("mode", MODES, 5, &settings[idx_mode]);
		return 1;

	case 4 :
		//Select AGC Speed
		get_enum("AGC", "fast#normal#slow#very slow#", 3, &settings[idx_agc_speed]);
		return 1;

	case 5 :
		//Select Squelch
		get_enum("squelch", SMETER, 12, &settings[idx_squelch]);
		return 1;

	case 6 : 
		get_enum("step", "10Hz#50Hz#100Hz#1kHz#5kHz#10kHz#12.5kHz#25kHz#50kHz#100kHz#", 9, &settings[idx_step]);

		//round frequency to the nearest step size
		settings[idx_frequency] -= settings[idx_frequency]%step_sizes[settings[idx_step]];
		return 1;

	case 7 :
		battery_voltage();
		return 1;

	case 8 :
		mic_level();
		return 1;

	case 9 :
		while(1){
                    LCD_CLEAR()
                    lcd_print("CW speed (wpm)");
                    LCD_LINE2()
		    encoder_control(&settings[idx_cw_speed], 1, 99);
	            lcd_print_udecimal(settings[idx_cw_speed], 2);
                    if(get_button(3)) return 1;
		    WAIT_100MS
		}

	case 10 :
		while(1){
                    LCD_CLEAR()
                    lcd_print("frequency error");
                    LCD_LINE2()
                    pps_count = fgetc(pps_count_in);
		    //if gps reading is out of range default to exact clock frequency
		    if(140000000 > pps_count || pps_count > 160000000) pps_count = 150000000;
	            ppm = pps_count/150;
		    lcd_print_sdecimal(ppm-1000000, 1);
		    lcd_print(" ppm");
		    if(get_button(1)){
	        	    settings[idx_pps_count] = pps_count;
			    return 1;
		    }
                    if(get_button(2)) return 1;
		    WAIT_100MS
		}

	case 11 : 
		while(ready(stdin)) getc();
		cat_mode = 1;
		return 1;

	case 12 : 
		get_enum("confirm", "No#Yes#", 2, &setting);
		if(setting) factory_reset(&bus);
		return 1;

    }

}
