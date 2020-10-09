# Patriot Coalition Leaked Message Analysis
Various tools oriented towards the analysis of the [Patriot-Coalition-PNW-Daily-Chatter-Scrapes.txt](https://eugeneantifa.noblogs.org/files/2020/09/Patriot-Coalition-PNW-Daily-Chatter-Scrapes.txt) file as downloaded from the [Patriot Coalition: Leaked Messages Show Far-Right Group's Plans for Portland Violence](https://www.bellingcat.com/news/2020/09/23/patriot-coalition-far-right-chat-logs-violence/) article on the [bell&iquest;ngcat](https://www.bellingcat.com) web site.

The end-goal is to produce tools capable of [network diagrams](https://www.data-to-viz.com/graph/network.html) and lookup applications of the various metadata extractable from the text file, e.g.:
- Network diagram of message authors and respondents
- A Python Flask web-based application capable of querying for message text, authors, respondants, sentiment

Along the way, various intermediate text files and work products will be implemented as well because such might be helpful to another analyst's efforts.

At this point in time, to run the leaked_messages_extractor's logic, invoke the "extract_leaked_messages_to_csv_and_sqlite.py" within this folder.
