# Card Usage Guidelines

A card is a tinted, rounded panel around a group of content. It says "this is one unit, apart from the rest" more strongly than anything else on a slide. Used where a slide really has units, it makes the layout calm and obvious; used everywhere, it adds weight that competes with the content and stops meaning anything.

## When a card helps

Grouping can be shown many ways, from weakest to strongest: spacing, a subheading, alignment on columns, a rule, a light tint, a card. Use the weakest one that makes the grouping unmistakable. A card earns its place when a slide holds a few self-contained units of equal standing that must read as separate, and spacing alone leaves it unclear where one ends and the next begins: each unit's heading, words and figure then sit together on their own panel, and the eye takes the slide in as two or three things instead of many.

A card is the wrong tool when the content already has a better form. Items of the same kind read better as a list or a table; items with an order or a cause read better as steps or a flow; numbers to compare belong in a table. A card also can't make a crowded slide less crowded; it only adds edges.

Formal statements (a theorem, lemma, proposition, definition or assumption) always sit on their own card (`add_statement`), even alone on a slide: the card marks them as a different kind of text from the talk's own words, and the same treatment every time makes them easy to spot.

A single box that makes one key result stand out is emphasis, not grouping. Try color first; if a box is needed, keep it to one on the slide and few in the deck.

## How cards look

`add_cards`, `add_card` and `add_statement` draw them: a light tint, 8 pt corners, no border and no shadow (both muddy on projectors). Cards in a group share one width, one height and the same inner layout, so they read as equals. Padding inside a card is smaller than the gap between cards, so each card holds together as one unit. Contents follow the card's padding, not the grid. Cards start at the top of the content area, right under the title like any other block, not floated to the middle of the slide: the eye goes from the title straight to them, and they sit in the same place on every slide. Never put a card inside a card, and never wrap a whole slide in one; the slide is already the frame.

## After building

Look at every card in the deck and ask whether spacing alone would have done as well. If cards appear on most slides, many of them are habit. If the user asks for cards where they don't help, follow the request and say why in one line.
