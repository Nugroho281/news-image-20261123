# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Nugroho281/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Nugroho281/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-page newspaper front page that sums up the world news of **Monday 23 November 2026** in a single 1024×1024 image: 49 stories — 16 drawn as picture panels, 33 more in brief — under one giant date line, with a day-in-numbers rail, a UTC timeline of how the day unfolded, and a date check. The hero story is Ukraine saying its sea drones sank the Russian corvette Merkury at the Libyan port of Benghazi. The pictured panels cover the collapse of the COP31 climate summit in Antalya after a record 49 hours of overtime, the Russian drone strike that partly collapsed an apartment block in Dymer killing at least 11, Nvidia reinstating founder Jensen Huang as CEO as AI stocks rebounded from Friday's rout, the Democrats winning their biggest House majority since 1992, the Banten candy-factory fire that killed 24, Israel's prime minister-elect calling settler arson in the West Bank "Jewish terrorism", Trump calling Putin "my friend" after the Shenzhen summit, drone strikes on Khartoum, an Oxfam report finding contamination across 99% of Gaza, 24 civilians killed in South Sudan, the capture of FBI most-wanted cartel boss "El Chapo Isidro", 12,000 people evacuated from a Manchester concert, South Korea's education minister resigning over an AI exam-cheating scandal, BepiColombo reaching Mercury, and Carlos Alcaraz winning his first ATP Finals title.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=scz7tdtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>

## How it is made

`main.py` is a pure Python 3 standard-library program — no Pillow, no
numpy, no network. It draws the whole page at 2048×2048 (2×
supersample) with flat saturated shapes and a hand-built 5×7 pixel
font, then box-downscales to 1024×1024 so every letter and edge stays
sharp and the colours stay vivid. Two layouts were built and judged
against each other (a warm-paper front page and a dark-masthead page
with a day-in-numbers rail); the dark-masthead layout won the blind
self-judge on thumbnail legibility and visual hierarchy, and it is
the layout this program draws by default. It writes `entry.png`
(63,610 bytes, well under the 1 MiB gate) in about two seconds,
deterministically: two runs produce byte-identical output. The
`entry.png` committed in this repository is the program's exact
output.

## Story credits — all first reported on Monday 23 November 2026

Pictured (16):

- Ukraine says its sea drones sank the Russian corvette Merkury at
  Benghazi, Libya; ten hurt — One Turn day page (France 24, BBC,
  Guardian wires), 23 Nov.
- COP31 in Antalya ends without a deal after a record 49 hours of
  overtime; the EU and about 130 parties reject a draft that never
  mentions fossil fuels — Just Security Early Edition; One Turn;
  Euronews, 23 Nov.
- Russian drone strike partly collapses a five-storey block in Dymer,
  north of Kyiv; at least 11 dead, a boy of seven pulled alive after
  14 hours — One Turn; Just Security, 23 Nov.
- Nvidia's board reinstates founder Jensen Huang as CEO, 11 days
  after he resigned; shares jump about 9% pre-market after Friday's
  14% rout; Nikkei −5.1%, S&P 500 −3.7% — BigGo Finance; TECHi;
  Kitco/Reuters; TipRanks, 23 Nov.
- Democrats secure at least 258 House seats, their biggest majority
  since 1992, after a North Carolina recount — One Turn; Medium
  strategic brief, 23 Nov.
- Fire at the PT Fonusa Agung Mulia candy factory in Banten kills at
  least 24; dozens missing — One Turn Indonesia page (Guardian,
  Euronews, The Hindu wires), 23 Nov.
- Israel's prime minister-elect Gadi Eisenkot calls settler arson
  attacks on Palestinian villages near Ramallah "Jewish terrorism"
  — Just Security; One Turn, 23 Nov.
- Trump calls Putin "my friend" again after a three-way summit with
  Xi Jinping in Shenzhen — One Turn; Frequent Business Traveler,
  23 Nov.
- Drone strikes hit homes and a UN building in Khartoum and
  Omdurman — One Turn, 23 Nov.
- Oxfam report: the war left toxic contamination across 99% of Gaza
  — Medium strategic brief; One Turn, 23 Nov.
- Paramilitary attack kills at least 24 civilians in South Sudan —
  One Turn, 23 Nov.
- Mexico captures FBI most-wanted cartel boss Fausto Isidro Meza
  Flores, "El Chapo Isidro", in Guasave, Sinaloa — One Turn;
  Frequent Business Traveler, 23 Nov.
- About 12,000 people evacuated from a Manchester concert after an
  unknown substance was found — One Turn, 23 Nov.
- South Korea's education minister resigns after an AI-assisted
  cheating scandal upends the national exam — One Turn; UBStandard,
  23 Nov.
- BepiColombo enters orbit around Mercury after an eight-year
  journey — One Turn, 23 Nov.
- Carlos Alcaraz beats world No. 1 Alexander Zverev 6-2, 7-6 to win
  his first ATP Finals title in Turin — Seven Lights; Acast Daily
  Sports Headlines, 23 Nov.

In brief (33): Liverpool beating Manchester United 4-0 in
Pochettino's debut and Boca Juniors winning the Copa Sudamericana
(One Turn; Seven Lights) · Lewis Pugh swimming the Strait of
Hormuz, a robot submarine finding volcanic activity in the Mariana
Trench, otters returning to a once-polluted Kuala Lumpur river and
Nepal's first UN Loss and Damage payout (One Turn) · Nepal PM
Balen Shah visiting India (One Turn) · an ICE video sparking
Seattle protests, the US Justice Department admitting a US citizen
was deported to Mexico, and nine people shot at a California
concert (One Turn) · Kenya and DR Congo restoring ties (One Turn)
· Belgian airports shut in an anti-austerity strike and Capita
shares plunging 67% (One Turn) · ConocoPhillips exiting Norway in
a $4.4bn deal and Tata Steel buying a $1.67bn stake in APL Apollo
(One Turn) · Netanyahu and Eisenkot ending coalition talks without
a deal, Iran vowing all means against the US blockade, a
Russia-bound freighter hit by a drone in the Gulf of Finland,
Denmark accusing Russia of plotting to kill rapper Kyivstoner, the
EU unveiling its 22nd sanctions package and NATO holding emergency
talks after Russian missiles entered Poland (One Turn; Open
Chronicle; Euronews) · Bolsonaro in intensive care and a storm
killing five in a Brazil town (One Turn) · Nigeria moving to end
prison terms for attempted suicide, a new thumb implant for
arthritis, Tamagotchi turning 30 and Doctor Who 63 years on (One
Turn) · Tarik Skubal's record $450m Mets deal, Dallas routing
Tennessee 51-30, the IHSG rising as the rupiah hit a record low,
the Polri/BNN drug-ring bust seizing 378 kg of meth, Prabowo
naming his vice-presidential candidates and the UN seeking an
inquiry into the Merkury sinking (Acast; jawawa.id; indonesianow;
One Turn).

Day in numbers: Nikkei −5.1%, S&P 500 −3.7%, gold +3.1%, 258 House
seats, 24 dead in Banten, 12,000 evacuated in Manchester, 7 sea
drones, 49 hours of COP31 overtime — One Turn; CNBC Indonesia;
Reuters, 23 Nov.

## License

MIT — see `LICENSE`.
