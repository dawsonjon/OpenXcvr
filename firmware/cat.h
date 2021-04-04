unsigned checksum;

char sumbyte() {
  char byte = getc();
  checksum += byte;
  checksum &= 0xff;
  return byte;
}

int checkbyte() return getc() == checksum;

void send_status(int len, char *data){
  int i;
  putc(0x55);
  putc(len);
  for(i=0; i<len; i++){
    putc(data[i]);
  }
}

void cat() {
  char cmd;
  int page, temp, i;
  unsigned buffer[16];
  unsigned sample_time=0;

  //clear any data already in the buffer.
  while (ready(stdin)) {
    getc();
  }
  while (1) {
    cmd = getc();
    switch (cmd) {

    // set a setting
    case 's':
      // value from 0 to 15
      checksum = 's';
      page = sumbyte() & 0xf;
      temp = sumbyte();
      temp |= sumbyte() << 8;
      temp |= sumbyte() << 16;
      temp |= sumbyte() << 24;
      if (!checkbyte()) {
	send_status(1, "X");
	break;
      }
      settings[page] = temp;
      apply_settings();
      putc(0x55);
      putc(1);
      putc('K');
      //send_status(1, "K");
      break;

    // get a setting
    case 'g':
      // value from 0 to 15
      page = getc() & 0xf;
      temp = settings[page];
      buffer[0] = temp & 0xff;
      buffer[1] = temp >> 8 & 0xff;
      buffer[2] = temp >> 16 & 0xff;
      buffer[3] = temp >> 24 & 0xff;
      send_status(4, buffer);
      break;

    //capture raw ADC data
    case 'c':
	for(i=0;i<2048;i++){
	    temp = fgetc(capture_in);
	    buffer[0] = temp & 0xff;
	    buffer[1] = temp >> 8 & 0xff;
	    buffer[2] = temp >> 16 & 0xff;
	    buffer[3] = temp >> 24 & 0xff;
	    send_status(4, buffer);
	}
	break;

    // upload settings to a page of eeprom
    case 'S':
      page = getc();
      page <<= 8;
      page |= getc();
      for (i = 0; i < 16; i++) {
	temp = getc();
	temp |= getc() << 8;
	temp |= getc() << 16;
	temp |= getc() << 24;
	buffer[i] = temp;
      }
      eeprom_page_write(&bus, page, buffer);
      break;

    // output audio
    case 'O':
      putc(0xAA);
      break;

    // input audio
    case 'I':
      //play back at 50kHz sample rate
      for (i = 0; i < 1024; i++) {
	temp = getc();
	while(timer_low() - sample_time < 966){}
	sample_time = timer_low();
	fputc(temp<<4, audio_out);
      }
      send_status(1, "K");
      break;

    }

    if(check_button(3)){
	    get_button(3);
	    return;
    }
  }
}
