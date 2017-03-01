# Shortener Url

[![Build Status](https://travis-ci.org/srault95/shortener-url.png?branch=master)](https://travis-ci.org/srault95/shortener-url)
[![Coveralls](https://coveralls.io/repos/srault95/shortener-url/badge.svg?branch=master&service=github)](https://coveralls.io/repos/srault95/shortener-url)
[![Code Health](https://landscape.io/github/srault95/shortener-url/master/landscape.svg?style=flat)](https://landscape.io/github/srault95/shortener-url/master)
[![Build Doc](http://shortener-url.readthedocs.io/en/latest/?badge=latest)](http://shortener-url.readthedocs.io/en/latest)
[![Updates](https://pyup.io/repos/github/srault95/shortener-url/shield.svg)](https://pyup.io/repos/github/srault95/shortener-url/)

## Assistez à la naissance d’un projet Open Source - [Jour 1](https://blog.s2ltic.fr/2017/02/assistez-a-la-naissance-dun-projet-open-source-jour-1.html) 

## Installation

> A partir de l'image disponible sur [Docker Hub](https://hub.docker.com/r/srault95/shortener-url)

	docker run -d --name mongodb mongo:3.4 mongod --noauth
	
	docker run -p 80:8080 -d --name shorturl --link mongodb:mongodb \
		-e SHORTURL_DB_URL=mongodb://mongodb/shorturl \
		srault95/shortener-url
	
## Exécution des tests

	docker run -d --name mongodb_test mongo:3.4 mongod --noauth

	docker build -t shortener_url_tests --build-arg mode=tests \
		https://github.com/srault95/shortener-url.git

	docker run --link mongodb_test:mongodb \
		-e SHORTURL_DB_URL=mongodb://mongodb/shorturl_test \
		shortener_url_tests nosetests shortener_url
