#!/bin/bash
# for each PR head, list machine strings added in the diff vs merge-base with BB6
cd /home/user/ext/ccz-busycoq
RE='([01-][LR-][A-F-]){2}(_([01-][LR-][A-F-]){2}){5}'
for n in $(git for-each-ref --format='%(refname:short)' refs/remotes/pr | sed 's#pr/##' | sort -n); do
  h=pr/$n; base=$(git merge-base $h origin/BB6)
  ms=$( (git diff --name-only $base $h; git diff $base $h | grep '^+'; git log --format=%B $base..$h) | grep -oE "$RE" | sort -u | tr '\n' ' ')
  echo "$n|$(git log -1 --format=%ad --date=short $h)|$(git log -1 --format=%an $h)|$ms"
done
