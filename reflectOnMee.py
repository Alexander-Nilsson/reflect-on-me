# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import gui_hooks, mw
from aqt.qt import QLabel, QSpinBox, QTimer

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


def on_deck_conf_setup(deck_conf):
    form = deck_conf.form
    r = form.gridLayout_3.rowCount()

    form.rgs_limit_label = QLabel(form.tab_3)
    form.rgs_limit_label.setText("RefxGrade Ans Limit:")
    form.gridLayout_3.addWidget(form.rgs_limit_label, r, 0, 1, 1)
    form.rgs_limit = QSpinBox(form.tab_3)
    form.rgs_limit.setMinimum(0)
    form.rgs_limit.setMaximum(120)
    form.rgs_limit.setSingleStep(5)
    form.gridLayout_3.addWidget(form.rgs_limit, r, 1, 1, 1)
    sec_label = QLabel(form.tab_3)
    sec_label.setText("secs (0 = disabled)")
    form.gridLayout_3.addWidget(sec_label, r, 2, 1, 1)

    r += 1
    form.rgs_pause_label = QLabel(form.tab_3)
    form.rgs_pause_label.setText("RefxGrade Pause:")
    form.gridLayout_3.addWidget(form.rgs_pause_label, r, 0, 1, 1)
    form.rgs_pause = QSpinBox(form.tab_3)
    form.rgs_pause.setMinimum(2)
    form.rgs_pause.setMaximum(60)
    form.rgs_pause.setSingleStep(5)
    form.gridLayout_3.addWidget(form.rgs_pause, r, 1, 1, 1)
    sec_label2 = QLabel(form.tab_3)
    sec_label2.setText("secs")
    form.gridLayout_3.addWidget(sec_label2, r, 2, 1, 1)


def on_load_config(deck_conf, deck, config):
    deck_conf.form.rgs_limit.setValue(config.get("rgs_limit", 0))
    deck_conf.form.rgs_pause.setValue(config.get("rgs_pause", 10))


def on_save_config(deck_conf, deck, config):
    config["rgs_limit"] = deck_conf.form.rgs_limit.value()
    config["rgs_pause"] = deck_conf.form.rgs_pause.value()


gui_hooks.deck_conf_did_setup_ui_form.append(on_deck_conf_setup)
gui_hooks.deck_conf_did_load_config.append(on_load_config)
gui_hooks.deck_conf_will_save_config.append(on_save_config)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)
gui_hooks.reviewer_will_answer_card.append(on_will_answer_card)
