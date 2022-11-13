fdp
=

[![Build](https://github.com/cedfactory/fdp/actions/workflows/build.yml/badge.svg)](https://github.com/cedfactory/fdp/actions)
[![codecov](https://codecov.io/gh/cedfactory/fdp/branch/main/graph/badge.svg)](https://codecov.io/gh/cedfactory/fdp)


[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=alert_status)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=bugs)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=code_smells)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=coverage)](https://sonarcloud.io/summary/new_code?id=cedfactory_fdp)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cedfactory_fdp)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=cedfactory_fdp&metric=ncloc)](https://sonarcloud.io/dashboard?id=cedfactory_fdp)

API
=

## list

- *exchanges* : for crypto may be hitbtc, bitmex, binance, speratated with ','

example :

```
localhost:5000/list?exchanges=binance
```

## symbol

- *screener* : should be crypto.
- *exchange* : may be hitbtc, bitmex, binance.
- *symbols* : symbols separated with ',' and '/' replaced with '_'

example :

```
localhost:5000/symbol?screener=crypto&exchange=binance&symbols=ETH_EUR
```

## history

- *exchange* : may be hitbtc, bitmex, binance.
- *symbol* : symbols separated with ',' and '/' replaced with '_'
- *start* : date with format yyyy-mm-dd
- *end* (optional) : date with format yyyy-mm-dd
- *interval* (optional) : may be 1m, 1h or 1d (default value)
- *length* (optional) : 
- *indicators* (optional) : indicators separated with ','

example :

```
localhost:5000/history?exchange=binance&symbol=ETH_EUR&start=2022-01-01
```

## recommendations

- *symbols* (optional) : symbols separated with ',' and '/' replaced with '_'
- *screener* : should be crypto
- *exchange* : may be hitbtc, bitmex, binance.
- *interval* : may be 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1W, 1M

example :

```
http://localhost:5000/recommendations?symbols=ETHEUR&screener=crypto&exchange=binance&interval=1h
```

## portfolio

- *exchange* : may be hitbtc, bitmex, binance (default).
- *recommendations* : may be STRONG_SELL, SELL, NEUTRAL, BUY, STRONG_BUY
- *intervals* : may be 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1W, 1M

example :

```
localhost:5000/portfolio?recommendations=STRONG_BUY,BUY&intervals=15m,30m,1h
```
