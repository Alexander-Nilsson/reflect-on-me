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
},maxTime);
"""

DECKOPTIONS_HTML = """
<style>
  #reflect-on-me input { -moz-appearance:textfield; width:80px; }
  #reflect-on-me input::-webkit-inner-spin-button,
  #reflect-on-me input::-webkit-outer-spin-button { -webkit-appearance:none; margin:0; }
  #reflect-on-me label { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
  #reflect-on-me span { min-width:150px; }
  #reflect-on-me .hint { font-size:0.85em; color:#888; margin-left:6px; }
</style>
<div id="reflect-on-me">
  <label>
    <span>Minimum think time (ms):</span>
    <input type="number" id="rgs_min_limit" value="0"
           title="Answer in under this (ms) → pause to force reflection.">
    <span class="hint">0 = off</span>
  </label>
  <label>
    <span>Maximum think time (ms):</span>
    <input type="number" id="rgs_max_limit" value="0"
           title="Think longer than this (ms) → pause to absorb.">
    <span class="hint">0 = off</span>
  </label>
  <label>
    <span>Pause duration (ms):</span>
    <input type="number" id="rgs_pause" value="2000"
           title="Blocks grading for the set duration (ms).">
    <span class="hint">default: 2000</span>
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
    pauseInput.value = data["rgs_pause"] ?? 2000;
  });

  minInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_min_limit: parseInt(minInput.value, 10) || 0 }))
  );
  maxInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_max_limit: parseInt(maxInput.value, 10) || 0 }))
  );
  pauseInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_pause: parseInt(pauseInput.value, 10) || 2000 }))
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
    QTimer.singleShot(delay, lambda: keys_off(False))


def on_show_answer(card):
    if card.odid and not AFFECTS_FILTERED_DECKS:
        return
    conf = mw.col.decks.config_dict_for_deck_id(card.current_deck_id())
    time_taken = card.time_taken()
    min_limit = conf.get("rgs_min_limit", 0)
    max_limit = conf.get("rgs_max_limit", 0)
    if min_limit < 1 and max_limit < 1:
        return
    delay = conf.get("rgs_pause", 2000)
    if (min_limit > 0 and time_taken < min_limit) or (max_limit > 0 and time_taken > max_limit):
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
