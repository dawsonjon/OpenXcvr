unsigned frequency_out = output("frequency_out");
unsigned control_out = output("control_out");
unsigned debug_out = output("debug_out");
unsigned debug_in = input("debug_in");

#include <stdio.h>
#include <scan.h>
#include <print.h>

void main(){

    stdout = debug_out;
    stdin = debug_in;

    unsigned int cmd, frequency, control;

        puts("FPGA transceiver v 0.01\n");
        puts("fxxxxxxxx: frequency\n");
        puts("mx: mode 0=LSB, 1=AM, 2=FM, 3=NBFM, 4=USB\n");

    while(1){


        cmd = getc();
        switch(cmd){
            case 'f':
                frequency = scan_uhex();
                puts("frequency: ");
                print_uhex(frequency);
                puts("\n");
                fputc(frequency, frequency_out);
                break;

            case 'm':
                control = scan_uhex();
                puts("mode : ");
                print_uhex(control);
                puts("\n");
                fputc(control, control_out);
                break;

            case 'h':
                puts("fxxxxxxxx: frequency\n");
                puts("mx: mode 0=LSB, 1=AM, 2=FM, 3=NBFM, 4=USB\n");
                puts("\n");
                break;
        }

    }
    puts(">");

}
