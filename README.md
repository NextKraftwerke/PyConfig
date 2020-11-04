# PyConfig

## README Plan

1. One sentence description.
1. One paragraph description.
1. Short, basic example without too much explanation or details but showing the two approaches with the global config and with dependency injection from main.
1. Motivation (take a look at the confluence page and the woninchen presentation).
1. No mutable global state. Yes, if you decide to use the global config testing becomes harder and you have the issue that you have to remember to initialize it before using it, but _then_ it is immutable (-ish, with the exception of the test util and repeated initialization, but you can easily scan the codebase to make sure those don't happen). And if you choose to use dependency injection there's no global config at all, no initialization worries etc.
1. Installation.
1. Detailed documentation.
