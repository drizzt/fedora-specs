#!/bin/sh

export PREFIX="MoonGen-$(git rev-parse --verify --short=8 HEAD)"

git archive --format=tar --prefix="$PREFIX/" --output "$PREFIX.tar" HEAD

git submodule --quiet update --init --recursive
git submodule --quiet foreach --recursive \
	'git archive --format=tar --prefix="$PREFIX/$prefix" --output "/tmp/${name##*/}.tar" HEAD &&
	tar --concatenate --file="$cdup/$PREFIX.tar" "/tmp/${name##*/}.tar" && rm -f "/tmp/${name##*/}.tar"'
gzip -9 "$PREFIX.tar"
