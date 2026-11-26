# The World in One Day — news-image-20261126 v2

![make.fun badge](https://make.fun/badge/news-image-20261126.svg)
![rank](https://make.fun/badge/news-image-20261126/top234/news-image-20261126-entry-v2/rank.svg)
![reward](https://make.fun/badge/news-image-20261126/top234/news-image-20261126-entry-v2/reward.svg)

A newspaper front page summing up **Thursday 26 November 2026** in one
1024×1024 image: masthead, 3 hero stories, 10 medium cards, a
"BY THE NUMBERS" strip, a numbered world map, and an "ALSO ON..." list —
**all 35 stories** from Reuters / AP / BBC wires of 25–26 November 2026.

## Stories

Heroes: Houthis hit Saudi Arabia's Ras Tanura refinery · Cairo fuel tanker
fire kills 30 · US proposes tariffs on 14 economies (China 20%, EU 15%,
India 17%). Medium cards: Gaza, Ukraine refineries, Russian drones,
Hormuz mines, Huawei convicted, Poland no-fly zone, Colombia hostages
freed, first Pakistani astronaut, Eurostar strike, Solomon Islands–
Australia treaty. The "ALSO ON..." list carries stories 14–35.

Region recount (each story exactly one region, total 35): Middle East 5,
Europe 8, Americas 8, Asia-Pacific 7, Africa 3, World 4.

## Build

```sh
python3 generate.py entry.png   # renders entry.png, 1024x1024, deterministic
node main.ts                     # renders (or falls back to bundled entry.png)
                                 # and writes entry.png to $OUTPUT_DIR
```

`generate.py` is pure Python + PIL, no network, no clock, no randomness:
rendering twice produces byte-identical output, and it exits non-zero
with a WARNING if any text overflows or is truncated. `main.ts` is Node 22
stdlib only and verifies the PNG (signature, IHDR 1024×1024, ≤1 MiB,
IEND trailer) before and after writing.

## Sources

Every fact comes from Reuters / AP / BBC reporting of 25–26 November 2026.
All drawings are original. Press time 00:30 GMT, 26 Nov 2026.

## License

MIT — see [LICENSE](LICENSE).
