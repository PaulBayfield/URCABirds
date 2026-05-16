// ──────────────────────────────────────────────────────
// Copyright (c) 2024-present, Paul Bayfield
// All rights reserved.
// ──────────────────────────────────────────────────────

#set page(
  background: image("../images/background.png"),
  numbering: none,
  margin: (
    top: 0cm,
    right: 0cm,
    bottom: 1.5cm,
    left: 0cm,
  ),
)

#set par(
  leading: 1em,
  first-line-indent: 0em,
  justify: false,
)

#set align(center)

#image("../images/spacing.png", width: 40%)

#align(center)[
  #block(
    inset: 0.5cm,
  )[
    #text(font: "Aptos", 2em, weight: 800, "INFO0806 • URCA Birds", fill: rgb("#FFFFFF"))
    #v(0.001em)
    #text(font: "Aptos", 1.6em, weight: 700, "Mise en place du suivi de trajets d'oiseaux", fill: rgb("#FFFFFF"))
  ]
]

#align(bottom)[
  #text(
    font: "Aptos",
    1em,
    weight: 500,
    "Réalisé par " + strong("Paul Bayfield") + " et " + strong("Lucas Charmettan"),
    fill: rgb("#FFFFFF"),
  )
  #v(0.1em)
  #text(font: "Aptos", 1em, weight: 500, strong("UFR Sciences Exactes et Naturelles"), fill: rgb("#FFFFFF"))
  #v(1.5em)
  #line(length: 40%, stroke: (thickness: 1pt, paint: rgb("#FFFFFF")))
  #v(1.5em)
  #stack(
    dir: ltr,
    spacing: 0.5cm,
    image("../images/urca.png", width: 3cm),
    image("../images/ufr.png", width: 2cm),
  )
]
