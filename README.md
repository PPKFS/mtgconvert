NOTES FOR 2021:

Have redone a bunch of stuff in this for 2021. the Delverlens->Deckbox mode works alright, but the deckbox->cardsphere mode has been completely rewritten.
you want to use mtgconvert2021.py, `python mtgconvert2021.py inv.csv delverlens deckbox out.csv`

# mtgconvert
Python script and config files to convert between different CSV export formats of various Magic: the Gathering collection apps and utilities.

Currently built for:

Delver Lens (Deckbox Export) -> Deckbox  
Deckbox -> Cardsphere


Note this will only convert a file that has the correct csv layout as expected, but differing set or card names - for instance 'Promotional: Non-Release' to a specific
set.

---

**Usage**

`python mtgconvert.py infile inputformat outputformat outfile`

infile: the input file  
outfile: the output file  
inputformat: currently supported: `deckbox, delverlens`  
outputformat: currently supported: `deckbox, cardsphere`  

Example usage:  

`python mtgconvert.py inv.csv delverlens deckbox out.csv`

---

**Config file syntax**

Four headings: SET_REPLACE, NAME_REPLACE, NAME_SET_REPLACE, NAME_NUMEBR_REPLACE. These contain replacement rules for all names of a card, all editions, specific name/edition pairs, or alt-art-same-number cards respectively.

A replacement rule for SET_REPLACE or NAME_REPLACE is of the format:

`old_name -> new_name`

A replacement rule for NAME_SET_REPLACE is of the format:

`old_name | old_edition -> new_name | new_edition`

The bulk replacement rule for NAME_SET_REPLACE (e.g. for a set of prerelease promos) is of the format:

`{ name1 | name2 | ... } | old_edition -> new_edition`

The replacement rule for NAME_NUMBER_REPLACE (Alliances, Homelands, Portal for Cardsphere) is of the format:

`name | number -> new_name`

Intention is for the community to update these replacement files as errors and mismatches are found. 
Easiest way to add full new set rules is to use a HTML table copier (e.g. Copytables) and text replace tools. 

To update finicky things (namely Deckbox->Cardsphere alt-art-same-number cards), it is recommended to check the deckbox collector number and the corresponding CS card name. As these are tedious and low-impact, they will be added as people find them.


