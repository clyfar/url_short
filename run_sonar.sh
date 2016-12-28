#!/bin/bash

TEST_FILES=$(find . | grep _test | grep -v pyc | grep -v .swp)
TEST_FILES_CSV=$(for f in $TEST_FILES; do echo -n $f, ;done)

rm coverage.xml
coverage clear

for f in $TEST_FILES
do
    coverage run --source src $f
done

coverage xml --omit ${TEST_FILES_CSV%,} 

sonar-runner
