# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

import json

from aqt import gui_hooks, mw
from aqt.deckoptions import DeckOptionsDialog
from aqt.qt import QTimer

ROMee_State = False
AFFECTS_FILTERED_DECKS = False

BT_JS = """
maxTime=%d
time=0
btn=document.querySelectorAll('table table button');
for(i=0;i<btn.length;i++){
 btn[i].disabled=true;
 btn[i].setAttribute('style','visibility:hidden');
}
window.setTimeout(function(){
 for(i=0;i<btn.length;i++){
  btn[i].disabled=false;
  btn[i].setAttribute('style','');
 }
},maxTime*1000);
"""

DECKOPTIONS_HTML = """
<div style="margin-bottom:12px;color:#555;font-size:13px;line-height:1.4">
  <strong>Too fast?</strong> If you reveal the answer in less than the
  <em>minimum</em> time, you're likely reflex grading — the pause forces
  you to slow down.<br>
  <strong>Too slow?</strong> If you spend longer than the
  <em>maximum</em> time, the pause gives you a moment to absorb the answer.<br>
  Set both to 0 to disable.
</div>
<div style="margin-bottom:8px">
  <label style="display:flex;align-items:center;gap:8px">
    <span style="min-width:150px">Minimum think time:</span>
    <input type="number" id="rgs_min_limit" min="0" max="120" step="5" value="0"
           style="width:80px" />
    <span>secs (0 = off)</span>
  </label>
</div>
<div style="margin-bottom:8px">
  <label style="display:flex;align-items:center;gap:8px">
    <span style="min-width:150px">Maximum think time:</span>
    <input type="number" id="rgs_max_limit" min="0" max="300" step="10" value="0"
           style="width:80px" />
    <span>secs (0 = off)</span>
  </label>
</div>
<div>
  <label style="display:flex;align-items:center;gap:8px">
    <span style="min-width:150px">Pause duration:</span>
    <input type="number" id="rgs_pause" min="2" max="60" step="5" value="5"
           style="width:80px" />
    <span>secs</span>
  </label>
</div>
"""

DECKOPTIONS_JS = """
function setup(options) {
  const store = options.auxData();
  const minInput = document.getElementById("rgs_min_limit");
  const maxInput = document.getElementById("rgs_max_limit");
  const pauseInput = document.getElementById("rgs_pause");

  store.subscribe((data) => {
    minInput.value = data["rgs_min_limit"] ?? 0;
    maxInput.value = data["rgs_max_limit"] ?? 0;
    pauseInput.value = data["rgs_pause"] ?? 5;
  });

  minInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_min_limit: parseInt(minInput.value, 10) || 0 }))
  );
  maxInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_max_limit: parseInt(maxInput.value, 10) || 0 }))
  );
  pauseInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_pause: parseInt(pauseInput.value, 10) || 5 }))
  );
}
$deckOptions.then((options) => {
  options.addHtmlAddon(HTML_CONTENT, () => setup(options));
});
"""


def keys_off(boo):
    global ROMee_State
    ROMee_State = boo


def eval(delay):
    keys_off(True)
    mw.reviewer.bottom.web.eval(BT_JS % delay)
    QTimer.singleShot(delay * 1000, lambda: keys_off(False))


def on_show_answer(card):
    if card.odid and not AFFECTS_FILTERED_DECKS:
        return
    conf = mw.col.decks.config_dict_for_deck_id(card.current_deck_id())
    time_taken = card.time_taken() // 1000
    min_limit = conf.get("rgs_min_limit", 0)
    max_limit = conf.get("rgs_max_limit", 0)
    if min_limit < 1 and max_limit < 1:
        return
    delay = conf.get("rgs_pause", 5)
    trigger = False
    if min_limit > 0 and time_taken < min_limit:
        trigger = True
    elif max_limit > 0 and time_taken > max_limit:
        trigger = True
    if trigger:
        eval(delay)


def on_will_answer_card(ease_tuple, reviewer, card):
    if ROMee_State:
        return (False, ease_tuple[1])
    return ease_tuple


def on_deck_options_loaded(dialog: DeckOptionsDialog) -> None:
    dialog.web.eval(DECKOPTIONS_JS.replace("HTML_CONTENT", json.dumps(DECKOPTIONS_HTML)))


gui_hooks.deck_options_did_load.append(on_deck_options_loaded)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)
gui_hooks.reviewer_will_answer_card.append(on_will_answer_card)
