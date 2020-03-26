#include "lcd.h"

void print_frequency(int frequency){

    char string[]="000.000.000     ";

    string[0] = '0'+frequency/100000000;
    frequency %= 100000000;
    string[1] = '0'+frequency/10000000;
    frequency %= 10000000;
    string[2] = '0'+frequency/1000000;
    frequency %= 1000000;

    string[3] = '.';

    string[4] = '0'+frequency/100000;
    frequency %= 100000;
    string[5] = '0'+frequency/10000;
    frequency %= 10000;
    string[6] = '0'+frequency/1000;
    frequency %= 1000;

    string[7] = '.';

    string[8] = '0'+frequency/100;
    frequency %= 100;
    string[9] = '0'+frequency/10;
    frequency %= 10;
    string[10] = '0'+frequency;
    lcd_line1();
    lcd_print(string);


}

void print_s_meter(int level){
    int i;
    lcd_line2();


    lcd_print("s");
    if(level <= 9) lcd_write('0'+level);
    else lcd_write('9');

    for(i=0; i<9; i++){
	    if(level>i){
		    lcd_print("-");
	    } else {
		    lcd_print(" ");
            }
    }

    if(level > 9){
	 lcd_print("+");
	 lcd_write('0' + level - 9);
	 lcd_print("0dB");
    } else {
	 lcd_print("     ");
    }
}
