# TODO
ideas for the future, possible extensions, etc.

Going to happen probably ONLY IF there is feedback, attention, donations, etc.

## analysis options
* sort tables by column headers (there is a javascript for that)

## more columns
* incidence - but must be smoothed over the past 5-7 days
* coloring prevalence per table column, perhaps simply as one more initial data column

## more rows
### Bundesland
* show also the districts AROUND that Bundesland (in table at the top, but still linked to other Bundesland pages)

## extend regions
* aggregate the numbers of district with all its neighbouring districts <=50km

## styling, design
* refactor all colors into a config file
* create a more beautiful colorscheme.

## code safety & beauty
* use 'datacolumns' everywhere (instead of dropping some columns and hoping the remainder is what was expected). Search for TODO
* 'dates' can be generated easily from 'datacolumns' so drop from all function interfaces, instead generate locally 

## integration
* the googlesheet table (momentary prevalence / mortality) is going to have links too, from each row to each Landkreis