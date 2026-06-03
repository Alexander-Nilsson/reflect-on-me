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
<div style="margin-bottom:12px;color:#666;font-size:13px">
  When you reveal the answer in under the time limit below, grade buttons
  are hidden for the pause duration — forcing you to reflect before grading.
  Set the limit to 0 to disable.
</div>
<div style="margin-bottom:8px">
  <label style="display:flex;align-items:center;gap:8px">
    <span style="min-width:140px">Speed limit:</span>
    <input type="number" id="rgs_limit" min="0" max="120" step="5" value="0"
           style="width:80px" />
    <span>secs (0 = off)</span>
  </label>
</div>
<div>
  <label style="display:flex;align-items:center;gap:8px">
    <span style="min-width:140px">Pause duration:</span>
    <input type="number" id="rgs_pause" min="2" max="60" step="5" value="5"
           style="width:80px" />
    <span>secs</span>
  </label>
</div>
"""

DECKOPTIONS_JS = """
function setup(options) {
  const store = options.auxData();
  const limitInput = document.getElementById("rgs_limit");
  const pauseInput = document.getElementById("rgs_pause");

  store.subscribe((data) => {
    limitInput.value = data["rgs_limit"] ?? 0;
    pauseInput.value = data["rgs_pause"] ?? 5;
  });

  limitInput.addEventListener("change", () =>
    store.update((data) => ({ ...data, rgs_limit: parseInt(limitInput.value, 10) || 0 }))
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
    limit = conf.get("rgs_limit", 0)
    if limit < 1:
        return
    delay = conf.get("rgs_pause", 5)
    if (card.time_taken() // 1000) > limit:
        eval(delay)
    elif card.queue == 1:
        eval(3)


def on_will_answer_card(ease_tuple, reviewer, card):
    if ROMee_State:
        return (False, ease_tuple[1])
    return ease_tuple


def on_deck_options_loaded(dialog: DeckOptionsDialog) -> None:
    dialog.web.eval(DECKOPTIONS_JS.replace("HTML_CONTENT", json.dumps(DECKOPTIONS_HTML)))


gui_hooks.deck_options_did_load.append(on_deck_options_loaded)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)
gui_hooks.reviewer_will_answer_card.append(on_will_answer_card)
