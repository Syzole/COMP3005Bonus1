Sept 14th - Read about EBNF, max munch, and grammar design, along with parsing and tokenizing
Sept 15th - Tried to make a prototype EBNF. AI was not able to give me a complete EBNF defition despite numerouis attempts it was incomplete. Will Most likley restart from scratch tommarow
Sept 16th - Restarted the EBNF, the ai told me that there is no precednece for unary operators, even when binary operators are present which is wrong. Made more progress and am testing it on the examples given in the document. I also did ask if all the binary operations can be in one precedence value. If not I can move it around but then my EBNF will need to change. 

Did finish the EBNF (after alot of deliberation and tested on a few traces from the document). Seems to be working, will test more to ensure it works for alot of cases. Will also ask prof about the precedence of binary operators and if they can all be in one precedence value. If not I will have to change my EBNF to reflect that, like how I did for "and", "or", and "not" in the condition.

I tried to get Ai to review it, it ended up making a left-recursive suggestion I found after a few minutes of testing the suggestions it gave me.
I also wrote some tests from the assignment specs, will most likley make some more of my own tommarow, which I will use the help of AI to review and improve.

Sept 17th - I started to work on the tokeniser, I have a feeling this will take a while. I plan to use the datatypes to save me some boiler plate code. I also asked the prof about what to do about "\n".
Sept 18th - Tokeniser is working so far, will test further to ensure it works for all cases. Will also begin to start working on AST as well, since the tokeniser is working pretty well so far. AI had made some solid suggestions this time, so I plan to use the suggestions such as how to handle the strings.

Sept 19th - Using what I used for the tokeniser, I started to work on the AST. I also learned that I can treat the "\n" as whitespace. So far solid progress has been made, will continue to work on it tommarow (since it is 3am right now)

Sept 20th & 21st - AST is working pretty well, will continue to work on it, it seems to be working for the examples given in the document. Parser is also working well, will continue to work on it. I tried to use AI, but it had left certain parts out of the EBNF document so I had to write them myself. 

Sept 21st - Parser is working better, added more stuff liek and + or + not, plus condition to work with comparisiosn, now I need to see if it covers all the cases, then will move to evaluation.

Sept 22nd- Evaluation and table loading has started, will continue to work down the cases over the next few days, and wrap up the project by the end of the week (hopefully)

Sept 24th - Evaluation seems to be working, all tests have passed, will double check that tests are correct and complete. Will also start to work on the report.