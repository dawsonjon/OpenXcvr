EESchema Schematic File Version 5
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 7
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
Connection ~ 3550 3150
Connection ~ 4050 6150
Connection ~ 4300 4250
Connection ~ 4750 3150
Connection ~ 4750 4250
Connection ~ 4900 6150
NoConn ~ 5050 3650
Wire Wire Line
	3100 3350 3100 3850
Wire Wire Line
	3350 2650 3350 3450
Wire Wire Line
	3550 3150 3550 2650
Wire Wire Line
	3550 3150 3850 3150
Wire Wire Line
	3550 3250 3550 3150
Wire Wire Line
	3900 6150 4050 6150
Wire Wire Line
	3900 6450 3900 6550
Wire Wire Line
	3950 4250 4300 4250
Wire Wire Line
	3950 4550 3950 4650
Wire Wire Line
	4050 6000 4050 6150
Wire Wire Line
	4050 6150 4250 6150
Wire Wire Line
	4150 3150 4750 3150
Wire Wire Line
	4250 6450 4250 6550
Wire Wire Line
	4300 3050 5050 3050
Wire Wire Line
	4300 4250 4300 3050
Wire Wire Line
	4300 4550 4300 4650
Wire Wire Line
	4700 2800 2700 2800
Wire Wire Line
	4700 2950 4700 2800
Wire Wire Line
	4750 2700 2700 2700
Wire Wire Line
	4750 2850 4750 2700
Wire Wire Line
	4750 3150 4750 4250
Wire Wire Line
	4750 4250 5100 4250
Wire Wire Line
	4750 4550 4750 4650
Wire Wire Line
	4750 6150 4900 6150
Wire Wire Line
	4750 6450 4750 6550
Wire Wire Line
	4850 3550 4850 3950
Wire Wire Line
	4850 3550 5050 3550
Wire Wire Line
	4850 3950 9150 3950
Wire Wire Line
	4900 6000 4900 6150
Wire Wire Line
	4900 6150 5100 6150
Wire Wire Line
	4950 3750 4950 3850
Wire Wire Line
	4950 3850 7150 3850
Wire Wire Line
	5050 2850 4750 2850
Wire Wire Line
	5050 2950 4700 2950
Wire Wire Line
	5050 3150 4750 3150
Wire Wire Line
	5050 3250 3550 3250
Wire Wire Line
	5050 3350 3100 3350
Wire Wire Line
	5050 3450 3350 3450
Wire Wire Line
	5050 3750 4950 3750
Wire Wire Line
	5100 4550 5100 4650
Wire Wire Line
	5100 6450 5100 6550
Wire Wire Line
	6300 2850 7500 2850
Wire Wire Line
	6300 2950 7950 2950
Wire Wire Line
	6300 3050 8250 3050
Wire Wire Line
	6300 3150 8550 3150
Wire Wire Line
	6300 3250 8850 3250
Wire Wire Line
	6300 3350 7150 3350
Wire Wire Line
	6300 3450 6700 3450
Wire Wire Line
	6300 3650 7150 3650
Wire Wire Line
	6300 3750 7150 3750
Wire Wire Line
	6700 3450 6700 2650
Wire Wire Line
	6700 3550 6300 3550
Wire Wire Line
	6700 3550 6700 4000
Wire Wire Line
	7500 2850 7500 2300
Wire Wire Line
	7950 2950 7950 2300
Wire Wire Line
	8250 3050 8250 2300
Wire Wire Line
	8550 3150 8550 2300
Wire Wire Line
	8850 3250 8850 2300
Wire Wire Line
	9150 3950 9150 2300
Text Notes 7650 2050 2    50   ~ 0
MODE1\n
Text Notes 8100 2050 2    50   ~ 0
MODE0\n
Text Notes 8350 2050 2    50   ~ 0
FMT1\n
Text Notes 8650 2050 2    50   ~ 0
FMT0\n
Text Notes 8900 2050 2    50   ~ 0
OSR\n
Text Notes 9250 2050 2    50   ~ 0
BYPAS\n
Text GLabel 2700 2700 0    50   Input ~ 0
RX_I
Text GLabel 2700 2800 0    50   Input ~ 0
RX_Q
Text GLabel 7150 3350 2    50   Input ~ 0
SCK
Text GLabel 7150 3650 2    50   Output ~ 0
DOUT
Text GLabel 7150 3750 2    50   Output ~ 0
BCK
Text GLabel 7150 3850 2    50   Output ~ 0
LRCK
$Comp
L power:+3V3 #PWR02
U 1 1 5E38F1B7
P 3350 2650
F 0 "#PWR02" H 3350 2500 50  0001 C CNN
F 1 "+3V3" H 3365 2823 50  0000 C CNN
F 2 "" H 3350 2650 50  0001 C CNN
F 3 "" H 3350 2650 50  0001 C CNN
	1    3350 2650
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR05
U 1 1 5E38C061
P 3550 2650
F 0 "#PWR05" H 3550 2500 50  0001 C CNN
F 1 "+5V" H 3565 2823 50  0000 C CNN
F 2 "" H 3550 2650 50  0001 C CNN
F 3 "" H 3550 2650 50  0001 C CNN
	1    3550 2650
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR06
U 1 1 5E38CACB
P 4050 6000
F 0 "#PWR06" H 4050 5850 50  0001 C CNN
F 1 "+3V3" H 4065 6173 50  0000 C CNN
F 2 "" H 4050 6000 50  0001 C CNN
F 3 "" H 4050 6000 50  0001 C CNN
	1    4050 6000
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR011
U 1 1 5E4393DB
P 4900 6000
F 0 "#PWR011" H 4900 5850 50  0001 C CNN
F 1 "+5V" H 4915 6173 50  0000 C CNN
F 2 "" H 4900 6000 50  0001 C CNN
F 3 "" H 4900 6000 50  0001 C CNN
	1    4900 6000
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR014
U 1 1 5E414A55
P 6700 2650
F 0 "#PWR014" H 6700 2500 50  0001 C CNN
F 1 "+3V3" H 6715 2823 50  0000 C CNN
F 2 "" H 6700 2650 50  0001 C CNN
F 3 "" H 6700 2650 50  0001 C CNN
	1    6700 2650
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR016
U 1 1 5E3B0E61
P 7500 2300
F 0 "#PWR016" H 7500 2150 50  0001 C CNN
F 1 "+3V3" H 7515 2473 50  0000 C CNN
F 2 "" H 7500 2300 50  0001 C CNN
F 3 "" H 7500 2300 50  0001 C CNN
	1    7500 2300
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR017
U 1 1 5E3B129D
P 7950 2300
F 0 "#PWR017" H 7950 2150 50  0001 C CNN
F 1 "+3V3" H 7965 2473 50  0000 C CNN
F 2 "" H 7950 2300 50  0001 C CNN
F 3 "" H 7950 2300 50  0001 C CNN
	1    7950 2300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR01
U 1 1 5E38B1EC
P 3100 3850
F 0 "#PWR01" H 3100 3600 50  0001 C CNN
F 1 "GND" H 3105 3677 50  0000 C CNN
F 2 "" H 3100 3850 50  0001 C CNN
F 3 "" H 3100 3850 50  0001 C CNN
	1    3100 3850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR03
U 1 1 5E3EBF7E
P 3900 6550
F 0 "#PWR03" H 3900 6300 50  0001 C CNN
F 1 "GND" H 3905 6377 50  0000 C CNN
F 2 "" H 3900 6550 50  0001 C CNN
F 3 "" H 3900 6550 50  0001 C CNN
	1    3900 6550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR04
U 1 1 5E3E42CA
P 3950 4650
F 0 "#PWR04" H 3950 4400 50  0001 C CNN
F 1 "GND" H 3955 4477 50  0000 C CNN
F 2 "" H 3950 4650 50  0001 C CNN
F 3 "" H 3950 4650 50  0001 C CNN
	1    3950 4650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR07
U 1 1 5E3EBFB7
P 4250 6550
F 0 "#PWR07" H 4250 6300 50  0001 C CNN
F 1 "GND" H 4255 6377 50  0000 C CNN
F 2 "" H 4250 6550 50  0001 C CNN
F 3 "" H 4250 6550 50  0001 C CNN
	1    4250 6550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR08
U 1 1 5E3E48F2
P 4300 4650
F 0 "#PWR08" H 4300 4400 50  0001 C CNN
F 1 "GND" H 4305 4477 50  0000 C CNN
F 2 "" H 4300 4650 50  0001 C CNN
F 3 "" H 4300 4650 50  0001 C CNN
	1    4300 4650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR09
U 1 1 5E3E4F1A
P 4750 4650
F 0 "#PWR09" H 4750 4400 50  0001 C CNN
F 1 "GND" H 4755 4477 50  0000 C CNN
F 2 "" H 4750 4650 50  0001 C CNN
F 3 "" H 4750 4650 50  0001 C CNN
	1    4750 4650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR010
U 1 1 5E418F46
P 4750 6550
F 0 "#PWR010" H 4750 6300 50  0001 C CNN
F 1 "GND" H 4755 6377 50  0000 C CNN
F 2 "" H 4750 6550 50  0001 C CNN
F 3 "" H 4750 6550 50  0001 C CNN
	1    4750 6550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR012
U 1 1 5E3E554C
P 5100 4650
F 0 "#PWR012" H 5100 4400 50  0001 C CNN
F 1 "GND" H 5105 4477 50  0000 C CNN
F 2 "" H 5100 4650 50  0001 C CNN
F 3 "" H 5100 4650 50  0001 C CNN
	1    5100 4650
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR013
U 1 1 5E4393DD
P 5100 6550
F 0 "#PWR013" H 5100 6300 50  0001 C CNN
F 1 "GND" H 5105 6377 50  0000 C CNN
F 2 "" H 5100 6550 50  0001 C CNN
F 3 "" H 5100 6550 50  0001 C CNN
	1    5100 6550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR015
U 1 1 5E38BC26
P 6700 4000
F 0 "#PWR015" H 6700 3750 50  0001 C CNN
F 1 "GND" H 6705 3827 50  0000 C CNN
F 2 "" H 6700 4000 50  0001 C CNN
F 3 "" H 6700 4000 50  0001 C CNN
	1    6700 4000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR018
U 1 1 5E3AF216
P 8250 2300
F 0 "#PWR018" H 8250 2050 50  0001 C CNN
F 1 "GND" H 8255 2127 50  0000 C CNN
F 2 "" H 8250 2300 50  0001 C CNN
F 3 "" H 8250 2300 50  0001 C CNN
	1    8250 2300
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR019
U 1 1 5E3AF827
P 8550 2300
F 0 "#PWR019" H 8550 2050 50  0001 C CNN
F 1 "GND" H 8555 2127 50  0000 C CNN
F 2 "" H 8550 2300 50  0001 C CNN
F 3 "" H 8550 2300 50  0001 C CNN
	1    8550 2300
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR020
U 1 1 5E3AFCD6
P 8850 2300
F 0 "#PWR020" H 8850 2050 50  0001 C CNN
F 1 "GND" H 8855 2127 50  0000 C CNN
F 2 "" H 8850 2300 50  0001 C CNN
F 3 "" H 8850 2300 50  0001 C CNN
	1    8850 2300
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR021
U 1 1 5E3B0106
P 9150 2300
F 0 "#PWR021" H 9150 2050 50  0001 C CNN
F 1 "GND" H 9155 2127 50  0000 C CNN
F 2 "" H 9150 2300 50  0001 C CNN
F 3 "" H 9150 2300 50  0001 C CNN
	1    9150 2300
	-1   0    0    1   
$EndComp
$Comp
L Device:R R1
U 1 1 5E61E083
P 4000 3150
F 0 "R1" V 4206 3150 50  0000 C CNN
F 1 "1K" V 4115 3150 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 3930 3150 50  0001 C CNN
F 3 "~" H 4000 3150 50  0001 C CNN
	1    4000 3150
	0    -1   -1   0   
$EndComp
$Comp
L Device:C C3
U 1 1 5E3EBF95
P 4250 6300
F 0 "C3" H 4365 6345 50  0000 L CNN
F 1 "100n" H 4365 6255 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 4288 6150 50  0001 C CNN
F 3 "~" H 4250 6300 50  0001 C CNN
	1    4250 6300
	1    0    0    -1  
$EndComp
$Comp
L Device:C C4
U 1 1 5E3DA67E
P 4300 4400
F 0 "C4" H 4415 4445 50  0000 L CNN
F 1 "100n" H 4415 4355 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 4338 4250 50  0001 C CNN
F 3 "~" H 4300 4400 50  0001 C CNN
	1    4300 4400
	1    0    0    -1  
$EndComp
$Comp
L Device:C C7
U 1 1 5E3DAF89
P 5100 4400
F 0 "C7" H 5215 4445 50  0000 L CNN
F 1 "100n" H 5215 4355 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 5138 4250 50  0001 C CNN
F 3 "~" H 5100 4400 50  0001 C CNN
	1    5100 4400
	1    0    0    -1  
$EndComp
$Comp
L Device:C C8
U 1 1 5E4393DC
P 5100 6300
F 0 "C8" H 5215 6345 50  0000 L CNN
F 1 "100n" H 5215 6255 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 5138 6150 50  0001 C CNN
F 3 "~" H 5100 6300 50  0001 C CNN
	1    5100 6300
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C1
U 1 1 5E3EBF59
P 3900 6300
F 0 "C1" H 4018 6345 50  0000 L CNN
F 1 "10u" H 4018 6255 50  0000 L CNN
F 2 "Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A" H 3938 6150 50  0001 C CNN
F 3 "~" H 3900 6300 50  0001 C CNN
	1    3900 6300
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C2
U 1 1 5E3DC2D0
P 3950 4400
F 0 "C2" H 4068 4445 50  0000 L CNN
F 1 "10u" H 4068 4355 50  0000 L CNN
F 2 "Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A" H 3988 4250 50  0001 C CNN
F 3 "~" H 3950 4400 50  0001 C CNN
	1    3950 4400
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C5
U 1 1 5E3DBC11
P 4750 4400
F 0 "C5" H 4868 4445 50  0000 L CNN
F 1 "10u" H 4868 4355 50  0000 L CNN
F 2 "Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A" H 4788 4250 50  0001 C CNN
F 3 "~" H 4750 4400 50  0001 C CNN
	1    4750 4400
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C6
U 1 1 5E418F95
P 4750 6300
F 0 "C6" H 4868 6345 50  0000 L CNN
F 1 "10u" H 4868 6255 50  0000 L CNN
F 2 "Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A" H 4788 6150 50  0001 C CNN
F 3 "~" H 4750 6300 50  0001 C CNN
	1    4750 6300
	1    0    0    -1  
$EndComp
$Comp
L RADIO-rescue:PCM1802-xcvr_components U1
U 1 1 5E385964
P 5750 3300
F 0 "U1" H 5675 4014 50  0000 C CNN
F 1 "PCM1802" H 5675 3923 50  0000 C CNN
F 2 "openxcvr:SSOP-20_5.3x7.2mm_P0.65mm" H 5650 3300 50  0001 C CNN
F 3 "" H 5300 3300 50  0001 C CNN
	1    5750 3300
	1    0    0    -1  
$EndComp
$EndSCHEMATC
