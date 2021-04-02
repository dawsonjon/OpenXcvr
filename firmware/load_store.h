void store_settings(i2c *bus, unsigned page){
    unsigned buffer[16], i;
    
    for(i=0; i<11; i++){
        buffer[i] = settings[i];
    }

    //program to 0 to indicate that data has been stored
    buffer[15] = 0;
    eeprom_page_write(bus, page, buffer);
}

void load_settings(i2c *bus, unsigned page){
    unsigned buffer[16], i;
    eeprom_page_read(bus, page, buffer);

    //copy settings from eeprom
    for(i=0; i<11; i++){
	    //These settings are retained between power ups, but not stored
	    if(page){
		    if(i==idx_volume)    continue;
		    if(i==idx_cw_speed)  continue;
		    if(i==idx_pps_count) continue;
	    }
	    settings[i] = buffer[i];
    }

    settings[idx_band]=0;
    settings[idx_test_signal]=0;
    settings[idx_USB_audio]=0;
    settings[idx_tx]=0;
    settings[idx_mute]=0;
}

void factory_reset(i2c *bus){
    unsigned buffer[16], i;

    //factory default settings (page 0)
    settings[idx_frequency] = 1215000;
    settings[idx_mode]      = 0; //AM
    settings[idx_agc_speed] = 2; //normal
    settings[idx_step]      = 3; //1kHz
    settings[idx_squelch]   = 0; //Off
    settings[idx_volume]    = 5; //mid way
    settings[idx_max_frequency] = 29999999;
    settings[idx_min_frequency] = 100;
    settings[idx_mic_gain] = 0;
    settings[idx_cw_speed] = 12;
    settings[idx_pps_count] = 150000000;
    settings[idx_band]=0;
    settings[idx_test_signal]=0;
    settings[idx_USB_audio]=0;
    settings[idx_tx]=0;
    settings[idx_mute]=0;
    store_settings(bus, 0);//page 0 contains power up settings

    //clear all memories (page 1-511)
    for(i=0; i<16; i++) buffer[i] = 0xffffffffu;
    for(i=1; i<512; i++) eeprom_page_write(bus, i, buffer);
}
