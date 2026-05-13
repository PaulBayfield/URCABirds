// ──────────────────────────────────────────────────────
// Copyright (c) 2024-present, Paul Bayfield
// All rights reserved.
// ──────────────────────────────────────────────────────

// Outline Headers level 1
#show outline.entry.where(level: 1, fill: repeat([.])): it => {
  //v(12pt, weak: true)
  strong(it)
}

// Outline Headers level 2
#show outline.entry.where(level: 2, fill: repeat([.])): it => {
  box(
    inset: (x: 0.5em, y: 0em),
  )
  text(weight: 500, it)
}

// Outline Headers level 3
#show outline.entry.where(level: 3, fill: repeat([.])): it => {
  box(
    inset: (x: 1em, y: 0em),
  )
  text(size: 11pt, it)
}

// Outline Headers level 4
#show outline.entry.where(level: 4, fill: repeat([.])): it => {
  box(
    inset: (x: 1.5em, y: 0em),
  )
  text(size: 11pt, it)
}

// Headers level 1
#show heading.where(level: 1): it => {
  if counter(page).get().at(0) > 1 {
    pagebreak()
  }
  box(
    inset: (y: 0.8em),
    outset: (x: 10000pt),
    text(weight: "bold", fill: black, it.body)
  )
  linebreak()
}

// Headers level 2
#show heading.where(level: 2): it => {
  if counter(page).get().at(0) > 3 {
    box(
      inset: (x: -2em, y: 0.8em),
      width: 1fr,
      text(weight: "bold", fill: black, it)
    )
  } else {
    box(
      inset: (y: 0.8em),
      width: 1fr,
      text(weight: "bold", fill: black, it)
    )
  }
  linebreak()
}

// Headers level 3
#show heading.where(level: 3): it => {
  box(
    inset: (x: -2em, y: 0.8em),
    text(weight: "bold", fill: black, size: 12pt, it)
  )
  linebreak()
}

// Headers level 4
#show heading.where(level: 4): it => {
  box(
    inset: (x: -2em, y: 0.8em),
    text(weight: "semibold", fill: black, size: 11pt, it)
  )
  linebreak()
}

// Footnotes
#set footnote.entry(indent: 0em)

// Figures
#show figure: it => {
  linebreak()
  it
  linebreak()
}

// Figure captions
#set figure.caption(
  separator: " •",
)

// Figure captions
#show figure.caption: it => [
  #text(
    it,
    size: 10pt,
    weight: 500,
    fill: black,
    style: "italic",
  )
]

#show figure.where(kind: "quarto-float-tbl"): set figure(supplement: [Tableau])

#show figure.where(kind: "quarto-float-tbl"): it => {
  show figure.caption: cap => {
    [Tableau ] + cap.counter.display(cap.numbering) + cap.separator + [ ] + cap.body
  }
  it
}

#show ref: it => {
  let el = it.element
  if el != none and el.func() == figure and el.kind == "quarto-float-tbl" {
    link(el.location(), [tableau ] + el.counter.display(el.numbering))
  } else {
    it
  }
}

#set figure(supplement: it => {
  if it.func() == table [Tableau] else [Figure]
})

// Tables
#set table(
  fill: (x, y) =>
    if y == 0 {
      gray.lighten(40%)
    },
  align: center,
)

// Paragraphs
#set par(
  justify: true,
  leading: 0.7em,
  first-line-indent: 2em,
)

// Page setup
#set page(
  margin: auto,
  footer: context {
    let currentPage = counter(page).get().at(0)
    let totalPages = counter(page).final().at(0)

    if counter(page).get().at(0) == 1 {
      return
    }

    box(
      image("./images/footer.jpg", height: 0.9in),
    )
    h(1fr)
    [
      #box(
        inset: (bottom: 15pt),
        text(
          "Page " + str(currentPage) + " sur " + str(totalPages),
          font: "Aptos",
          size: 10pt,
          weight: 400,
          fill: black,
        )
      )
    ]
  }
)

// Bibliography
#set bibliography(
  title: "Bibliographie",
)

// Article
#let article(
  authors: none,
  cols: none,
  date: none,
  font: none,
  lang: none,
  margin: none,
  sectionnumbering: none,
  title: none,
  toc: none,
  toc_depth: none,
  toc_title: none,
  doc,
) = context {
  set text(lang: lang, font: "Inter", hyphenate: false, size: 11pt)
  // set text(font: "Aptos", size: 11pt)
  // set heading(numbering: sectionnumbering)

  // Cover
  include "./content/cover.typ"

  show heading: it => {
    it
    if counter(page).get().at(0) > 3 {
      text()[#v(0.3em, weak: true)]
    }
  }

  set par(
    first-line-indent: 0em,
  )

  // Table of Contents
  outline(
    title: toc_title,
    depth: toc_depth,
    indent: auto,
    target: {
      selector(heading).after(<table-des-matières>, inclusive: false).before(<annexes>, inclusive: false)
    }
  )

  // If figures are present, add a list of figures
  if query(figure).len() > 0 {
    // Table of Figures
    heading("Table des figures", level: 1)
    outline(
      title: none, 
      indent: false,
      target: {
        selector(figure).before(<annexes>, inclusive: false)
      },
      fill: repeat([..])
    )
  }

  set par(
    first-line-indent: 2em,
  )

  // let the fun begin - Quarto document
  doc

  // Annexes
  // include "./content/annexes.typ"
}
