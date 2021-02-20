#!/bin/env python3

import random
from uuid import uuid4
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
UserResponse = namedtuple("UserResponse", "id, val")


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


class Card(namedtuple('Card', 'a, op, b, correct_ans, id')):
    def __new__(cls, a, op, b):
        py_op = {
            'x': '*',
            '/': '//',
        }
        _op = py_op.get(op) or op
        correct_ans = eval(f"{a} {_op} {b}")
        card_id = uuid4()
        self = super().__new__(cls, a, op, b, correct_ans, card_id)
        return self

    def __init__(self, *args):
        self.tries = 0
        self.correctly_answered = False

    def __str__(self):
        return f"{str(self.a)} {self.op} {str(self.b)}"

    def test(self, user_response):
        if user_response.id != str(self.id):
            return None
        self.tries += 1
        if not self.correctly_answered:
            self.correctly_answered = user_response.val == self.correct_ans
        return self.correctly_answered

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
    operators, tables = args.operators, args.tables
    _generated, extra = [], max(args.total - len(_practice), 0)
    if extra > 0:
        _generated = [
            card
            for op in operators
            for card in Card.from_table(tables, op)
        ]
        _generated = list(set(_ for _ in _generated if _ not in _practice))
        random.shuffle(_generated)
    _cards = _practice + _generated[:extra]
    random.shuffle(_cards)
    return _cards[:args.total]


def next_card(args, statistics):
    unsolved = cards(args)
    while unsolved:
        card, unsolved = unsolved[0], unsolved[1:]
        pre_timer = datetime.now()
        user_response = (yield card)
        total_time = datetime.now() - pre_timer
        correct = card.test(user_response)
        yield correct
        if correct is False:
            if args.repeat == 'end':
                unsolved += [card]
            elif args.repeat == "next":
                unsolved.insert(0, card)
        if correct is not None:
            statistics.record(card, total_time, user_response.val)


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
