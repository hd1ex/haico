# Contributing

Thank you for digging into this project!    
There are some small things to read, before you can start coding.

## Style guidelines

Python code has to follow the
[PEP 8 style guide](https://www.python.org/dev/peps/pep-0008).

A python linter/formatter should cover all the relevant rules. Just limit all
lines to a maximum of 79 characters, and you should be good to go. If you are
using an editor which supports [EditorConfig](https://editorconfig.org/), this
should be configured automatically for you.

**All** other source files also have to be limited to 79 characters per line.
There maybe some exceptions, but be prepared to defend these in discussions!

Here are some more things to consider when writing python code:

- Do not mix `'` and `"` for strings in python code, just use `'`

## Pull requests

### Commits

Commits should follow the **recipe based system**. Commits are viewed as small,
self-contained changes (recipes). Between two commits the project should be in
a useful, well-defined state. For example, if you add code in one commit and
modify it in another following one, you probably should join these changes into
one. In a pull request every commit will be viewed individually - if it is not
useful as an individual one, you should join it with others. These commits
should not serve as your personal log, but rather summarize your work in an
useful way.

Here is also some further information about the recipe based system:
https://www.bitsnbites.eu/git-history-work-log-vs-recipe/

If you already have some random commits lying around, consider to use
[git-rebase](https://git-rebase.io/).

### Commit messages

All interesting info about changes should be contained in the commit messages.
Look at the output of `git log` if you are unsure about the style of commit
messages.

If you are completely new, here is a nice and well known blog post about commit
messages: https://chris.beams.io/posts/git-commit/

## Branches

Please base your work on the `main` branch. Expect other branches as work in
progress.

## Miscellaneous

Please use a **spell checker**!

Be nice to other people :)
