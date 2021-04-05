#!/usr/bin/env python3

# python modules
import sys
import time
import subprocess
from multiprocessing import Process, Queue
import atexit
import argparse
import logging

# numpy etc
import numpy as np
import matplotlib.pyplot as plt

# open xcvr modules
import openxcvr
from cat_server import cat_server, command_queue, request_queue, response_queue

# A table of the playback sample rates for each mode
sample_rate_for_modes = {
    "AM": 12207,
    "LSB": 6103,
    "USB": 6103,
    "FM": 24414,
    "NFM": 24414,
    "CW": 8138,
}


def convert_16to8(data):
    data = np.frombuffer(data, dtype="int16") / 256
    return data.astype("int8")


def terminate_process(p):
    """Quit process nicely at first, then forcefully"""

    # try to quit cleanly
    p.terminate()
    try:
        outs, errs = p.communicate(timeout=1)
        logging.info("process exited %s %s", outs, errs)
    except subprocess.TimeoutExpired:
        # if that doesn't work quite by force
        p.kill()
        outs, errs = p.communicate()
        logging.info("process killed %s %s", outs, errs)


class Transceiver:
    def __init__(self, port, mode, frequency, squelch, agc, server_host, server_port):

        xcvr = openxcvr.Xcvr(port)
        self.xcvr = xcvr

        # keep local copies of settings so we know where we are
        if mode is None:
            xcvr.request_mode()
            self.mode = xcvr.get_mode()
        else:
            self.mode = mode

        if frequency is None:
            xcvr.request_frequency()
            self.frequency = xcvr.get_frequency()
        else:
            self.frequency = frequency

        self.squelch = squelch
        self.agc = agc
        self.tx_rx = 0

        # create an xcvr instance to communicate with the hardware
        xcvr.set_frequency(self.frequency)
        xcvr.set_mode(self.mode)
        xcvr.set_squelch(squelch)
        xcvr.set_AGC(agc)
        xcvr.set_volume(0)

        # start a tcp server listening for cat commands
        self.command_queue = command_queue
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.cp = Process(
            target=cat_server, args=(frequency, mode, server_host, server_port)
        )
        self.cp.start()


    def receive(self):

        """Read audio a block at a time from the receiver and send to the sound card

        Whenever there is a command that needs to be processed, quit transmitting and
        process it.
        """

        logging.info("transceiver: start receiving")
        # request extra packet at start so there is always one ready
        self.xcvr.request_audio_output()
        while 1:


            if not self.command_queue.empty():
                break

            request = None
            if not self.request_queue.empty():
                request = self.request_queue.get()
                if request == "frequency" : 
                    self.xcvr.request_frequency()
                elif request == "mode" : 
                    self.xcvr.request_mode()
                elif request == "tx" : 
                    self.xcvr.request_TX()
            self.xcvr.request_audio_output()
            data = self.xcvr.get_audio()
            self.player.stdin.write(data)

            if request is not None:
                if request == "frequency" : 
                    self.frequency = self.xcvr.get_frequency()
                    self.response_queue.put(self.frequency)
                elif request == "mode" : 
                    mode = self.xcvr.get_mode()
                    self.response_queue.put(mode)
                    if mode != self.mode:
                        self.mode = mode
                        break
                elif request == "tx" : 
                    tx_rx = self.xcvr.get_TX()
                    self.response_queue.put(tx_rx)
                    if tx_rx != self.tx_rx:
                        self.tx_rx = tx_rx
                        break

        # when complete, play the extra packet
        data = self.xcvr.get_audio()  # process extra request once finished
        self.player.stdin.write(data)
        logging.info("transceiver: stop receiving")

    def transmit(self):

        """Read audio a block at a time from the soundcard and send to the transmitter

        Whenever there is a command that needs to be processed, quit transmitting and
        process it.
        """

        logging.info("transceiver: start transmitting")
        self.recorder = subprocess.Popen(
            ["arecord", "-t", "raw", "--format=S16_LE", "--rate=50000"],
            stdout=subprocess.PIPE,
        )
        self.xcvr.set_USB_audio(1)
        self.xcvr.set_TX(1)

        # send an extra block of data to prevent pipeline emptying
        data = convert_16to8(
            self.recorder.stdout.read(2048)
        )  # 2048bytes = 1024 samples
        self.xcvr.put_audio(data.tobytes())  # 1024 samples

        t0 = time.time()
        samples_sent = 0
        while 1:

            if not self.command_queue.empty():
                break

            request = None
            if not self.request_queue.empty():
                request = self.request_queue.get()
                if request == "frequency" : 
                    self.xcvr.request_frequency()
                elif request == "mode" : 
                    self.xcvr.request_mode()
                elif request == "tx" : 
                    self.xcvr.request_TX()

            # send a block
            data = convert_16to8(self.recorder.stdout.read(2048))

            samples_sent += len(data)
            elapsed = time.time() - t0
            logging.debug(samples_sent / elapsed)

            self.xcvr.put_audio(data.tobytes())
            self.xcvr.wait_audio_in_ack()

            if request is not None:
                if request == "frequency" : 
                    self.frequency = self.xcvr.get_frequency()
                    self.response_queue.put(self.frequency)
                elif request == "mode" : 
                    mode = self.xcvr.get_mode()
                    self.response_queue.put(mode)
                    if mode != self.mode:
                        self.mode = mode
                        break
                elif request == "tx" : 
                    tx_rx = self.xcvr.get_TX()
                    self.response_queue.put(tx_rx)
                    if tx_rx != self.tx_rx:
                        self.tx_rx = tx_rx
                        break

        self.xcvr.wait_audio_in_ack()
        self.xcvr.set_USB_audio(0)
        self.xcvr.set_TX(0)
        terminate_process(self.recorder)
        logging.info("transceiver: stop transmitting")

    def process_commands(self):

        """Sit in a loop processing commands from the cat server.

        Whenever we aren't receiving commands, we are either transmitting or receiving
        """

        # start out in receive mode
        self.player = subprocess.Popen(
            [
                "aplay",
                "-t",
                "raw",
                "--format=S16_LE",
                "--rate=%u" % sample_rate_for_modes[self.mode],
            ],
            stdin=subprocess.PIPE,
        )
        self.receive()
        # self.transmit()

        while 1:
            while not self.command_queue.empty():
                # pull command from command stream
                command, value = self.command_queue.get()

                if command == "frequency":
                    logging.info("transceiver: executing frequency command")
                    self.frequency = value
                    self.xcvr.set_frequency(self.frequency)
                elif command == "mode":
                    logging.info("transceiver: executing mode command")
                    terminate_process(self.player)
                    self.mode = value
                    self.xcvr.set_mode(self.mode)
                    self.player = subprocess.Popen(
                        [
                            "aplay",
                            "-t",
                            "raw",
                            "--format=S16_LE",
                            "--rate=%u" % sample_rate_for_modes[self.mode],
                        ],
                        stdin=subprocess.PIPE,
                    )
                elif command == "tx":
                    logging.info("transceiver: executing tx_rx command")
                    self.tx_rx = int(value)
                else:
                    assert False

            if self.tx_rx:
                self.transmit()
            else:
                self.receive()

    def __del__(self):

        """Run clean-up of child processes"""

        logging.info("transceiver: running clean-up")

        if hasattr(self, "cp"):
            self.cp.terminate()
        if hasattr(self, "player"):
            terminate_process(self.player)
        if hasattr(self, "recorder"):
            terminate_process(self.recorder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenXCVR command line transceiver")
    parser.add_argument(
        "-p",
        "--port",
        default="/dev/ttyUSB0",
        help="USB serial port to connect to OpenXCVR hardware",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=openxcvr.modes.keys(),
        help="Mode (AM, FM, NFM, USB, LSB, CW)",
    )
    parser.add_argument(
        "-f", "--frequency", type=float, help="frequency (Hz)"
    )
    parser.add_argument(
        "-s",
        "--squelch",
        default=0,
        type=int,
        choices=range(13),
        help="squelch (0=s0, 9=s9, 10=s9+10dB, 11=s9+20dB, 12=s9+30dB)",
    )
    parser.add_argument(
        "-a",
        "--agc",
        default="VERY_SLOW",
        choices=openxcvr.agc_speeds.keys(),
        help="AGC speed (very slow, slow, normal, fast)",
    )
    parser.add_argument(
        "-lp",
        "--server_host",
        default="0.0.0.0",
        help="port to bind rigtld compatible server",
    )
    parser.add_argument(
        "-lh",
        "--server_port",
        default=4532,
        type=int,
        help="IP address to bind rigctld compatible server",
    )
    args = parser.parse_args()
    print(args)

    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    trx = Transceiver(
        args.port,
        args.mode,
        args.frequency,
        args.squelch,
        args.agc,
        args.server_host,
        args.server_port,
    )
    trx.process_commands()
