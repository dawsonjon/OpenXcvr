EESchema Schematic File Version 5
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 3 7
Title "Open XCVR"
Date "2020-06-14"
Rev "0.2"
Comp "Jon Dawson"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
Comment5 ""
Comment6 ""
Comment7 ""
Comment8 ""
Comment9 ""
$EndDescr
Connection ~ 3100 4800
Connection ~ 4200 4100
Connection ~ 4250 4200
Connection ~ 6150 3500
Connection ~ 6150 5100
Connection ~ 7500 3700
Connection ~ 7800 3200
Connection ~ 7800 3500
Connection ~ 7800 4800
Connection ~ 7800 5100
Connection ~ 8750 3200
Connection ~ 8750 3600
Connection ~ 8750 4800
Connection ~ 8750 5200
Connection ~ 9450 3600
Connection ~ 9450 5200
NoConn ~ 4000 4300
NoConn ~ 4000 4400
NoConn ~ 4000 4600
NoConn ~ 4000 4700
Wire Wire Line
	1050 4200 1400 4200
Wire Wire Line
	1050 4500 1050 4200
Wire Wire Line
	1200 3800 1400 3800
Wire Wire Line
	2200 3800 2250 3800
Wire Wire Line
	2200 4000 2350 4000
Wire Wire Line
	2200 4200 2500 4200
Wire Wire Line
	2250 3550 2500 3550
Wire Wire Line
	2250 3800 2250 3550
Wire Wire Line
	2350 4000 2350 3900
Wire Wire Line
	2350 4500 3200 4500
Wire Wire Line
	2350 4600 3200 4600
Wire Wire Line
	2350 4800 3100 4800
Wire Wire Line
	2800 3550 3000 3550
Wire Wire Line
	2800 4200 3200 4200
Wire Wire Line
	3000 3550 3000 4100
Wire Wire Line
	3000 4100 3200 4100
Wire Wire Line
	3100 4800 3200 4800
Wire Wire Line
	3100 4900 3100 4800
Wire Wire Line
	3200 1100 3200 1150
Wire Wire Line
	3200 1750 3200 1850
Wire Wire Line
	3200 4900 3100 4900
Wire Wire Line
	3550 1150 3550 1300
Wire Wire Line
	3550 1600 3550 1700
Wire Wire Line
	3600 3800 3600 3900
Wire Wire Line
	3600 5100 3600 5350
Wire Wire Line
	4000 1150 4000 1300
Wire Wire Line
	4000 1600 4000 1700
Wire Wire Line
	4000 4100 4200 4100
Wire Wire Line
	4000 4200 4250 4200
Wire Wire Line
	4000 4800 4250 4800
Wire Wire Line
	4000 4900 4200 4900
Wire Wire Line
	4200 4100 4600 4100
Wire Wire Line
	4200 4900 4200 4100
Wire Wire Line
	4250 4200 4600 4200
Wire Wire Line
	4250 4800 4250 4200
Wire Wire Line
	4600 3500 6150 3500
Wire Wire Line
	4600 4100 4600 3500
Wire Wire Line
	4600 4200 4600 5100
Wire Wire Line
	4600 5100 6150 5100
Wire Wire Line
	6150 3500 6150 3700
Wire Wire Line
	6150 3500 6850 3500
Wire Wire Line
	6150 4000 6150 4150
Wire Wire Line
	6150 5100 6150 5300
Wire Wire Line
	6150 5100 6850 5100
Wire Wire Line
	6150 5600 6150 5750
Wire Wire Line
	7150 3500 7800 3500
Wire Wire Line
	7150 5100 7800 5100
Wire Wire Line
	7500 3300 7500 3700
Wire Wire Line
	7500 3700 7500 5300
Wire Wire Line
	7500 3700 7950 3700
Wire Wire Line
	7500 5300 7950 5300
Wire Wire Line
	7800 2750 7800 3200
Wire Wire Line
	7800 3200 8100 3200
Wire Wire Line
	7800 3500 7800 3200
Wire Wire Line
	7800 4400 7800 4800
Wire Wire Line
	7800 4800 7800 5100
Wire Wire Line
	7800 5100 7950 5100
Wire Wire Line
	7950 3500 7800 3500
Wire Wire Line
	8100 2750 7800 2750
Wire Wire Line
	8100 4400 7800 4400
Wire Wire Line
	8100 4800 7800 4800
Wire Wire Line
	8400 2750 8750 2750
Wire Wire Line
	8400 3200 8750 3200
Wire Wire Line
	8400 4400 8750 4400
Wire Wire Line
	8400 4800 8750 4800
Wire Wire Line
	8750 2750 8750 3200
Wire Wire Line
	8750 3200 8750 3600
Wire Wire Line
	8750 3600 8550 3600
Wire Wire Line
	8750 3600 9000 3600
Wire Wire Line
	8750 4400 8750 4800
Wire Wire Line
	8750 4800 8750 5200
Wire Wire Line
	8750 5200 8550 5200
Wire Wire Line
	8750 5200 9000 5200
Wire Wire Line
	9100 4200 9450 4200
Wire Wire Line
	9100 4300 9800 4300
Wire Wire Line
	9100 4400 9450 4400
Wire Wire Line
	9300 3600 9450 3600
Wire Wire Line
	9300 5200 9450 5200
Wire Wire Line
	9450 3600 9600 3600
Wire Wire Line
	9450 4200 9450 3600
Wire Wire Line
	9450 4400 9450 5200
Wire Wire Line
	9450 5200 9600 5200
Wire Wire Line
	9800 4300 9800 4600
Text Notes 2200 3450 2    50   ~ 0
Primary 4T Unifilar\nSecondary 2T Bifilar\n
Text GLabel 1200 3800 0    50   BiDi ~ 0
RF_BPF
Text GLabel 2350 4500 0    50   Input ~ 0
LO_I
Text GLabel 2350 4600 0    50   Input ~ 0
LO_Q
Text GLabel 2350 4800 0    50   BiDi ~ 0
TX_ENABLE
Text GLabel 9600 3600 2    50   Input ~ 0
RX_I
Text GLabel 9600 5200 2    50   Input ~ 0
RX_Q
$Comp
L power:+2V5 #PWR041
U 1 1 5E6A7FCA
P 2350 3900
F 0 "#PWR041" H 2350 3750 50  0001 C CNN
F 1 "+2V5" H 2365 4073 50  0000 C CNN
F 2 "" H 2350 3900 50  0001 C CNN
F 3 "" H 2350 3900 50  0001 C CNN
	1    2350 3900
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR042
U 1 1 5E2E2ABD
P 3200 1100
F 0 "#PWR042" H 3200 950 50  0001 C CNN
F 1 "+5V" H 3215 1273 50  0000 C CNN
F 2 "" H 3200 1100 50  0001 C CNN
F 3 "" H 3200 1100 50  0001 C CNN
	1    3200 1100
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR044
U 1 1 5E41F324
P 3550 1150
F 0 "#PWR044" H 3550 1000 50  0001 C CNN
F 1 "+5V" H 3565 1323 50  0000 C CNN
F 2 "" H 3550 1150 50  0001 C CNN
F 3 "" H 3550 1150 50  0001 C CNN
	1    3550 1150
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR046
U 1 1 5E3043EB
P 3600 3800
F 0 "#PWR046" H 3600 3650 50  0001 C CNN
F 1 "+5V" H 3615 3973 50  0000 C CNN
F 2 "" H 3600 3800 50  0001 C CNN
F 3 "" H 3600 3800 50  0001 C CNN
	1    3600 3800
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0102
U 1 1 5ECD0B83
P 4000 1150
F 0 "#PWR0102" H 4000 1000 50  0001 C CNN
F 1 "+5V" H 4015 1323 50  0000 C CNN
F 2 "" H 4000 1150 50  0001 C CNN
F 3 "" H 4000 1150 50  0001 C CNN
	1    4000 1150
	1    0    0    -1  
$EndComp
$Comp
L power:+2V5 #PWR050
U 1 1 5E6C5245
P 7500 3300
F 0 "#PWR050" H 7500 3150 50  0001 C CNN
F 1 "+2V5" H 7515 3473 50  0000 C CNN
F 2 "" H 7500 3300 50  0001 C CNN
F 3 "" H 7500 3300 50  0001 C CNN
	1    7500 3300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR040
U 1 1 5E6A9694
P 1050 4500
F 0 "#PWR040" H 1050 4250 50  0001 C CNN
F 1 "GND" H 1055 4327 50  0000 C CNN
F 2 "" H 1050 4500 50  0001 C CNN
F 3 "" H 1050 4500 50  0001 C CNN
	1    1050 4500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR043
U 1 1 5E2E1D5D
P 3200 1850
F 0 "#PWR043" H 3200 1600 50  0001 C CNN
F 1 "GND" H 3205 1677 50  0000 C CNN
F 2 "" H 3200 1850 50  0001 C CNN
F 3 "" H 3200 1850 50  0001 C CNN
	1    3200 1850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR045
U 1 1 5E418F7E
P 3550 1700
F 0 "#PWR045" H 3550 1450 50  0001 C CNN
F 1 "GND" H 3555 1527 50  0000 C CNN
F 2 "" H 3550 1700 50  0001 C CNN
F 3 "" H 3550 1700 50  0001 C CNN
	1    3550 1700
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR047
U 1 1 5E2FDE55
P 3600 5350
F 0 "#PWR047" H 3600 5100 50  0001 C CNN
F 1 "GND" H 3605 5177 50  0000 C CNN
F 2 "" H 3600 5350 50  0001 C CNN
F 3 "" H 3600 5350 50  0001 C CNN
	1    3600 5350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0103
U 1 1 5ECD0B93
P 4000 1700
F 0 "#PWR0103" H 4000 1450 50  0001 C CNN
F 1 "GND" H 4005 1527 50  0000 C CNN
F 2 "" H 4000 1700 50  0001 C CNN
F 3 "" H 4000 1700 50  0001 C CNN
	1    4000 1700
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR048
U 1 1 5E73DEF2
P 6150 4150
F 0 "#PWR048" H 6150 3900 50  0001 C CNN
F 1 "GND" H 6155 3977 50  0000 C CNN
F 2 "" H 6150 4150 50  0001 C CNN
F 3 "" H 6150 4150 50  0001 C CNN
	1    6150 4150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR049
U 1 1 5E73A28C
P 6150 5750
F 0 "#PWR049" H 6150 5500 50  0001 C CNN
F 1 "GND" H 6155 5577 50  0000 C CNN
F 2 "" H 6150 5750 50  0001 C CNN
F 3 "" H 6150 5750 50  0001 C CNN
	1    6150 5750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0105
U 1 1 5EDC0D6C
P 9800 4600
F 0 "#PWR0105" H 9800 4350 50  0001 C CNN
F 1 "GND" H 9805 4427 50  0000 C CNN
F 2 "" H 9800 4600 50  0001 C CNN
F 3 "" H 9800 4600 50  0001 C CNN
	1    9800 4600
	1    0    0    -1  
$EndComp
$Comp
L Device:R R13
U 1 1 5E2D04D7
P 2650 3550
F 0 "R13" V 2856 3550 50  0000 C CNN
F 1 "82" V 2765 3550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2580 3550 50  0001 C CNN
F 3 "~" H 2650 3550 50  0001 C CNN
	1    2650 3550
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R14
U 1 1 5E7EE68A
P 2650 4200
F 0 "R14" V 2856 4200 50  0000 C CNN
F 1 "82" V 2765 4200 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2580 4200 50  0001 C CNN
F 3 "~" H 2650 4200 50  0001 C CNN
	1    2650 4200
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R15
U 1 1 5E6B255C
P 7000 3500
F 0 "R15" H 6930 3455 50  0000 R CNN
F 1 "100" H 6930 3545 50  0000 R CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 6930 3500 50  0001 C CNN
F 3 "~" H 7000 3500 50  0001 C CNN
	1    7000 3500
	0    1    1    0   
$EndComp
$Comp
L Device:R R16
U 1 1 5E70FAD3
P 7000 5100
F 0 "R16" H 6930 5055 50  0000 R CNN
F 1 "100" H 6930 5145 50  0000 R CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 6930 5100 50  0001 C CNN
F 3 "~" H 7000 5100 50  0001 C CNN
	1    7000 5100
	0    1    1    0   
$EndComp
$Comp
L Device:R R17
U 1 1 5E2682B3
P 8250 3200
F 0 "R17" V 8456 3200 50  0000 C CNN
F 1 "2K2" V 8365 3200 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 8180 3200 50  0001 C CNN
F 3 "~" H 8250 3200 50  0001 C CNN
	1    8250 3200
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R18
U 1 1 5E268EC4
P 8250 4800
F 0 "R18" V 8456 4800 50  0000 C CNN
F 1 "2K2" V 8365 4800 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 8180 4800 50  0001 C CNN
F 3 "~" H 8250 4800 50  0001 C CNN
	1    8250 4800
	0    -1   -1   0   
$EndComp
$Comp
L Amplifier_Operational:LM4562 U4
U 3 1 5E262A9E
P 3300 1450
F 0 "U4" H 3200 2100 50  0000 C CNN
F 1 "LM4562" H 3200 1450 50  0000 C CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 3300 1450 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/lm4562.pdf" H 3300 1450 50  0001 C CNN
	3    3300 1450
	1    0    0    -1  
$EndComp
$Comp
L Device:C C20
U 1 1 5E418F5E
P 3550 1450
F 0 "C20" H 3665 1495 50  0000 L CNN
F 1 "100n" H 3665 1405 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 3588 1300 50  0001 C CNN
F 3 "~" H 3550 1450 50  0001 C CNN
	1    3550 1450
	1    0    0    -1  
$EndComp
$Comp
L Device:C C51
U 1 1 5ECD0BA5
P 4000 1450
F 0 "C51" H 4115 1495 50  0000 L CNN
F 1 "100n" H 4115 1405 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 4038 1300 50  0001 C CNN
F 3 "~" H 4000 1450 50  0001 C CNN
	1    4000 1450
	1    0    0    -1  
$EndComp
$Comp
L Device:C C21
U 1 1 5E72F21F
P 6150 3850
F 0 "C21" V 6401 3850 50  0000 C CNN
F 1 "22n" V 6310 3850 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 6188 3700 50  0001 C CNN
F 3 "~" H 6150 3850 50  0001 C CNN
	1    6150 3850
	-1   0    0    1   
$EndComp
$Comp
L Device:C C22
U 1 1 5E7357AF
P 6150 5450
F 0 "C22" V 6401 5450 50  0000 C CNN
F 1 "22n" V 6310 5450 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 6188 5300 50  0001 C CNN
F 3 "~" H 6150 5450 50  0001 C CNN
	1    6150 5450
	-1   0    0    1   
$EndComp
$Comp
L Device:C C23
U 1 1 5E72984C
P 8250 2750
F 0 "C23" V 8501 2750 50  0000 C CNN
F 1 "1n" V 8410 2750 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 8288 2600 50  0001 C CNN
F 3 "~" H 8250 2750 50  0001 C CNN
	1    8250 2750
	0    -1   -1   0   
$EndComp
$Comp
L Device:C C24
U 1 1 5E729FA5
P 8250 4400
F 0 "C24" V 8501 4400 50  0000 C CNN
F 1 "1n" V 8410 4400 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 8288 4250 50  0001 C CNN
F 3 "~" H 8250 4400 50  0001 C CNN
	1    8250 4400
	0    -1   -1   0   
$EndComp
$Comp
L Device:C C25
U 1 1 5E26B729
P 9150 3600
F 0 "C25" V 9401 3600 50  0000 C CNN
F 1 "1u" V 9310 3600 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 9188 3450 50  0001 C CNN
F 3 "~" H 9150 3600 50  0001 C CNN
	1    9150 3600
	0    -1   -1   0   
$EndComp
$Comp
L Device:C C26
U 1 1 5E38AC32
P 9150 5200
F 0 "C26" V 9401 5200 50  0000 C CNN
F 1 "1u" V 9310 5200 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 9188 5050 50  0001 C CNN
F 3 "~" H 9150 5200 50  0001 C CNN
	1    9150 5200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_01x03_Male J8
U 1 1 5EDBE7DA
P 8900 4300
F 0 "J8" H 9000 4600 50  0000 C CNN
F 1 "IQ TEST" H 9050 4500 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical" H 8900 4300 50  0001 C CNN
F 3 "~" H 8900 4300 50  0001 C CNN
	1    8900 4300
	1    0    0    -1  
$EndComp
$Comp
L Amplifier_Operational:LM4562 U4
U 2 1 5E26166E
P 8250 3600
F 0 "U4" H 8250 3966 50  0000 C CNN
F 1 "LM4562" H 8250 3875 50  0000 C CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 8250 3600 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/lm4562.pdf" H 8250 3600 50  0001 C CNN
	2    8250 3600
	1    0    0    1   
$EndComp
$Comp
L Amplifier_Operational:LM4562 U4
U 1 1 5E262689
P 8250 5200
F 0 "U4" H 8250 5400 50  0000 C CNN
F 1 "LM4562" H 8250 5500 50  0000 C CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 8250 5200 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/lm4562.pdf" H 8250 5200 50  0001 C CNN
	1    8250 5200
	1    0    0    1   
$EndComp
$Comp
L RADIO-rescue:cx2074NL-xcvr_components T1
U 1 1 5E6894D6
P 1800 4000
F 0 "T1" H 1800 4379 50  0000 C CNN
F 1 "BN43-2402" H 1800 4288 50  0000 C CNN
F 2 "openxcvr:bn43-2402-transformer" H 1800 4000 50  0001 C CNN
F 3 "https://datasheet.octopart.com/CX2074NL-Pulse-datasheet-123678.pdf" H 1800 4000 50  0001 C CNN
	1    1800 4000
	1    0    0    -1  
$EndComp
$Comp
L RADIO-rescue:FST5253-xcvr_components U5
U 1 1 5E2AF6E6
P 3600 4500
AR Path="/5E2AF6E6" Ref="U5"  Part="1" 
AR Path="/5E35BCF5/5E2AF6E6" Ref="U5"  Part="1" 
F 0 "U5" H 4000 5200 50  0000 C CNN
F 1 "FST3253" H 4000 5100 50  0000 C CNN
F 2 "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" H 3600 4500 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74cbt3253" H 3600 4500 50  0001 C CNN
	1    3600 4500
	1    0    0    -1  
$EndComp
$EndSCHEMATC
