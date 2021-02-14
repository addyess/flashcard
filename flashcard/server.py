import os
from bottle import Bottle, run, request, redirect, response
from bottle import jinja2_view as view
from bottle import TEMPLATE_PATH
from flashcard.logic import UX, Statistics, next_card, UserResponse

TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(__file__), 'views'))


class WebUX(UX):
    def __init__(self, args):
        super().__init__(args)
        self._app = Bottle()
        self._route()
        self._stats, self._all_cards = None, None
        self._reset(init=False)

    def _route(self):
        self._app.route('/', method='GET', callback=self._reset)
        self._app.route('/card', method='GET', callback=self._card)
        self._app.route('/stats', method='GET', callback=self._stat_page)
        self._app.route('/practice', method='GET', callback=self._practice)
        self._app.route('/update', method='POST', callback=self._update)

    def _reset(self, init=True):
        self._stats = Statistics()
        self._all_cards = next_card(self.args, self._stats)
        return redirect("/card") if init else None

    @view('practice.j2')
    def _practice(self):
        return dict(
            enumerate=enumerate,
            args=self.args
        )

    def _update(self):
        try:
            user_req = request.json
        except:
            response.status = 400
            return
        self.args.practice_data = user_req['practice_data']
        self.args.total = user_req['total']
        self.args.wait_time = user_req['wait_time']
        self.args.operators = user_req['operators']
        self.args.repeat = user_req['repeat']
        return {}

    @view('stats.j2')
    def _stat_page(self):
        return dict(
            duration=self._stats.duration,
            repeated=self._stats.repeated,
            hardest=self._stats.hardest
        )

    @view('card.j2')
    def _card(self):
        ans = request.query.get('ans')
        card_id = request.query.get('card_id')
        if ans is not None:
            try:
                user_resp = UserResponse(
                    card_id, int(ans) if ans.isdigit() else "timeout"
                )
                self._all_cards.send(user_resp)
            except TypeError:
                return redirect("/")
            except StopIteration:
                return redirect("/stats")
        card = next(self._all_cards, None)
        if not card:
            return redirect("/stats")
        return dict(
            card=card, args=self.args
        )

    def main(self):
        run(self._app, host='0.0.0.0', port=8080)
