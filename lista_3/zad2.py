import os
import random
import sys
import time
from collections import Counter


class Station:
    def __init__(self, wire_len, position, bits_to_send):
        self.wire_len = wire_len
        self.position = position
        self.bits_to_send = bits_to_send
        self.bits_sent = 0
        self.next_release_time = 0
        self.wire_clear = False
        self.clear_counter = W_LEN + position
        self.attempt = 0
        self.max_attempt = 128
        self.block = False

    def send_byte(self, current_time, delay=0.2):
        if (
            self.bits_sent < self.bits_to_send
            and current_time >= self.next_release_time
            and self.wire_clear == True
            and self.block == False
        ):
            direction = random.choice([-1, 1])
            self.bits_sent += 1
            self.next_release_time = current_time + delay
            sys.stderr.write(
                f"\nSTATION {self.position} SEND_BIT ({self.bits_sent}/{self.bits_to_send}) T={current_time:.2f}\n"
            )
            return self.position, direction
        return None, None

    def detect_collision(self, wire_positions):
        position_counter = Counter(wire_positions)
        for pos, count in position_counter.items():
            if count > 1:
                sys.stderr.write(
                    f"\nSTATION {self.position} COLLISION DETECTED @ {pos}\n"
                )
                # jam()
                if self.attempt > self.max_attempt:
                    self.block = True
                    sys.stderr.write(f"\nSTATION {self.position} TRANSMIT_FAIL")
                else:
                    self.clear_counter = random.randint(W_LEN//2, W_LEN)
                    sys.stderr.write(
                        f"\nSTATION {self.position} JAM_WAIT FOR {self.clear_counter}"
                    )
                    self.wire_clear = False
                    self.attempt += 1
                return True
        return False

    def listen(self, wire_positions):

        colided = self.detect_collision(wire_positions)
        if self.position in wire_positions:
            if not colided:
                self.clear_counter = W_LEN
                self.wire_clear = False
            sys.stderr.write(f"\nSTATION {self.position} WIRE NOT CLEAR\n")

        else:
            self.clear_counter = self.clear_counter - 1 if self.clear_counter > 0 else 0
            if self.clear_counter == 0:
                self.wire_clear = True


class Wire:
    def __init__(self, length, stations):
        self.length = length
        self.stations = stations
        self.station_pos = [station.position for station in stations]
        self.cable = [
            "-" if p not in self.station_pos else "|ST_{}|".format(p)
            for p in range(length)
        ]
        self.positions = []
        self.directions = []

    def print_cable(self):
        os.system("cls" if os.name == "nt" else "clear")
        sys.stdout.write("".join(self.cable) + "\n")
        sys.stdout.flush()

    def update_cable(self, old_positions, new_positions):
        for pos in old_positions:
            if (
                pos is not None
                and 0 <= pos < self.length
                and pos not in self.station_pos
            ):
                self.cable[pos] = "-"
        for pos in new_positions:
            if (
                pos is not None
                and 0 <= pos < self.length
                and pos not in self.station_pos
            ):
                self.cable[pos] = "*"
        self.print_cable()

    def simulate_traveling_bytes(self, fps=30):
        current_time = 0
        old_positions = [None] * len(self.positions)

        while any(
            pos is not None and 0 <= pos < self.length for pos in self.positions
        ) or any(station.bits_sent < station.bits_to_send for station in self.stations):
            for station in self.stations:
                station.listen(self.positions)

            for station in self.stations:
                pos, dir = station.send_byte(current_time)
                if pos is not None:
                    self.positions.append(pos)
                    self.directions.append(dir)

            self.update_cable(old_positions, self.positions)
            old_positions = self.positions[:]
            self.positions = [
                pos + dir for pos, dir in zip(self.positions, self.directions)
            ]

            time.sleep(1 / fps)
            current_time += 1 / fps

        self.update_cable(old_positions, [None] * len(old_positions))


W_LEN = 100
stations = [Station(W_LEN, 0, 32),Station(W_LEN,50,16), Station(W_LEN, 98, 32)]
wire = Wire(W_LEN, stations)
wire.simulate_traveling_bytes(fps=60)
