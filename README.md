# mtgconvert
Python script and config files to convert between different CSV export formats of various Magic: the Gathering collection apps and utilities.

Currently built for:

Delver Lens (Deckbox Export) -> Deckbox  
Deckbox -> Cardsphere


Note this will only convert a file that has the correct csv layout as expected, but differing set or card names - for instance 'Promotional: Non-Release' to a specific
set.

---

**Config file syntax**

Three headings: SET_REPLACE, NAME_REPLACE, NAME_SET_REPLACE. These contain replacement rules for all names of a card, all editions, or specific name/edition
pairs respectively.

A replacement rule for SET_REPLACE or NAME_REPLACE is of the format:

`old_name -> new_name`

A replacement rule for NAME_SET_REPLACE is of the format:

`old_name | old_edition -> new_name | new_edition`

The bulk replacement rule for NAME_SET_REPLACE (e.g. for a set of prerelease promos) is of the format:

`{ name1 | name2 | ... } | old_edition -> new_edition`

Intention is for the community to update these replacement files as errors and mismatches are found.

