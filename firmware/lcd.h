#ifndef LCD_H
#define LCD_H

unsigned lcd_out = output("lcd_out");

#define OE 0x400
#define RS 0x200
#define E  0x100

// output byte value to the lcd
void lcd_io( unsigned value )
{
   fputc(OE, lcd_out);
   wait_clocks(500);//1us delay
   fputc(value | OE, lcd_out);
   wait_clocks(500);//1us delay
   fputc(value | E | OE, lcd_out);
   wait_clocks(500);//1us delay
   fputc(value | OE, lcd_out);
   wait_clocks(5000);//100us delay
   fputc(0, lcd_out);
}

// output the instruction byte in value to the lcd
void lcd_instruction( unsigned value )
{
   lcd_io((value >> 4) & 0xf);
   lcd_io(value & 0xf);
}

// output the data byte in value to the lcd
void lcd_write( unsigned value )
{
   lcd_io(RS | ((value >> 4) & 0xf));
   lcd_io(RS | (value & 0xf));
}

// lcd initialisation
void lcdInit()
{
   fputc(0, lcd_out);
   wait_clocks(5000000);//100ms delay
   lcd_io(0x3); //8 bit mode
   wait_clocks(500000);//10ms delay
   lcd_io(0x3); //8 bit mode
   lcd_io(0x3); //8 bit mode
   lcd_io(0x2); //4 bit mode (8 bit transaction)
   lcd_instruction( 0x28 );  // 4 bit mode + 2 lines, 
   lcd_instruction( 0x0c );  // display_on | auto_increment | ~cursor | ~blink
   lcd_instruction( 0x01 );  // clear display
   wait_clocks(100000);//2ms delay
   lcd_instruction( 0x06 );  // auto increment no shift
   lcd_instruction( 0x02 );  // display home
   lcd_instruction( 0x10 );  // cursor_move, shift_left

   //setup symbols for bignum charaters
   //lcd_define(0, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C);
   //lcd_define(1, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07);
   //lcd_define(2, 0x1F, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00);
   //lcd_define(3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F);
   //lcd_define(4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x07);
   //lcd_define(5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x18, 0x1C);
   //lcd_define(6, 0x07, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00);
   //lcd_define(7, 0x1C, 0x18, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00);

}

#define LCD_CLEAR() {lcd_instruction(0x01);  wait_clocks(100000);}
#define LCD_LINE1() {lcd_instruction(0x80);}
#define LCD_LINE2() {lcd_instruction(0xA8);}

void lcd_define( 
   unsigned x,
   unsigned b0, 
   unsigned b1, 
   unsigned b2, 
   unsigned b3, 
   unsigned b4, 
   unsigned b5, 
   unsigned b6,
   unsigned b7
) 
{
   lcd_instruction( 0x40 | ( x << 3 ) );
   lcd_write( b0 );
   lcd_write( b1 );
   lcd_write( b2 );
   lcd_write( b3 );
   lcd_write( b4 );
   lcd_write( b5 );
   lcd_write( b6 );
   lcd_write( b7 );
}

void lcd_print(char * string)
{
  int i=0;
  char character;
  while(1)
  {
    character = string[i++];
    if(!character) return;
    lcd_write(character);
  }
}


void lcd_print_udecimal(unsigned x, unsigned digits)
{

    unsigned digitval = 1000000000;
    unsigned digitpos = 10;
    unsigned digit;
    unsigned leading = 0;

    while(digitpos){

        if(digitpos == digits){
            leading = 1;
        }

	digit = x/digitval;
	if(digit || leading){
	    lcd_write('0' + digit);
	    if(digitpos==4){
	        lcd_write(',');
	    }
	    leading = 1;
	}


       	x %= digitval;
	digitval /= 10;
	digitpos --;

    }

}

void lcd_print_decimal(unsigned x, unsigned digits, unsigned decimals){
    unsigned significance[3] = {10, 100, 1000};
    lcd_print_udecimal(x/significance[decimals-1], digits);
    lcd_write('.');
    lcd_print_udecimal(x%significance[decimals-1], decimals);
}

#endif
