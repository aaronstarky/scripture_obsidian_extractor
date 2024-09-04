# Scripture Obsidian Extractor
The code provided in this repository uses some web scraping to extract the text of the standard scriptures of the Church of Jesus Christ of Latter-Day Saints off of their website, and convert the text into MarkDown format. Then, all cross references are formatted in the traditonal Obsidian format so that they can be represented using Obsidian's graph view. 

# Pending Additions
- Add link to previous chapter to the beginning of each note
- Add link to following chapter to the end of each note

- # Issues:
- the unicode long dash character is coming through as unreadable in the obsidian vault.
- references within parentheses are not separated by spaces
- some references are getting parentheses generated but are not containing any actual references (see the following passage)
`14 Neglect ( #Priesthood_Magnifying_Callings_within ) not the gift ( #God_Gifts_of  #Stewardship  #Talents ) that is in thee, which was given thee by prophecy ([[1 Tim. 1_18]] #Prophecy ), with the laying ( #Priesthood_Authority  #Priesthood_Ordination ) on of the hands ( #Hands_Laying_on_of ) of the presbytery ().`
