#!/bin/env python3

import signal
import random
import threading
from itertools import takewhile
from datetime import datetime
from collections import namedtuple, defaultdict

GNOME_UX = False

"""
#################################
### Change these settings
#################################
"""
TOTAL_QUESTIONS = 50

TIMEOUT = "timeout"
Record = namedtuple('Record', 'time, correct, user_answer')


class Statistics:
    def __init__(self):
        self.card_stats = defaultdict(list)
        self.start = datetime.now()

    def record(self, card, time, user_answer):
        correct = user_answer == card.correct_ans
        self.card_stats[card].append(Record(time, correct, user_answer))

    @property
    def duration(self):
        return datetime.now() - self.start

    @property
    def repeated(self):
        longest = sorted(self.card_stats.items(), key=lambda elem: len(elem[1]), reverse=True)
        return takewhile(lambda elem: 1 < len(elem[1]) == len(longest[0][1]), longest)

    @property
    def hardest(self):
        longest = sorted((
            (c, rec)
            for c, recs in self.card_stats.items()
            for rec in recs
        ), key=lambda elem: elem[1], reverse=True)
        return longest


class Card(namedtuple('Card', 'a, op, b, correct_ans')):
    def __new__(cls, a, op, b):
        py_op = {
            'x': '*',
            '/': '//',
        }
        _op = py_op.get(op) or op
        correct_ans = eval(f"{a} {_op} {b}")
        self = super().__new__(cls, a, op, b, correct_ans)
        return self

    def __str__(self):
        return f"{str(self.a)} {self.op} {str(self.b)}"

    @classmethod
    def create(cls, a, b, op):
        if op in '+-x/':
            return cls(a, op, b)
        raise ArithmeticError("Invalid Operator")

    @classmethod
    def from_table(cls, tables, op):
        def eval_first(a, b):
            _op = '*' if op == '/' else '+'
            ans = eval(f"{a} {_op} {b}")
            try:
                return cls.create(ans, b, op)
            except ZeroDivisionError:
                return None

        if op in 'x+':
            return (
                cls.create(a, b, op)
                for a in range(0, max(tables) + 1)
                for b in tables
            )
        return filter(None, (
            eval_first(a, b)
            for a in range(0, max(tables) + 1)
            for b in tables
        ))


def cards(args):
    def parse(line):
        a, op, b = line.strip().split()
        return int(a), int(b), op

    _practice = []
    if args.practice_data:
        _practice = [
            Card.create(*parse(data))
            for data in args.practice_data
        ]
    operators = args.operators
    tables = args.tables
    _generated = [
        card
        for op in operators
        for card in Card.from_table(tables, op)
    ]
    _generated = list(set(_ for _ in _generated if _ not in _practice))
    random.shuffle(_generated)
    _cards = _practice + _generated[:args.total - len(_practice)]
    random.shuffle(_cards)
    return _cards[:args.total]


def next_card(args, statistics):
    unsolved = cards(args)
    while unsolved:
        card, unsolved = unsolved[0], unsolved[1:]
        pre_timer = datetime.now()
        user_ans = (yield card)
        total_time = datetime.now() - pre_timer
        correct = user_ans == card.correct_ans
        yield correct
        if not correct:
            if args.repeat == 'end':
                unsolved += [card]
            elif args.repeat == "next":
                unsolved.insert(0, card)
        statistics.record(card, total_time, user_ans)


def file_maker(arg):
    with open(arg) as f:
        return [
            line.strip()
            for line in f
            if not line.startswith("#")
        ]


def range_maker(arg):
    def split_hyphens(commas):
        for sep in commas:
            ranges = sep.split('-')
            if len(ranges) == 2:
                for i in range(*[int(s) for s in ranges]):
                    yield i
            elif len(ranges) == 1:
                yield int(ranges[0])
            else:
                raise TypeError(f"Invalid Range {sep}")
    return list(split_hyphens(arg.split(",")))


class UX:
    def __init__(self, args):
        self.args = args

    def __iter__(self):
        return self

    def main(self):
        stats = Statistics()
        all_cards = next_card(self.args, stats)
        out = next(self)
        for card in all_cards:
            ans = out.user_input_int(f"What's {card}? ")
            correct = all_cards.send(ans)
            out = next(self)
            if ans is TIMEOUT:
                out.print("Time's up, moving on")
            if not correct:
                out.print("It's ok, we'll see that again...")
        out = next(self)
        out.print("=====       Statistics          =====")
        out.print("=====================================")
        out.print(f"Finished in {stats.duration} seconds")
        for card, stat in stats.repeated:
            out.print(f"Repeated '{card}' {len(stat)} times")
        for card, stat in stats.hardest:
            out.print(f"Problem  '{card}' took {stat.time} seconds")


class GnomeUX(UX):
    def __init__(self, args):
        super().__init__(args)
        self.output = None
        self.input = None
        self.setup()

    def main(self):
        thread = threading.Thread(target=super().main)
        thread.daemon = True
        thread.start()
        Gtk.main()

    def setup(self):
        import Gtk
        window = Gtk.Window(title="Flash Cards")
        window.set_border_width(50)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        window.add(vbox)

        self.output = Gtk.Label(label="Let's Begin")
        vbox.pack_start(self.output, True, True, 0)

        self.input = Gtk.Entry()
        self.input.set_text("")
        vbox.pack_start(self.input, True, True, 0)

        window.show()
        window.connect("destroy", Gtk.main_quit)
        window.show_all()

    def __next__(self):
        self.output.set_text('')
        self.input.set_text('')
        return self

    def print(self, new=None):
        old = self.output.get_text()
        self.output.set_text('\n'.join(filter(None, [old, new])))

    def user_input_int(self, prompt):
        def pending(entry):
            event.value = entry.get_text()
            event.set()

        valid = None
        while not valid:
            if valid is False:
                self.print("Sorry, that's not a valid integer")
            self.print(prompt)
            event = threading.Event()
            handle_id = self.input.connect('activate', pending)
            ok = event.wait(self.args.wait_time if self.args.wait_time > 0 else None)
            try:
                if not ok:
                    return TIMEOUT
                return int(event.value)
            except ValueError:
                valid = False
            finally:
                self.input.disconnect(handle_id)


class CliUX(UX):
    def __next__(self):
        self.print("=================yay====================")
        return self

    @property
    def print(self):
        return print

    def user_input_int(self, prompt):
        def raised(_signal, _timeout):
            self.print()
            raise TimeoutError()

        valid = None
        while not valid:
            if valid is False:
                self.print("Sorry, that's not a valid integer..")
            signal.signal(signal.SIGALRM, raised)
            try:
                if self.args.wait_time > 0:
                    signal.alarm(self.args.wait_time)
                return int(input(prompt))
            except TimeoutError:
                return TIMEOUT
            except ValueError:
                valid = False
            finally:
                signal.alarm(0)
