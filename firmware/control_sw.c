unsigned frequency_out = output("frequency_out");
unsigned control_out = output("control_out");
unsigned debug_out = output("debug_out");
unsigned debug_in = input("debug_in");
unsigned capture_in = input("capture_in");
unsigned power_in = input("power_in");
unsigned pps_count_in = input("pps_count_in");
unsigned adc_in = input("adc_in");

#include <stdio.h>
#include <scan.h>
#include <print.h>

//int(round((2**32)*(2**32)/300e6))
#define FREQUENCY_STEP_MULTIPLIER 61489146912ul

//convert a frequency in Hertz into a frequency in NCO step size.
unsigned convert_to_steps(unsigned x){
    unsigned long long y = x * FREQUENCY_STEP_MULTIPLIER;
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
int read_smeter(unsigned gain){

    gain = to_dB(gain);
    unsigned power = to_dB(fgetc(power_in));

    //ADC has 1.5Vpk = 1.06Vrms = 0.0225W into 50ohm = 22.5mW = 13.5dBm
    //Receiver has a gain of 1+(2*2k2/150) = 30.33.. = 29.6dB
    //so full scale pk magnitude = 13.5 - 29.6 = -16.1dBm at input connector

    int power_dbm = -16-(102-power)-gain;
    int s_scale;

    if(power_dbm < -63){
        power_dbm += 127;
        s_scale = 0;
        while(power_dbm >= 6){
            power_dbm -= 6;
            s_scale += 1;
        }
    } else {
        power_dbm += 73;
        s_scale = 9;
        while(power_dbm >= 10){
            power_dbm -= 10;
            s_scale += 1;
        }
    }

    return s_scale;
}

void set_volume(unsigned volume, unsigned * control){
    unsigned attenuation; 
    switch(volume){
        case 9: attenuation = 0; break;
        case 8: attenuation = 1; break;
        case 7: attenuation = 2; break;
        case 6: attenuation = 3; break;
        case 5: attenuation = 4; break;
        case 4: attenuation = 5; break;
        case 3: attenuation = 6; break;
        case 2: attenuation = 7; break;
        case 1: attenuation = 8; break;
        case 0: attenuation = 17; break;
    }
    *control &= 0xffff00ffu;
    *control |= (attenuation << 8);
    fputc(*control, control_out);
}

void set_mode(unsigned mode, unsigned * control){
    mode &= 0x7;
    *control &= 0xfffffff8u;
    *control |= mode;
    fputc(*control, control_out);
}

void set_agc_speed(unsigned agc_speed, unsigned * control){
    agc_speed &= 0x3;
    *control &= 0xffffffcfu;
    *control |= (agc_speed << 4);
    fputc(*control, control_out);
}

void set_gain(unsigned gain, unsigned * control){
    gain &= 0xf;
    *control &= 0xfff0ffffu;
    *control |= (gain << 16);
    fputc(*control, control_out);
}

void set_tx(unsigned tx, unsigned frequency, unsigned * control){

    if(tx){
        *control |= 0x00000008u;
    } else {
        *control &= ~0x00000008u;
    }

    if(tx){
        //RX has an FS/4 IF
        fputc(convert_to_steps(frequency), frequency_out);
    } else {
        //TX is direct conversion
        fputc(convert_to_steps(frequency-24414), frequency_out);
    }

    fputc(*control, control_out);

}

void set_test_signal(unsigned on, unsigned * control){
    if(on){
        *control |= 0x00000040u;
    } else {
        *control &= ~0x00000040u;
    }
    fputc(*control, control_out);
}

void main(){

    stdout = debug_out;
    stdin = debug_in;

    unsigned int cmd, frequency=1215000-24414, control=0x1100, gain=0, power, i, smeter, volume=9, squelch=0, mode, pps_count, adc, agc_speed;
    unsigned int capture[1000];

    fputc(convert_to_steps(1215000-24414), frequency_out);
    fputc(control, control_out);

    puts("FPGA transceiver v 0.01\n");


    while(1){


        if(ready(stdin)){ 
            cmd = getc();
            switch(cmd){
                case 'f':
                //set frequency, reduce by fs/4
                    frequency = scan_udecimal();
                    puts("frequency: ");
                    print_uhex(frequency);
                    puts("\n");
                    fputc(convert_to_steps(frequency-24414), frequency_out);
                    break;

                case 'm':
                //set mode/sideband
                    mode = scan_udecimal();
                    set_mode(mode, &control);
                    puts("control : ");
                    print_uhex(control);
                    puts("\n");
                    break;

                case 'A':
                //set mode/sideband
                    agc_speed = scan_udecimal();
                    set_agc_speed(agc_speed, &control);
                    puts("control : ");
                    print_uhex(control);
                    puts("\n");
                    break;

                case 't':
                //set tx
                    set_tx(scan_udecimal(), frequency, &control);
                    puts("control : ");
                    print_uhex(control);
                    puts("\n");
                    break;

                case 'T':
                //set tx
                    set_test_signal(scan_udecimal(), &control);
                    puts("control : ");
                    print_uhex(control);
                    puts("\n");
                    break;

                case 'h':
                //print help
                    puts("fxxxxxxxx: frequency\n");
                    puts("mx: mode 0=LSB, 1=AM, 2=FM, 3=NBFM, 4=USB\n");
                    puts("g: set gain (decimal)\n");
                    puts("p: read power (hex)\n");
                    puts("s: read smeter\n");
                    puts("v: set volume (0-9)\n");
                    puts("q: set squelch (0-12)\n");
                    puts("t: TX (0, 1)\n");
                    puts("x: get GPS 1pps count\n");
                    puts("a: adc\n");
                    puts("A: AGC speed (0-3)\n");
                    puts("T: test signal, (0, 1)\n");
                    puts("\n");
                    break;

                case 'x':
                    pps_count = fgetc(pps_count_in);
                    print_uhex(pps_count);
                    puts("\n");
                    break;

                case 'a':
                    for(i=0; i<5; i++){
                        capture[i] = fgetc(adc_in);
                    }
                    for(i=0; i<5; i++){
                        print_uhex(capture[i]);
                        puts("\n");
                    }
                    break;

                case 'g':
                    set_gain(scan_udecimal(), &control);
                    print_uhex(control);
                    puts("\n");
                    break;

                case 'v':
                    volume = scan_udecimal();
                    set_volume(volume, &control);
                    print_uhex(volume);
                    puts("\n");
                    break;

                case 'q':
                    squelch = scan_udecimal();
                    print_uhex(squelch);
                    puts("\n");
                    break;

                case 'p':
                //print rx magnitude (post filter)
                    power = fgetc(power_in);
                    print_uhex(power);
                    puts("\n");
                    break;

                case 's':
                //read smeter
                    smeter = read_smeter(gain);
                    putc('s');
                    if(smeter <= 9){
                        putc('0'+smeter);
                    } else if(smeter == 10){
                        puts("9+10dB");
                    } else if(smeter == 11){
                        puts("9+20dB");
                    } else if(smeter == 12){
                        puts("9+30dB");
                    }
                    puts("\n");
                    break;

                case 'c':
                    for(i=0;i<1000;i++){
                        capture[i] = fgetc(capture_in);
                    }
                    for(i=0;i<1000;i++){
                        print_uhex(capture[i]&0xffff);
                        puts("\n");
                        print_uhex((capture[i]>>16)&0xffff);
                        puts("\n");
                    }
                    break;
            }
        }

        //implement squelch by muting the audio if s-meter
        //falls bellow specified value
        if(read_smeter(gain) < squelch){
            set_volume(0, &control);
        } else {
            set_volume(volume, &control);
        }

    }

}
