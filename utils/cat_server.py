#!/usr/bin/env python3

import socket
import logging
from multiprocessing import Process, Queue

dump2 = """ 0
2
2
150000.000000 30000000.000000  0x900af -1 -1 0x10 000003 0x3
0 0 0 0 0 0 0
150000.000000 30000000.000000  0x900af -1 -1 0x10 000003 0x3
0 0 0 0 0 0 0
0 0
0 0
0
0
0
0


0x0
0x0
0x0
0x0
0x0
0
"""



command_queue = Queue() #use a queue to send updates to the radio hardware
def cat_server(frequency, mode, host="0.0.0.0", port=4532):

    VFO = "VFOA"
    tx = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        thefile = s.makefile("rwb", buffering=0)
        logging.info("cat_server: listening on %s:%s", host, port) 

        while 1:
            conn, addr = s.accept()
            with conn:
                logging.info("cat_server: connected by %s", addr) 

                while True:
                    command = conn.recv(1024).decode("utf8")

                    if "dump_state" in command:
                        conn.send(dump2.encode("utf8"))

                    #get commands
                    elif command.startswith("s") or command.startswith("get_split_vfo"):
                        conn.send("0\n".encode("utf8"))
                        conn.send(("%s\n"%VFO).encode("utf8"))
                    elif command.startswith("v") or command.startswith("get_vfo"):
                        conn.send(("%s\n"%VFO).encode("utf8"))
                    elif command.startswith("f") or command.startswith("get_freq"):
                        conn.send(("%s\n"%frequency).encode("utf8"))
                    elif command.startswith("m") or command.startswith("get_mode"):
                        conn.send(("%s\n"%mode).encode("utf8"))
                        conn.send("0\n".encode("utf8"))
                    elif command.startswith("t") or command.startswith("get_ptt"):
                        conn.send(("%s\n"%tx).encode("utf8"))

                    #set commands
                    elif command.startswith("S") or command.startswith("set_split_vfo"):
                        conn.send("RPRT 0\n".encode("utf8"))
                    elif command.startswith("F") or command.startswith("set_freq"):
                        frequency = round(float(command.split()[1]))
                        logging.info("cat_server: sending frequency") 
                        command_queue.put(("frequency", frequency))
                        conn.send("RPRT 0\n".encode("utf8"))
                    elif command.startswith("V") or command.startswith("set_vfo"):
                        VFO = command.split()[1]
                        conn.send("RPRT 0\n".encode("utf8"))
                    elif command.startswith("M") or command.startswith("set_mode"):
                        mode = command.split()[1]
                        logging.info("cat_server: sending mode") 
                        conn.send("RPRT 0\n".encode("utf8"))
                        command_queue.put(("mode", mode))
                    elif command.startswith("T") or command.startswith("set_ptt"):
                        tx = command.split()[1]
                        logging.info("cat_server: sending tx_rx") 
                        command_queue.put(("tx", tx))
                        conn.send("RPRT 0\n".encode("utf8"))

                    elif command.startswith("q"):
                        conn.close()
                        break

                logging.info("cat_server: disconnected") 
