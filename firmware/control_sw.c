unsigned frequency_out = output("frequency_out");
unsigned control_out = output("control_out");
unsigned debug_out = output("debug_out");
unsigned debug_in = input("debug_in");
unsigned capture_in = input("capture_in");
unsigned power_in = input("power_in");
unsigned pps_count_in = input("pps_count_in");
unsigned adc_in = input("adc_in");
unsigned position_in = input("position_in");
unsigned push_button_in = input("pb_in");
unsigned i2c_in = input("i2c_in");
unsigned i2c_out = output("i2c_out");

#include <print.h>
#include <scan.h>
#include <stdio.h>

// int(round((2**32)*(2**32)/300e6))
#define FREQUENCY_STEP_MULTIPLIER 61489146912ul

// settings that get stored in eeprom
#define idx_frequency 0
#define idx_mode 1
#define idx_agc_speed 2
#define idx_step 3
#define idx_squelch 4
#define idx_volume 5
#define idx_max_frequency 6
#define idx_min_frequency 7
#define idx_mic_gain 8
#define idx_cw_speed 9
#define idx_pps_count 10

// settings that are transient
#define idx_band 11
#define idx_test_signal 12
#define idx_USB_audio 13
#define idx_tx 14
#define idx_mute 15

unsigned settings[16];

void apply_settings();
void update_lcd(unsigned cat_mode);

#include "i2c.h"
i2c bus;
#include "eeprom.h"
#include "load_store.h"
#include "ui.h"
#include "transmit.h"
#include "utils.h"

// convert a frequency in Hertz into a frequency in NCO step size.
unsigned convert_to_steps(unsigned x) {
  unsigned long long y = x * FREQUENCY_STEP_MULTIPLIER;
  y >>= 32;
  y *= 150000000;
  y = divide(y, settings[idx_pps_count]);
  return y;
}

// convert dBs to s-meter scale
int read_smeter() {

  unsigned power = to_dB(fgetc(power_in));

  // ADC has 1.5Vpk = 1.06Vrms = 0.0225W into 50ohm = 22.5mW = 13.5dBm
  // Receiver has a gain of (220/50)*(3300/100) = 145.2 = 43dB
  // so full scale pk magnitude = 13.5 - 43 = -29.5dBm at input connector

  int power_dbm = -29 - (102 - power);
  int s_scale;

  if (power_dbm < -63) {
    power_dbm += 127;
    s_scale = power_dbm / 6;
  } else {
    power_dbm += 73;
    s_scale = 9 + power_dbm / 10;
  }

  return s_scale;
}

const attenuation_settings[10] = {17, 8, 7, 6, 5, 4, 3, 2, 1, 0};

void apply_settings() {
  unsigned attenuation;
  unsigned control = 0;
  int rx_frequency_correction[6];

  // set volume
  attenuation = attenuation_settings[settings[idx_volume]];
  if (settings[idx_mute]) {
    attenuation = 18; // use a special value to indicate mute due to squelch
  }
  control |= (attenuation << 8);

  // set mode
  settings[idx_mode] &= 0x7;
  control |= settings[idx_mode];

  // set agc speed
  settings[idx_agc_speed] &= 0x3;
  control |= (settings[idx_agc_speed] << 4);

  if (settings[idx_test_signal])
    control |= 0x00000040u;
  if (settings[idx_USB_audio])
    control |= 0x00100000u;

  // force a band
  if (settings[idx_band] & 0x8) {
    control |= ((settings[idx_band] & 0x7) << 21);
  } else {
    if (settings[idx_frequency] >= 2000000 &&
        settings[idx_frequency] < 4000000) {
      control |= (3 << 21);
    } else if (settings[idx_frequency] >= 4000000 &&
               settings[idx_frequency] < 8000000) {
      control |= (2 << 21);
    } else if (settings[idx_frequency] >= 8000000 &&
               settings[idx_frequency] < 16000000) {
      control |= (1 << 21);
    } else if (settings[idx_frequency] >= 16000000 &&
               settings[idx_frequency] < 30000000) {
      control |= (0 << 21);
    } else {
      control |= (4 << 21);
    }
  }

  // set mic gain
  settings[idx_mic_gain] &= 0xf;
  control |= (settings[idx_mic_gain] << 24);
  // Mode Clock Divider   NCO Offset
  rx_frequency_correction[0] = -12207; // AM    2   48828    -12207
  rx_frequency_correction[1] = -24414; // NFM   1   97656    -24414
  rx_frequency_correction[2] = -24414; // FM    1   97656    -24414
  rx_frequency_correction[4] = -10681; // LSB   4   24414    -10681
  rx_frequency_correction[3] = -13732; // USB   4   24414    -13732
  rx_frequency_correction[5] = -8138;  // CW    3   32552    -8138

  if (tx_on && settings[idx_frequency] >= 3500000 &&
      settings[idx_frequency] <= 29700000)
    control |= 0x00000008u;
  if (tx_on) {
    // TX is direct conversion
    fputc(convert_to_steps(settings[idx_frequency]), frequency_out);
  } else {
    // Rx uses Fs/4 IF
    fputc(convert_to_steps(settings[idx_frequency] +
                           rx_frequency_correction[settings[idx_mode]]),
          frequency_out);
  }

  fputc(control, control_out);
}

void update_lcd(unsigned cat_mode) {
  // update display status
  LCD_CLEAR() //this takes a long time, so might need to reivew
  LCD_LINE1()
  lcd_print_decimal(settings[idx_frequency], 5, 3);
  if(cat_mode){
    lcd_print(" C ");
  } else {
    lcd_print("   ");
  }
  print_option(MODES, settings[idx_mode]);
  LCD_LINE2()
  print_option(SMETER, read_smeter());
}

void main() {

  stdout = debug_out;
  stdin = debug_in;
  puts("FPGA transceiver v 0.01\n");

  unsigned int power, i, pps_count;
  unsigned wake_time = 0;
  int audio;
  int position_change = 0;

  // initialise peripherals
  lcdInit();
  i2c_init(&bus, i2c_in, i2c_out);
  load_settings(&bus, 0); // page 0 contains power up settings
  apply_settings();
  update_lcd(cat_mode);

  while (1) {

    if(cat_mode && ready(stdin)){
      cat();
    }


    if(tx_on){

        if (timer_low() - wake_time > 500000) {
          wake_time = timer_low();
          transmit();
        }

    } else {

        if (timer_low() - wake_time > 5000000) {
          wake_time = timer_low();

          settings[idx_mute] = read_smeter() < settings[idx_squelch];

          // If knob is turned adjust frequency
          // don't store this in EEPROM to avoid wear
          position_change = get_position_change();
          if (position_change) {
            if (check_button(4)) {
              settings[idx_frequency] +=
                  position_change * step_sizes[settings[idx_step]] * 10;
            } else if (check_button(8)) {
              settings[idx_frequency] +=
                  position_change * step_sizes[settings[idx_step]] / 10;
            } else {
              settings[idx_frequency] +=
                  position_change * step_sizes[settings[idx_step]];
            }
            if (settings[idx_frequency] > settings[idx_max_frequency])
              settings[idx_frequency] = settings[idx_min_frequency];
            if ((int)settings[idx_frequency] < (int)settings[idx_min_frequency])
              settings[idx_frequency] = settings[idx_max_frequency];
            apply_settings();
          }

          //pressing any key cancels cat mode
          if(cat_mode){
            if(check_button(3)){
              get_button(3);
              cat_mode = 0;
              settings[idx_tx] = 0;
            }
          }
          // if the menu was entered, update settings and
          // store them in EEPROM
          else{
            if (do_ui()) {
              apply_settings();
              store_settings(&bus, 0);
            }
          }

          update_lcd(cat_mode);

          // check transmit button etc
          check_ptt();

      }
    }
  }
}

