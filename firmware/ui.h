#include "lcd.h"

#define WAIT_10MS wait_clocks(500000);

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
    options[2] = "mode";
    options[3] = "AGC";
    options[4] = "squelch";
    options[5] = "step";
    options[6] = "factory reset";
    if(!get_enum("menu:", options, 6, &setting)) return 1;
    title = options[setting];

    switch(setting){
	case 0 : get_frequency();
		 return 1;

	case 1 : get_digit(title, 9, &settings.volume);
		 return 1;

	case 2 : 
		get_enum(title, modes, 5, &settings.mode);
		return 1;

	case 3 :
		//Select AGC Speed
		options[0]="fast";
		options[1]="normal";
		options[2]="slow";
		options[3]="very slow";
		get_enum(title, options, 3, &settings.agc_speed);
		return 1;

	case 4 :
		//Select Squelch
		get_enum(title, smeter, 12, &settings.squelch);
		return 1;

	case 5 : 
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

	case 6 : 
		options[0]="No";
		options[1]="Yes";
		get_enum("confirm", options, 2, &setting);
		if(setting) factory_reset(&bus);
		return 1;

    }

}
