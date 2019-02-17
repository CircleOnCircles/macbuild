#!/usr/bin/env bash

# Ensure that the latest Ruby version is used
export PATH=/usr/local/opt/ruby/bin:$PATH

# Ensure that Ruby gems are in our PATH
export PATH=$(gem environment gemdir)/bin:$PATH
