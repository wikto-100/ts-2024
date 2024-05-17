import random
import sys
import time
from collections import Counter


class Station:
    def __init__(self, name, wire_len, position, bits_to_send):
        self.wire_len = wire_len
        self.position = position
        self.bits_to_send = bits_to_send
        self.bits_sent = 0
        self.wire_clear = False
        self.clear_counter = W_LEN + position
        self.attempt = 0
        self.max_attempt = 10
        self.last_collision_prox = None
        self.block = False
        self.name = name

    def send_byte(self):
        if self.bits_sent < self.bits_to_send and self.wire_clear and not self.block:
            direction = random.choice([-1, 1])
            self.bits_sent += 1

            return self.position, direction, self.name
        return None, None, None

    def print_where(self, pos):
        space = "".join(" " for _ in range(self.wire_len))
        start = min(self.position, pos)
        end = max(self.position, pos)
        where = space[:start] + "_" * (end - start) + space[end:]
        where = where[:pos] + "**" + where[pos + 1:]
        where = where[:self.position] + "|^" + where[self.position + 1:]

        print(where)
        print(f"\nSTATION {self.name} @ POSITION {self.position} COLLISION DETECTED @ {pos}\n")

    def detect_collision(self, wire_positions):
        position_counter = Counter(wire_positions)
        for pos, count in position_counter.items():
            if count > 1:
                # where = "".join("_" for _ in range(pos)) + "**"
                self.print_where(pos)
                self.last_collision_prox = abs(pos - self.position)
                # jam()
                if self.attempt > self.max_attempt:
                    self.block = True
                else:
                    self.clear_counter = random.randint(W_LEN // 2, W_LEN)
                    sys.stdout.write(
                        f"\nSTATION {self.position} JAM_WAIT FOR {self.clear_counter}\n"
                    )
                    self.wire_clear = False
                    self.attempt += 1
                    input("Press Enter to continue...")

                return True
        return False

    def listen(self, wire_positions):

        colided = self.detect_collision(wire_positions)
        if self.position in wire_positions:
            if not colided:
                self.clear_counter = W_LEN
                self.wire_clear = False

        else:
            self.clear_counter = max(0, self.clear_counter - 1)
            if self.clear_counter == 0:
                self.wire_clear = True


class Wire:
    def __init__(self, length, stations):
        self.length = length
        self.stations = stations
        self.station_pos = [station.position for station in stations]
        self.cable = ["=" for _ in range(length)] + ["\n"]
        i = 0
        for s in self.stations:
            st_str = f"ST_{s.name}"
            for _ in range(self.station_pos[max(0,i-1)],max(0,self.station_pos[i] - len(st_str) - 1)):
                self.cable.append(" ")
            self.cable.append(st_str)
            i+=1

        self.positions = []
        self.directions = []
        self.ownership = []

    def print_cable(self):
        sys.stdout.write("".join(self.cable) + "\n")
        sys.stdout.flush()

    def update_cable(self, old_positions, new_positions):
        for pos in old_positions:
            if pos is not None and 0 <= pos < self.length:
                self.cable[pos] = "="
        for pos in new_positions:
            if pos is not None and 0 <= pos < self.length:
                self.cable[pos] = self.ownership[self.positions.index(pos)]
        self.print_cable()

    def simulate_traveling_bytes(self, fps=30):
        old_positions = [None] * len(self.positions)
        f_interval = round(1 / fps, 2)

        while any(
            pos is not None and 0 <= pos < self.length for pos in self.positions
        ) or any(station.bits_sent < station.bits_to_send for station in self.stations):
            self.stations.sort(key=lambda s: (s.last_collision_prox is None, s.last_collision_prox))
            for station in self.stations:
                station.listen(self.positions)

            for station in self.stations:
                pos, dir, st = station.send_byte()
                if pos is not None:
                    self.positions.append(pos)
                    self.directions.append(dir)
                    self.ownership.append(st)

            old_positions = self.positions[:]
            self.update_cable(old_positions, self.positions)
            self.positions = [
                pos + dir for pos, dir in zip(self.positions, self.directions)
            ]

            time.sleep(f_interval)

            if all(station.block for station in self.stations):
                return

        self.update_cable(old_positions, [None] * len(old_positions))


W_LEN = 100
stations = [
    Station("A", W_LEN, 0, 32),
    Station("B", W_LEN, 50, 16),
    Station("C", W_LEN, 90, 32),
]
wire = Wire(W_LEN, stations)
wire.simulate_traveling_bytes(fps=30)
sys.stdout.write(f"TOTAL COLLISIONS: {stations[0].attempt}\t")
sys.stdout.flush()
blocked = sum(1 for station in stations if station.block)
sys.stdout.write(f"STATIONS BLOCKED: {blocked}")

sys.stdout.flush()
