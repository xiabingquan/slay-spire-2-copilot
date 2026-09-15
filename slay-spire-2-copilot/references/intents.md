# Enemy intents

Labels come from game loc tables; observed formats during play:

- FORMAT_DAMAGE_SINGLE: attack for N damage (N shown as label value)
- FORMAT_DAMAGE_MULTI / label with xN: attack N times for listed damage each
- FORMAT_STATUS_CARD_COUNT: adds status cards to draw/discard, no direct damage
- FORMAT_EMPTY: no action / placeholder

Note: raw loc BBCode like [font_size=18]x3[/font_size] may leak into labels (known server polish item).
