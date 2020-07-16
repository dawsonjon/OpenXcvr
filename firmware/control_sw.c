unsigned frequency_out = output("frequency_out");
unsigned control_out = output("control_out");
unsigned debug_out = output("debug_out");
unsigned debug_in = input("debug_in");
unsigned capture_in = input("capture_in");
unsigned audio_in = input("audio_in");
unsigned audio_out = output("audio_out");
unsigned power_in = input("power_in");
unsigned pps_count_in = input("pps_count_in");
unsigned adc_in = input("adc_in");
unsigned position_in = input("position_in");
unsigned push_button_in = input("pb_in");
unsigned i2c_in = input("i2c_in");
unsigned i2c_out = output("i2c_out");

#include <stdio.h>
#include <scan.h>
#include <print.h>

//int(round((2**32)*(2**32)/300e6))
#define FREQUENCY_STEP_MULTIPLIER 61489146912ul
#define FREQUENCY_CALIBRATION 4294860440ul

typedef struct{
    unsigned volume;
    unsigned frequency;
    unsigned max_frequency;
    unsigned min_frequency;
    unsigned squelch;
    unsigned mode;
    unsigned band;
    unsigned agc_speed;
    unsigned test_signal;
    unsigned USB_audio;
    unsigned tx;
    unsigned mute;
    unsigned step;
    unsigned mic_gain;
} struct_settings;
struct_settings settings;

void apply_settings();

#include "i2c.h"
i2c bus;
#include "eeprom.h"
#include "load_store.h"
#include "ui.h"
#include "transmit.h"

//convert a frequency in Hertz into a frequency in NCO step size.
unsigned convert_to_steps(unsigned x){
    unsigned long long y = x * FREQUENCY_STEP_MULTIPLIER;
    y >>= 32;
    y *= FREQUENCY_CALIBRATION;
    y >>= 32;
    return y;
}

//crude conversion to dBs
unsigned to_dB(unsigned x){
    unsigned dB = 0;
    while(x > 1){
        x >>= 1;
        dB += 6;
    }
    return dB;
}

//crude conversion to dBs
int read_smeter(){

    unsigned power = to_dB(fgetc(power_in));

    //ADC has 1.5Vpk = 1.06Vrms = 0.0225W into 50ohm = 22.5mW = 13.5dBm
    //Receiver has a gain of 1+(2*2k2/150) = 30.33.. = 29.6dB
    //so full scale pk magnitude = 13.5 - 29.6 = -16.1dBm at input connector

    int power_dbm = -16-(102-power);
    int s_scale;

    if(power_dbm < -63){
        power_dbm += 127;
        s_scale = power_dbm/6;
    } else {
        power_dbm += 73;
        s_scale = 9 + power_dbm/10;
    }

    return s_scale;
}

const attenuation_settings[10] = {17, 8, 7, 6, 5, 4, 3, 2, 1, 0};

void apply_settings (){
    unsigned attenuation; 
    unsigned control = 0;
    int rx_frequency_correction[6];

    //set volume
    attenuation = attenuation_settings[settings.volume];
    if(settings.mute) {
        attenuation = 17;
    }
    control |= (attenuation << 8);

    //set mode
    settings.mode &= 0x7;
    control |= settings.mode;

    //set agc speed
    settings.agc_speed &= 0x3;
    control |= (settings.agc_speed << 4);

    if(settings.test_signal) control |= 0x00000040u;
    if(settings.USB_audio)  control |= 0x00100000u;

    //force a band
    if(settings.band & 0x8){
        control |= ((settings.band & 0x7) << 21);
    } else {
        if(settings.frequency >= 2000000 && settings.frequency <4000000){
            control |= (3 << 21);
        } else if(settings.frequency >= 4000000 && settings.frequency < 8000000){
            control |= (2 << 21);
        } else if(settings.frequency >= 8000000 && settings.frequency < 16000000){
            control |= (1 << 21);
        } else if(settings.frequency >= 16000000 && settings.frequency < 30000000){
            control |= (0 << 21);
        } else {
            control |= (4 << 21);
        }
    }


                                            //Mode Clock Divider   NCO Offset
    rx_frequency_correction[0] = -12207;     //AM    1   48828    -12207
    rx_frequency_correction[1] = -24414;     //NFM   1   97656    -24414
    rx_frequency_correction[2] = -24414;     //FM    1   97656    -24414
    rx_frequency_correction[4] = -4578;      //LSB   4   24414    -4578
    rx_frequency_correction[3] = -7629;      //USB   4   24414    -7629
    rx_frequency_correction[5] = -8138;      //CW    3   32552    -8138

    if(settings.tx)         control |= 0x00000008u;
    if(settings.tx){
        //TX is direct conversion
        fputc(convert_to_steps(settings.frequency), frequency_out);
    } else {
        //Rx uses Fs/4 IF
        fputc(convert_to_steps(settings.frequency+rx_frequency_correction[settings.mode]), frequency_out);
    }

    fputc(control, control_out);


}

void update_lcd(){
    //update display status
    LCD_CLEAR()
    LCD_LINE1()
    print_frequency(settings.frequency);
    lcd_print("   ");
    lcd_print(modes[settings.mode]);
    LCD_LINE2()
    lcd_print(smeter[read_smeter()]);
}

void main(){

    stdout = debug_out;
    stdin = debug_in;
    puts("FPGA transceiver v 0.01\n");

    unsigned int cmd, power, i, page, pps_count, last_smeter=0;
    unsigned wake_time = 0;
    int audio;
    int capture[16], temp;
    
    //initialise peripherals
    lcdInit();
    init_ui();

    i2c_init(&bus, i2c_in, i2c_out);
    load_settings(&bus, 0);//page 0 contains power up settings
    apply_settings();
    update_lcd();

    while(1){


        if(ready(stdin)){ 
            cmd = getc();
            switch(cmd){
                case 'f': settings.frequency   = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'm': settings.mode        = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'b': settings.band        = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'A': settings.agc_speed   = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 't': settings.tx          = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'U': settings.USB_audio   = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'T': settings.test_signal = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'v': settings.volume      = scan_udecimal(); apply_settings(); update_lcd(); break;
                case 'q': settings.squelch     = scan_udecimal(); apply_settings(); update_lcd(); break;
                //case 'h':
                //print help
                    //euts("fxxxxxxxx: frequency\n");
                    //puts("mx: mode 0=LSB, 1=AM, 2=FM, 3=NBFM, 4=USB\n");
                    //puts("b: set band (decimal)\n");
                    //puts("p: read power (hex)\n");
                    //puts("s: read smeter\n");
                    //puts("v: set volume (0-9)\n");
                    //puts("q: set squelch (0-12)\n");
                    //puts("t: TX (0, 1)\n");
                    //puts("x: get GPS 1pps count\n");
                    //puts("a: adc\n");
                    //puts("A: AGC speed (0-3)\n");
                    //puts("T: test signal, (0, 1)\n");
                    //puts("O: get audio\n");
                    //puts("I: put audio\n");
                    //puts("U: set_usb_audio\n");
                    //puts("S: memory store\n");
                    //puts("\n");
                    //break;

                case 'x':
                    pps_count = fgetc(pps_count_in);
                    print_uhex(pps_count);
                    puts("\n");
                    break;

                case 'a':
                    for(i=0; i<10; i++){
                        capture[i] = fgetc(adc_in);
                    }
                    for(i=0; i<10; i++){
                        print_uhex(capture[i]);
                        puts("\n");
                    }
                    break;

                case 'p':
                //print rx magnitude (post filter)
                    power = fgetc(power_in);
                    print_uhex(power);
                    puts("\n");
                    break;

                case 's':
                //read smeter
                    puts(smeter[read_smeter()]);
                    puts("\n");
                    break;

                case 'c':
                    for(i=0;i<4000;i++){
                        temp = fgetc(capture_in);
                        putc(temp & 0xff);
                        putc(temp >> 8  & 0xff);
                        putc(temp >> 16 & 0xff);
                        putc(temp >> 24 & 0xff);
                    }
                    break;
                case 'S':
                    page = getc();
                    for(i=0;i<16;i++){
                        temp = getc();
                        temp |= getc() << 8;
                        temp |= getc() << 16;
                        temp |= getc() << 24;
                        capture[i] = temp;
                    }
                    eeprom_page_write(&bus, page, capture);
                    putc('k');//send acknowledgement
                    break;
                case 'O':
                    for(i=0;i<1000;i++){
                        audio =  fgetc(audio_in);
                        audio += fgetc(audio_in);
                        audio += fgetc(audio_in);
                        audio += fgetc(audio_in);
                        audio >>= 4;
                        putc(audio);
                        putc(audio>>8);
                    }
                    break;
                case 'I':
                    for(i=0;i<1000;i++){
                        audio = getc();
                        fputc(audio, audio_out);
                    }
                    break;
            }
       }

       
       if(timer_low() - wake_time > 2000000){ 
           wake_time = timer_low();
            settings.mute = read_smeter() < settings.squelch;

            //check transmit button
            if(check_ptt()){
                transmit();
                last_smeter = 1234567; //force smeter to be updated straight away.
            }

            //If knob is turned adjust frequency
            //don't store this in EEPROM to avoid wear
            position_change = get_position_change();
            if(position_change){
               settings.frequency += position_change * step_sizes[settings.step];
               if (settings.frequency > settings.max_frequency) settings.frequency = settings.min_frequency;
               if ((int)settings.frequency < (int)settings.min_frequency) settings.frequency = settings.max_frequency;
               apply_settings();
               update_lcd();
            }

            //if the menu was entered, update settings and
            //store them in EEPROM
            if(do_ui()){
                apply_settings();
                update_lcd();
                store_settings(&bus, 0);
            }
            

            if(last_smeter != read_smeter()){
                LCD_LINE2()
                lcd_print(smeter[read_smeter()]);
                last_smeter = read_smeter();
            }

       }

    }

}
