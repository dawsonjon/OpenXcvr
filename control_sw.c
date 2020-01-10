unsigned frequency_out = output("frequency_out");
unsigned control_out = output("control_out");
unsigned debug_out = output("debug_out");
unsigned debug_in = input("debug_in");
unsigned capture_in = input("capture_in");
unsigned power_in = input("power_in");
unsigned gain_in = input("gain_in");

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

void main(){

    stdout = debug_out;
    stdin = debug_in;

    unsigned int cmd, frequency, control, gain, power, i;
    unsigned int capture[1000];

    fputc(convert_to_steps(1215000-18311), frequency_out);

    puts("FPGA transceiver v 0.01\n");


    while(1){


        cmd = getc();
        switch(cmd){
            case 'f':
            //set frequency, reduce by fs/4
                frequency = scan_udecimal();
                puts("frequency: ");
                print_uhex(frequency);
                puts("\n");
                fputc(convert_to_steps(frequency-18311), frequency_out);
                break;

            case 'm':
            //set mode/sideband
                control = scan_uhex();
                puts("mode : ");
                print_uhex(control);
                puts("\n");
                fputc(control, control_out);
                break;

            case 'h':
            //print help
                puts("fxxxxxxxx: frequency\n");
                puts("mx: mode 0=LSB, 1=AM, 2=FM, 3=NBFM, 4=USB\n");
                puts("g: read gain (hex)\n");
                puts("p: read power (hex)\n");
                puts("\n");
                break;

            case 'g':
            //print rx gain
                gain = fgetc(gain_in);
                print_uhex(gain);
                puts("\n");
                break;

            case 'p':
            //print rx magnitude (post filter)
                power = fgetc(power_in);
                print_uhex(power);
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
        puts(">");

    }

}
