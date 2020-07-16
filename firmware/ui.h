#include "lcd.h"

#define WAIT_10MS wait_clocks(500000);
#define WAIT_100MS wait_clocks(5000000);
#define WAIT_500MS wait_clocks(25000000);

char * smeter[13];
char * modes[6];
void init_ui(){
smeter[0]="s0               ";
smeter[1]="s1-|             ";
smeter[2]="s2--|            ";
smeter[3]="s3---|           ";
smeter[4]="s4----|          ";
smeter[5]="s5-----|         ";
smeter[6]="s6------|        ";
smeter[7]="s7-------|       ";
smeter[8]="s8--------|      ";
smeter[9]="s9---------|     ";
smeter[10]="s9---------+10dB";
smeter[11]="s9---------+20dB";
smeter[12]="s9---------+30dB";

//Select Mode
modes[0]="AM";
modes[1]="NFM";
modes[2]="FM";
modes[3]="LSB";
modes[4]="USB";
modes[5]="CW";
}

////////////////////////////////////////////////////////////////////////////////
// Interogate buttons and encoder
////////////////////////////////////////////////////////////////////////////////

int position;
get_position_change(){
    int new_position = fgetc(position_in);
    int change = new_position - position;
    position = new_position;
    return change;
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
// Draw frequency XX.XXX.XXX 0 to 99.999999 MHz in 1Hz steps
////////////////////////////////////////////////////////////////////////////////

void print_frequency(int frequency){

    int i;
    int mask = 10000000;
    LCD_LINE1()
    for(i=0; i<8; i++){
	lcd_write('0'+frequency/mask);
	frequency %= mask;
	mask /= 10;
	if(i==1||i==4) lcd_write('.');
    }

}

////////////////////////////////////////////////////////////////////////////////
// Generic menu item for an enumerated list of options
////////////////////////////////////////////////////////////////////////////////

int get_enum(char * title, char * options[], int max, int *value){

    int select=*value;


    while(1){
	select += get_position_change();
	if(select > max) select = 0;
	if(select < 0) select = max;

	//print selected menu item
	LCD_CLEAR()
	lcd_print(title);
	LCD_LINE2()
	lcd_print(options[select]);

	//select menu item
	if(get_button(1)){
		*value = select;
		return 1;
	}

	//cancel
	if(get_button(2)){
		return 0;
	}

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

    while(1){
	i = get_position_change();
		page += i;
		if(page < 1) page = 499;
		if(page > 499) page = 1;

		//temporarily load settings
		load_settings(&bus, page);
		apply_settings();

		//read the page into memory
		eeprom_page_read(&bus, page, buffer);

		//print memory content
		LCD_CLEAR()
		lcd_print("memory load: ");
		lcd_write('0' + (page / 100));
		lcd_write('0' + (page % 100) / 10);
		lcd_write('0' + (page % 100) % 10);
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
    frequency = settings.frequency;
    digit_val = 10000000;
    for(i=0; i<8; i++){
        digits[i] = frequency / digit_val;
	frequency %= digit_val;
        digit_val /= 10;
    }

    while(1){

	if(edit_mode){
            digits[digit] += get_position_change();
	    if(digits[digit] > 9) digits[digit] = 0;
	    if(digits[digit] < 0) digits[digit] = 9;
	} else {
            digit += get_position_change();
	    if(digit > 9) digit = 0;
	    if(digit < 0) digit = 9;
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
		settings.frequency = 0;
		for(i=0; i<8; i++){
	            settings.frequency += (digits[i] * digit_val);
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
    char * options[10];
    options[0] = "0";
    options[1] = "1-|";
    options[2] = "2--|";
    options[3] = "3---|";
    options[4] = "4----|";
    options[5] = "5-----|";
    options[6] = "6------|";
    options[7] = "7-------|";
    options[8] = "8--------|";
    options[9] = "9---------|";
    return get_enum(title, options, max, value);
}

////////////////////////////////////////////////////////////////////////////////
// Procedure to read and display battery voltage
////////////////////////////////////////////////////////////////////////////////
#define CHAN_BATTERY 2
#define CHAN_MICROPHONE 8
unsigned read_adc_chan(unsigned chan){
    unsigned int raw;
    while(1){
        raw = fgetc(adc_in);
        if(raw >> 16 == chan) return raw & 0xffff;
    }
}

void battery_voltage(){
    unsigned int i, voltage, raw_voltage=0;
    LCD_CLEAR()
    lcd_print("battery voltage");
    while(1){
	LCD_LINE2()
	raw_voltage = (raw_voltage*9 + read_adc_chan(CHAN_BATTERY))/10;
        voltage = (raw_voltage*33*11)/(4096);
	lcd_write('0'+voltage/100); voltage %= 100;
	lcd_write('0'+voltage/10); voltage %= 10;
	lcd_write('.');
	lcd_write('0'+voltage);
	lcd_write('V');
	if(get_button(3)){
		return;
	}
	WAIT_100MS
    }
}

void mic_level(){
    int raw, amplitude, max = 0, min=4095, level;
    int gain=settings.mic_gain, i;

    LCD_CLEAR()
    lcd_print("mic level");
    while(1){

	gain += get_position_change();
	gain %= 10;
	
	raw = read_adc_chan(CHAN_MICROPHONE)-2047;
	if (max > raw){
		max = max*4/5;
	} else {
		max = raw;
	}
	if (min < raw){
		min = min*4/5;
	} else {
		min = raw;
	}
	amplitude = (max-min)/2;
	
	level = 0;
	while(amplitude > 3){
		level++;
		amplitude >>= 1;
	}
	level += gain;

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
		settings.mic_gain=gain;
		return;
	}
	WAIT_100MS
    }
}

////////////////////////////////////////////////////////////////////////////////
// This is the main UI loop. Should get called about 100 times/second
////////////////////////////////////////////////////////////////////////////////

int step_sizes[10] = {10, 50, 100, 1000, 5000, 10000, 12500, 25000, 50000, 100000};
int position_change=0;

int do_ui(){

    //If button is pressed enter menu
    if(!check_button(1)) return 0;
    get_button(1);

    //top level menu
    char unsigned buttons;
    char * options[13];
    unsigned setting = 0;
    char * title;

    options[0] = "frequency";
    options[1] = "volume";
    options[2] = "load memory";
    options[3] = "mode";
    options[4] = "AGC";
    options[5] = "squelch";
    options[6] = "step";
    options[7] = "check battery";
    options[8] = "mic level";
    options[9] = "factory reset";
    if(!get_enum("menu:", options, 9, &setting)) return 1;
    title = options[setting];

    switch(setting){
	case 0 : get_frequency();
		 return 1;

	case 1 : get_digit(title, 9, &settings.volume);
		 return 1;

	case 2 : 
		load_memory();
		return 1;

	case 3 : 
		get_enum(title, modes, 5, &settings.mode);
		return 1;

	case 4 :
		//Select AGC Speed
		options[0]="fast";
		options[1]="normal";
		options[2]="slow";
		options[3]="very slow";
		get_enum(title, options, 3, &settings.agc_speed);
		return 1;

	case 5 :
		//Select Squelch
		get_enum(title, smeter, 12, &settings.squelch);
		return 1;

	case 6 : 
		options[0]="10Hz";
		options[1]="50Hz";
		options[2]="100Hz";
		options[3]="1kHz";
		options[4]="5kHz";
		options[5]="10kHz";
		options[6]="12.5kHz";
		options[7]="25kHz";
		options[8]="50kHz";
		options[9]="100kHz";
		get_enum(title, options, 9, &settings.step);

		//round frequency to the nearest step size
		settings.frequency -= settings.frequency%step_sizes[settings.step];
		return 1;

	case 7 :
		battery_voltage();
		return 1;

	case 8 :
		mic_level();
		return 1;

	case 9 : 
		options[0]="No";
		options[1]="Yes";
		get_enum("confirm", options, 2, &setting);
		if(setting) factory_reset(&bus);
		return 1;

    }

}
