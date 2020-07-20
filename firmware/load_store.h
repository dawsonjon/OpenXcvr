void store_settings(i2c *bus, unsigned page){
    unsigned buffer[16];
    buffer[0] = settings.frequency;
    buffer[1] = settings.mode;
    buffer[2] = settings.agc_speed;
    buffer[3] = settings.step;
    buffer[4] = settings.squelch;
    buffer[5] = settings.volume;
    buffer[6] = settings.max_frequency;
    buffer[7] = settings.min_frequency;
    buffer[8] = settings.mic_gain;
    buffer[9] = settings.cw_speed;
   
    //program to 0 to indicate that data has been stored
    buffer[15] = 0;
    eeprom_page_write(bus, page, buffer);
}

void load_settings(i2c *bus, unsigned page){
    unsigned buffer[16];
    eeprom_page_read(bus, page, buffer);
    int i;

    settings.frequency = buffer[0];
    settings.mode      = buffer[1];
    settings.agc_speed = buffer[2];
    settings.step      = buffer[3];
    settings.squelch   = buffer[4];
    settings.max_frequency = buffer[6];
    settings.min_frequency = buffer[7];
    settings.mic_gain = buffer[8];
    settings.tx=0;
    settings.mute=0;

    //page 0 contains power up settings
    //load things like volume which wouldn't normally be stored
    if(page==0){
        settings.volume = buffer[5];
        settings.cw_speed = buffer[9];
    }
}

void factory_reset(i2c *bus){
    unsigned buffer[16], i;

    //factory default settings (page 0)
    buffer[0] = 1215000;
    buffer[1] = 0; //AM
    buffer[2] = 2; //normal
    buffer[3] = 3; //1kHz
    buffer[4] = 0; //Off
    buffer[5] = 5; //mid way
    buffer[6] = 29999999;
    buffer[7] = 100;
    buffer[8] = 0;
    buffer[9] = 12;

    settings.frequency = 1215000;
    settings.mode      = 0; //AM
    settings.agc_speed = 2; //normal
    settings.step      = 3; //1kHz
    settings.squelch   = 0; //Off
    settings.volume    = 5; //mid way
    settings.max_frequency = 29999999;
    settings.min_frequency = 100;
    settings.mic_gain = 0;
    settings.cw_speed = 12;
    buffer[15] = 0;
    eeprom_page_write(bus, 0, buffer);

    //clear all memories (page 1-511)
    for(i=0; i<16; i++) buffer[i] = 0xffffffffu;
    for(i=1; i<512; i++) eeprom_page_write(bus, i, buffer);
}
