void eeprom_page_write(i2c *bus, unsigned page, unsigned data[]){
    unsigned nack, i;

    page <<= 6;
    i2c_write_byte(bus, 0xa0|I2C_START_FLAG);
    i2c_write_byte(bus, (page >> 8) & 0xff);//address high
    i2c_write_byte(bus, (page)&0xff);       //address lo

    for(i=0; i<16; i++){
        i2c_write_byte(bus, (data[i]&0xff));//data
        i2c_write_byte(bus, (data[i]>>8&0xff));//data
        i2c_write_byte(bus, (data[i]>>16&0xff));//data
        if(i==15) i2c_write_byte(bus, (data[i]>>24&0xff)|I2C_STOP_FLAG);//data
        else i2c_write_byte(bus, (data[i]>>24&0xff));//data
    }

    //poll ack to wait for end of write cycle
    do {nack = i2c_write_byte(bus, 0xa0|I2C_START_FLAG);} while (nack);
}

void eeprom_page_read(i2c *bus, unsigned page, unsigned data[]){
    unsigned word, i;

    page <<= 6;
    i2c_write_byte(bus, 0xa0|I2C_START_FLAG);
    i2c_write_byte(bus, (page >> 8) & 0xff);//address high
    i2c_write_byte(bus, (page)&0xff);       //address lo
    i2c_write_byte(bus, 0xa1|I2C_START_FLAG);  //read

    for(i=0; i<16; i++){
        word = i2c_read_byte(bus, 0);
        word |= i2c_read_byte(bus, 0) << 8;
	word |= i2c_read_byte(bus, 0) << 16;
        word |= i2c_read_byte(bus, 0) << 24;
	data[i] = word;
    }
    i2c_write_byte(bus, I2C_NACK_FLAG|I2C_STOP_FLAG);//data
}

void eeprom_byte_write(i2c *bus, unsigned address, unsigned data){
    unsigned nack;

    i2c_write_byte(bus, 0xa0|I2C_START_FLAG);
    i2c_write_byte(bus, (address >> 8) & 0xff);//address high
    i2c_write_byte(bus, (address)&0xff);       //address lo
    i2c_write_byte(bus, (data&0xff)|I2C_STOP_FLAG);//data

    //poll ack to wait for end of write cycle
    do {nack = i2c_write_byte(bus, 0xa0|I2C_START_FLAG);} while (nack);
}

unsigned eeprom_random_read(i2c *bus, unsigned address){
    i2c_write_byte(bus, 0xa0|I2C_START_FLAG);
    i2c_write_byte(bus, (address >> 8) & 0xff);//address high
    i2c_write_byte(bus, (address)&0xff);       //address lo
    i2c_write_byte(bus, 0xa1|I2C_START_FLAG);  //read
    return i2c_read_byte(bus, I2C_STOP_FLAG|I2C_NACK_FLAG);//data
}
