// ──────────────────────────────────────────────────────
// Copyright (c) 2024-present, Paul Bayfield
// All rights reserved.
// ──────────────────────────────────────────────────────

// Some definitions presupposed by pandoc's typst output.
#let blockquote(body) = [
  #set text( size: 0.92em )
  #block(inset: (left: 1.5em, top: 0.2em, bottom: 0.2em))[#body]
]

#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

// Some quarto-specific definitions.

#show raw.where(block: true): set block(
    fill: luma(230),
    width: 100%,
    inset: 8pt,
    radius: 2pt
  )

#let block_with_new_content(old_block, new_content) = {
  let d = (:)
  let fields = old_block.fields()
  fields.remove("body")
  if fields.at("below", default: none) != none {
    // TODO: this is a hack because below is a "synthesized element"
    // according to the experts in the typst discord...
    fields.below = fields.below.abs
  }
  return block.with(..fields)(new_content)
}

#let empty(v) = {
  if type(v) == str {
    // two dollar signs here because we're technically inside
    // a Pandoc template :grimace:
    v.matches(regex("^\\s*$")).at(0, default: none) != none
  } else if type(v) == content {
    if v.at("text", default: none) != none {
      return empty(v.text)
    }
    for child in v.at("children", default: ()) {
      if not empty(child) {
        return false
      }
    }
    return true
  }

}

// Subfloats
// This is a technique that we adapted from https://github.com/tingerrr/subpar/
#let quartosubfloatcounter = counter("quartosubfloatcounter")

#let quarto_super(
  kind: str,
  caption: none,
  label: none,
  supplement: str,
  position: none,
  subrefnumbering: "1a",
  subcapnumbering: "(a)",
  body,
) = {
  context {
    let figcounter = counter(figure.where(kind: kind))
    let n-super = figcounter.get().first() + 1
    set figure.caption(position: position)
    [#figure(
      kind: kind,
      supplement: supplement,
      caption: caption,
      {
        show figure.where(kind: kind): set figure(numbering: _ => numbering(subrefnumbering, n-super, quartosubfloatcounter.get().first() + 1))
        show figure.where(kind: kind): set figure.caption(position: position)

        show figure: it => {
          let num = numbering(subcapnumbering, n-super, quartosubfloatcounter.get().first() + 1)
          show figure.caption: it => {
            num.slice(2) // I don't understand why the numbering contains output that it really shouldn't, but this fixes it shrug?
            [ ]
            it.body
          }

          quartosubfloatcounter.step()
          it
          counter(figure.where(kind: it.kind)).update(n => n - 1)
        }

        quartosubfloatcounter.update(0)
        body
      }
    )#label]
  }
}

// callout rendering
// this is a figure show rule because callouts are crossreferenceable
#show figure: it => {
  if type(it.kind) != str {
    return it
  }
  let kind_match = it.kind.matches(regex("^quarto-callout-(.*)")).at(0, default: none)
  if kind_match == none {
    return it
  }
  let kind = kind_match.captures.at(0, default: "other")
  kind = upper(kind.first()) + kind.slice(1)
  // now we pull apart the callout and reassemble it with the crossref name and counter

  // when we cleanup pandoc's emitted code to avoid spaces this will have to change
  let old_callout = it.body.children.at(1).body.children.at(1)
  let old_title_block = old_callout.body.children.at(0)
  let old_title = old_title_block.body.body.children.at(2)

  // TODO use custom separator if available
  let new_title = if empty(old_title) {
    [#kind #it.counter.display()]
  } else {
    [#kind #it.counter.display(): #old_title]
  }

  let new_title_block = block_with_new_content(
    old_title_block, 
    block_with_new_content(
      old_title_block.body, 
      old_title_block.body.body.children.at(0) +
      old_title_block.body.body.children.at(1) +
      new_title))

  block_with_new_content(old_callout,
    block(below: 0pt, new_title_block) +
    old_callout.body.children.at(1))
}

// 2023-10-09: #fa-icon("fa-info") is not working, so we'll eval "#fa-info()" instead
#let callout(body: [], title: "Callout", background_color: rgb("#dddddd"), icon: none, icon_color: black, body_background_color: white) = {
  block(
    breakable: false, 
    fill: background_color, 
    stroke: (paint: icon_color, thickness: 0.5pt, cap: "round"), 
    width: 100%, 
    radius: 2pt,
    block(
      inset: 1pt,
      width: 100%, 
      below: 0pt, 
      block(
        fill: background_color, 
        width: 100%, 
        inset: 8pt)[#text(icon_color, weight: 900)[#icon] #title]) +
      if(body != []){
        block(
          inset: 1pt, 
          width: 100%, 
          block(fill: body_background_color, width: 100%, inset: 8pt, body))
      }
    )
}

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
) = {
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
      selector(heading).after(<table-des-matières>, inclusive: false).before(<note>, inclusive: false)
    }
  )

  // If figures are present, add a list of figures
  context {
    if query(figure).len() > 0 {
      // Table of Figures
      heading("Table des figures", level: 1)
      outline(
        title: none,
        indent: 0pt,
        target: {
          selector(figure).before(<annexes>, inclusive: false)
        },
      )
    }
  }

  set par(
    first-line-indent: 2em,
  )

  // let the fun begin - Quarto document
  doc

  // Note
  include "./content/note.typ"
}

// ──────────────────────────────────────────────────────
// Copyright (c) 2024-present, Paul Bayfield
// All rights reserved.
// ──────────────────────────────────────────────────────
// 
// Typst custom formats typically consist of a 'typst-template.typ' (which is
// the source code for a typst template) and a 'typst-show.typ' which calls the
// template's function (forwarding Pandoc metadata values as required)
//
// This is an example 'typst-show.typ' file (based on the default template  
// that ships with Quarto). It calls the typst function named 'article' which 
// is defined in the 'typst-template.typ' file. 
//
// If you are creating or packaging a custom typst template you will likely
// want to replace this file and 'typst-template.typ' entirely. You can find
// documentation on creating typst templates here and some examples here:
//   - https://typst.app/docs/tutorial/making-a-template/
//   - https://github.com/typst/templates

#show: doc => article(
  title: [Mise en place du suivi de trajets d'oiseaux],
  authors: (
    ),
  date: [2027-01-05],
  lang: "fr",
  margin: (x: 2cm,y: 2cm,),
  sectionnumbering: "1.1.",
  toc: true,
  toc_title: [Table des matières],
  toc_depth: 5,
  cols: 1,
  doc,
)

= Table des sigles et abréviations
<table-sigles>
- #strong[AMOA] : Assistance à la Maîtrise d'Ouvrage
- #strong[API] : Application Programming Interface
- #strong[CI/CD] : Continuous Integration / Continuous Deployment
- #strong[HTTP] : HyperText Transfer Protocol
- #strong[HTTPS] : HyperText Transfer Protocol Secure
- #strong[IA] : Intelligence Artificielle
- #strong[IoT] : Internet of Things
- #strong[JSON] : JavaScript Object Notation
- #strong[KPI] : Key Performance Indicator (indicateur clé de performance)
- #strong[MOA] : Maîtrise d'Ouvrage
- #strong[MOE] : Maîtrise d'Œuvre
- #strong[PDCA] : Plan, Do, Check, Act
- #strong[RACI] : Responsible, Accountable, Consulted, Informed
- #strong[REST] : Representational State Transfer
- #strong[SMART] : Spécifique, Mesurable, Acceptable, Réaliste, Temporellement défini
- #strong[SQL] : Structured Query Language
- #strong[URCA] : Université de Reims Champagne-Ardenne
- #strong[WAV] : Waveform Audio File Format

= Introduction
<introduction>
Dans le contexte de la surveillance de la biodiversité, l'identification automatique des espèces aviaires par analyse acoustique ouvre de nouvelles perspectives pour le suivi des populations d'oiseaux en milieu naturel ou péri-urbain. Ce projet, développé dans le cadre du module INFO0806 à l'URCA, vise à déployer un système de suivi automatisé des oiseaux sur le campus universitaire Moulin de la Housse à Reims.

Le système repose sur un réseau de nœuds de capture basés sur des Raspberry Pi équipés de microphones. Chaque nœud capture en continu des segments audio de l'environnement et les analyse localement à l'aide du modèle de reconnaissance ornithologique BirdNET @kahl2021birdnet. Les détections identifiées sont ensuite transmises à un serveur central via une API REST, persistées dans une base de données relationnelle PostgreSQL, et consultables via un tableau de bord web.

Ce rapport présente l'architecture générale du système, les choix techniques retenus, ainsi que les détails d'implémentation des deux composants déjà développés : le service de capture (#emph[worker];) embarqué sur Raspberry Pi, l'API REST centrale ainsi que le tableau de bord de visualisation. Les sections suivantes détaillent les différentes étapes du projet, les défis rencontrés et les solutions apportées pour garantir la robustesse, la performance et la scalabilité du système.

= Gestion de projet
<gestion-projet>
== Acteurs du projet
<acteurs-du-projet>
Le projet mobilise deux catégories d'acteurs, conformément au cadre défini en gestion de projets.

La Maîtrise d'Ouvrage (MOA) est représentée par l'encadrant du module INFO0806 de l'URCA, Monsieur Fouchal HACENE. Il exprime le besoin, définit les exigences fonctionnelles et valide les livrables tout au long du projet.

La Maîtrise d'Œuvre (MOE) est constituée de l'équipe de développement, Paul Bayfield et Lucas Charmettan, qui assure la conception, le développement et le déploiement de l'intégralité du système.

== Triangle des contraintes
<triangle-des-contraintes>
Le projet a été piloté en tenant compte des trois contraintes interdépendantes du triangle d'or :

- #strong[Performance] : livrer un système fonctionnel capable d'identifier des espèces aviaires avec un seuil de confiance ≥ 0,80, de transmettre les détections en temps réel et d'assurer la résilience hors-ligne du pipeline.
- #strong[Délais] : respecter les jalons imposés par le module. Le rendu du rapport le 1#super[er] juin 2026, fourniture du lien GitHub le 8 juin 2026, soutenance orale le 11 juin 2026.
- #strong[Coûts] : minimiser les dépenses en s'appuyant exclusivement sur des technologies open source et des services gratuits (Docker Hub, GitHub Actions), avec un matériel mis à disposition par l'UFR.

L'indisponibilité des puces 4G/5G a constitué une contrainte externe imprévue. Conformément à la logique du triangle, cette situation a nécessité un ajustement de la performance (substitution des données réelles par des données simulées) afin de préserver les délais de livraison.

== Objectifs SMART
<objectifs-smart>
Les objectifs du projet ont été formulés selon la méthode SMART :

#table(
  columns: (29.03%, 70.97%),
  align: (auto,auto,),
  table.header([Critère], [Application au projet],),
  table.hline(),
  [#strong[Spécifique];], [Déployer un réseau de capteurs acoustiques pour identifier automatiquement les oiseaux sur le campus Moulin de la Housse],
  [#strong[Mesurable];], [Seuil BirdNET ≥ 0,80 ; disponibilité ≥ 95 % ; capacité ≥ 10 000 détections/jour ; support de 50+ capteurs simultanés],
  [#strong[Acceptable];], [Objectifs validés conjointement par les encadrants (MOA) et l'équipe de développement (MOE) en début de projet],
  [#strong[Réaliste];], [Technologies maîtrisées (Python, Docker, API REST), matériel accessible (Raspberry Pi 4/5)],
  [#strong[Temporel];], [Rapport au 1#super[er] juin, lien GitHub au 8 juin, soutenance au 11 juin 2026],
)
== Répartition des responsabilités
<répartition-des-responsabilités>
La matrice RACI ci-dessous formalise la répartition des responsabilités entre les acteurs du projet :

#table(
  columns: 4,
  align: (auto,center,center,center,),
  table.header([Tâche], [Paul Bayfield], [Lucas Charmettan], [Encadrants (MOA)],),
  table.hline(),
  [Architecture système], [A/R], [A/R], [I],
  [Développement worker], [A/R], [A/R], [I],
  [Développement API REST], [A/R], [C], [I],
  [Pipeline CI/CD], [A/R], [C], [I],
  [Tableau de bord], [C], [A/R], [I],
  [Rédaction du rapport], [R], [R], [A],
  [Validation des livrables], [I], [I], [A],
)
#emph[R = Réalise • A = Approuve • C = Consulté • I = Informé]

== Méthodologie
<méthodologie>
Le projet a été conduit en suivant une organisation agile inspirée de Scrum, adaptée à notre échelle. Nous avons travaillé par sprints de deux à trois semaines, chacun structuré autour d'un planning (définition des tâches et répartition du travail) et d'une review (bilan des livrables et ajustements pour la suite). Des points hebdomadaires informels assuraient la synchronisation continue entre les membres de l'équipe.

Cette démarche itérative s'inscrit dans les trois grandes phases du cycle de vie d'un projet : le cadrage (analyse des besoins et planification, sprints 1-2), la conduite (développement et industrialisation, sprints 3-4) et la clôture (finalisation et soutenance, sprint 5). À chaque fin de sprint, une boucle PDCA (Plan-Do-Check-Act) a guidé l'amélioration continue : les points de blocage identifiés en review alimentaient directement la planification du sprint suivant.

== Sprints
<sprints>
=== Sprint 1 : Initialisation et service Worker (18 févr. - 3 mars 2026)
<sprint-1-initialisation-et-service-worker-18-févr.---3-mars-2026>
#strong[Planning]

L'idée de départ était simple : il fallait d'abord savoir où on allait. Ce premier sprint a donc servi à poser l'architecture globale du système, choisir les technologies et écrire une première version fonctionnelle du worker.

- Initialisation du dépôt GitHub et de la structure du projet
- Conception de l'architecture en trois niveaux (capteurs, API, visualisation)
- Choix des technologies : Python avec asyncio pour le worker, BirdNET pour l'analyse, PostgreSQL pour la persistance
- Développement du pipeline de base : capture audio, analyse BirdNET, boucle asynchrone ~

~

#strong[Review]

Le pipeline fonctionne de bout en bout en local. Le worker capture des segments audio, les soumet à BirdNET et journalise les détections identifiées. L'architecture générale a été validée et la configuration via `.env` est en place.

=== Sprint 2 : API REST et CI/CD (4 mars - 13 mars 2026)
<sprint-2-api-rest-et-cicd-4-mars---13-mars-2026>
#strong[Planning]

Avec le worker opérationnel, il fallait développer l'API REST côté serveur, conteneuriser les deux services et automatiser les déploiements.

- Développement des routes, modèles et composants de l'API avec Sanic
- Mise en place de l'authentification Bearer et de la limitation du débit
- Création des Dockerfiles pour l'API et le worker
- Configuration des workflows GitHub Actions pour la publication des images Docker
- Mise en place de Dependabot pour maintenir les dépendances à jour ~

~

#strong[Review]

L'API expose l'ensemble des endpoints prévus. L'authentification et le rate limiting sont fonctionnels. Le pipeline CI/CD publie automatiquement les images sur Docker Hub à chaque push sur `main`. L'auto-enregistrement du capteur via `POST /v1/sensors/register` fonctionne correctement.

=== Sprint 3 : Stabilisation et support Raspberry Pi (13 mars - 1er avril 2026)
<sprint-3-stabilisation-et-support-raspberry-pi-13-mars---1er-avril-2026>
#strong[Planning]

Les premiers tests sur Raspberry Pi réel ont mis en évidence des problèmes de compatibilité matérielle. Ce sprint était centré sur la résolution de ces blocages.

- Migration de l'image worker vers `python:3.13-slim` pour pouvoir installer `portaudio19-dev`
- Ajout du support ARM64 via `docker buildx` dans le pipeline CI/CD
- Correction du canal audio en mono, requis par BirdNET
- Ajustement du niveau de journalisation ~

~

#strong[Review]

Les images sont désormais publiées pour `amd64` et `arm64`, ce qui permet de déployer directement depuis Docker Hub sur les Raspberry Pi 4 et 5 sans recompilation locale. La capture audio fonctionne correctement sur le matériel cible. Le service a été validé en conditions réelles sur le campus.

=== Sprint 4 : Maintenance et rédaction du rapport (avril - mai 2026)
<sprint-4-maintenance-et-rédaction-du-rapport-avril---mai-2026>
#strong[Planning]

Le gros du développement étant terminé, ce sprint s'est concentré sur la stabilité du projet dans le temps et le démarrage de la rédaction du rapport.

- Mise à jour des dépendances Python et des actions GitHub Actions
- Rédaction du rapport : architecture, implémentation, déploiement
- Préparation des figures et diagrammes de séquence ~

~

#strong[Review]

Le rapport est structuré et les sections principales sont rédigées. Les diagrammes sont intégrés.

=== Sprint 5 : Tableau de bord et finalisation (mai - 1er juin 2026, en cours)
<sprint-5-tableau-de-bord-et-finalisation-mai---1er-juin-2026-en-cours>
#strong[Planning]

Ce dernier sprint couvre le développement du tableau de bord de visualisation, la finalisation du rapport et la préparation de l'oral.

- Développement du tableau de bord web pour visualiser les détections
- Affichage des détections sur une carte interactive du campus
- Rendu du rapport (délai : 1er juin 2026 à 12 h)
- Fourniture du lien GitHub (délai : 8 juin 2026 à 12 h)
- Préparation de la soutenance orale (11 juin 2026)

= 1. Contexte et objectifs
<contexte>
== 1.1. Problématique
<problématique>
Le suivi des populations d'oiseaux représente un enjeu écologique important pour évaluer la biodiversité et mesurer l'impact des activités humaines sur les écosystèmes. Les méthodes traditionnelles de recensement requièrent une présence humaine régulière sur le terrain, ce qui est coûteux en temps et limite la granularité des données collectées.

L'avancée des modèles d'IA appliqués à la bioacoustique permet désormais d'identifier automatiquement les espèces aviaires à partir de leurs chants. Le modèle BirdNET @birdnet_analyzer, développé par la Cornell Lab of Ornithology et l'Institut Max Planck, est en mesure de distinguer plus de 6 000 espèces d'oiseaux avec une précision élevée, en s'appuyant sur des enregistrements audio de courte durée.

== 1.2. Objectifs du projet
<objectifs-du-projet>
Le projet URCABirds vise à :

- déployer un réseau de capteurs autonomes sur le campus universitaire Moulin de la Housse ;
- identifier automatiquement les espèces aviaires en temps réel par analyse acoustique ;
- centraliser les données de détection sur un serveur avec une API REST ;
- offrir un tableau de bord de visualisation permettant le suivi temporel et géographique des détections. ~

~

== 1.3. Périmètre
<périmètre>
Le périmètre initial du projet se limite au campus universitaire Moulin de la Housse, avec au minimum trois nœuds de capture distribués. L'architecture a néanmoins été conçue pour être généralisable à d'autres sites avec un minimum de reconfiguration.

À ce jour, les Raspberry Pi ne sont pas encore déployés en production sur le campus. Deux obstacles liés à la connectivité l'en empêchent : le Wi-Fi de l'université n'est pas disponible partout sur le campus, et surtout il impose une ré-authentification manuelle quotidienne sur le portail captif, incompatible avec des capteurs autonomes. En attendant la livraison de puces 4G/5G qui permettront une connexion indépendante du réseau universitaire, les capteurs ne peuvent pas transmettre leurs données au serveur central.

Pour permettre le développement et les tests du tableau de bord en l'absence de données réelles, nous avons intégré des données simulées, inspirées des positions géographiques effectives des futurs emplacements de capteurs sur le campus.

= 2. Architecture du système
<architecture>
== 2.1. Vue d'ensemble
<vue-densemble>
Le système repose sur une architecture distribuée à trois niveaux : les nœuds de capture (Raspberry Pi avec microphones USB), le serveur central (API REST et base de données PostgreSQL), et l'interface web de visualisation (en cours de développement).

#figure([
#box(image("figures/arch.png"))
], caption: figure.caption(
position: bottom, 
[
Architecture générale du système
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-arch>


== 2.2. Composants matériels
<composants-matériels>
Chaque nœud de capture est composé d'un Raspberry Pi 4 ou 5, d'une carte microSD, d'un microphone USB adapté à la captation extérieure et d'un boîtier étanche. La connectivité est assurée par Wi-Fi ou Ethernet selon l'emplacement.

Le serveur central tourne sous Linux Ubuntu Server sur une machine disposant de 4 cœurs, 16 Go de RAM et 1 To de stockage, avec redondance sur disque externe.

== 2.3. Flux de données
<flux-de-données>
Le cycle de vie d'une détection suit les étapes suivantes :

#figure([
#box(image("figures/seq-flux.png"))
], caption: figure.caption(
position: bottom, 
[
Diagramme de séquence - cycle de vie d'une détection
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-seq-flux>


= 3. Nœuds de capture (Worker)
<worker>
== 3.1. Architecture générale
<architecture-générale>
Le service #emph[worker] est un programme Python asynchrone (`asyncio`) déployé en conteneur Docker sur chaque Raspberry Pi. Il orchestre l'ensemble du cycle : capture audio, analyse ornithologique, transmission à l'API et gestion du cache hors-ligne.

La classe `Worker` est le point d'entrée principal. Elle initialise les différents sous-systèmes au démarrage et exécute une boucle principale infinie :

+ Enregistrement d'un segment audio de 10 secondes dans le répertoire `captures/`
+ Lancement de l'analyse BirdNET dans un #emph[thread pool executor] (tâche CPU-intensive)
+ Transmission des détections filtrées à l'API REST
+ Synchronisation périodique des enregistrements mis en cache localement

L'utilisation de `concurrent.futures.ThreadPoolExecutor` permet d'éviter le blocage de la boucle `asyncio` lors de l'inférence BirdNET, qui est une opération synchrone et intensivement calculatoire. Le nombre de #emph[threads] alloués est `max(1, nb_cœurs - 1)`.

== 3.2. Capture audio
<capture-audio>
La classe `Audio` (module `utils/audio.py`) gère l'enregistrement via `sounddevice` @sounddevice et la sauvegarde sur disque avec `soundfile`. L'audio est enregistré en mono à 44 100 Hz au format PCM 16 bits, par segments de 10 secondes configurables.

En cas d'indisponibilité du périphérique audio (environnement de test), le module bascule automatiquement sur un mode #emph[mock] simulant la durée d'enregistrement sans capturer de vrai signal, permettant de tester le reste du pipeline.

== 3.3. Analyse ornithologique avec BirdNET
<analyse-ornithologique-avec-birdnet>
La classe `Analyser` (module `utils/analyser.py`) encapsule le modèle BirdNET v2.4 @birdnet_analyzer via la bibliothèque Python `birdnet`. Le modèle acoustique est chargé une seule fois à l'initialisation du worker.

```python
self.model = birdnet.load("acoustic", "2.4", "tf")
```

~

Pour chaque segment audio, la méthode `analyse_audio()` appelle `model.predict()` sur le fichier WAV, itère sur les prédictions retournées sous forme de tableau structuré, filtre les résultats selon le seuil de confiance configurable (`CONFIDENCE_THRESHOLD`), puis supprime le fichier audio temporaire. Le seuil par défaut de 0,80 est recommandé pour limiter les faux positifs en conditions extérieures. ~

~

== 3.4. Cache local et résilience hors-ligne
<cache-local-et-résilience-hors-ligne>
La classe `Database` (module `utils/db.py`) gère un cache SQLite local dans `cache.db`. Ce mécanisme garantit qu'aucune détection n'est perdue en cas d'indisponibilité réseau ou de l'API.

La table SQLite `detections` stocke les champs `timestamp`, `species`, `confidence` et un indicateur booléen `synced`. Lors de chaque cycle de la boucle principale, `sync_offline_data()` récupère les entrées non synchronisées et tente de les transmettre à l'API. Dès qu'une tentative échoue, la synchronisation s'arrête pour éviter d'inonder l'API à la reprise réseau.

== 3.5. Configuration
<configuration>
Au démarrage, le worker s'auto-enregistre auprès de l'API via `POST /v1/sensors/register`, en transmettant son identifiant, ses coordonnées GPS et son nom. Si le capteur est déjà enregistré, l'appel met à jour le champ `last_connection`. L'ensemble du comportement est piloté par des variables d'environnement définies dans un fichier `.env` : `API_URL`, `API_KEY`, `SENSOR_ID`, `SENSOR_NAME`, `CONFIDENCE_THRESHOLD`, `LATITUDE`, `LONGITUDE`, `AUDIO_DURATION` et `LOG_LEVEL`.

= 4. API REST
<api>
== 4.1. Présentation
<présentation>
L'API REST est développée avec le framework Sanic @sanic (Python 3.13+), un framework web asynchrone adapté aux charges I/O intensives. Elle expose les données de détection aux workers et au futur tableau de bord, et assure la gestion du registre de capteurs ainsi que l'administration des clés d'accès. La documentation OpenAPI est générée automatiquement et accessible via Scalar UI. La connexion à PostgreSQL est gérée par `asyncpg` @asyncpg avec un pool de 10 connexions maintenues en permanence.

#figure([
#box(image("figures/scalar-ui.png"))
], caption: figure.caption(
position: bottom, 
[
Interface de documentation interactive de l'API (Scalar UI)
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-scalar>


== 4.2. Endpoints disponibles
<endpoints-disponibles>
Tous les endpoints sont versionnés sous le préfixe `/v1/`. L'endpoint `GET /v1/detections` accepte les paramètres `limit` (1 à 100, défaut 50), `offset`, `species` et `sensor_id` pour filtrer et paginer les résultats. L'endpoint `POST /v1/sensors/register` effectue un #emph[upsert] : si le capteur existe déjà, ses métadonnées et sa date de dernière connexion sont mises à jour, sinon un nouvel enregistrement est créé.

#table(
  columns: (23.68%, 26.32%, 15.79%, 34.21%),
  align: (auto,auto,auto,auto,),
  table.header([Méthode], [Endpoint], [Auth], [Description],),
  table.hline(),
  [`POST`], [`/v1/detections`], [Requise], [Soumettre une détection],
  [`GET`], [`/v1/detections`], [Optionnelle], [Lister les détections (paginé, filtrable)],
  [`GET`], [`/v1/detections/{id}`], [Optionnelle], [Consulter une détection par ID],
  [`POST`], [`/v1/sensors/register`], [Requise], [Enregistrer ou mettre à jour un capteur],
  [`GET`], [`/v1/sensors`], [Optionnelle], [Lister tous les capteurs],
  [`GET`], [`/v1/sensors/{sensor_id}`], [Optionnelle], [Consulter un capteur],
  [`GET`], [`/v1/species`], [Optionnelle], [Lister les espèces détectées],
  [`GET`], [`/v1/species/{name}`], [Optionnelle], [Statistiques d'une espèce],
  [`GET`], [`/v1/status`], [Aucune], [Health check],
  [`GET`], [`/v1/stats`], [Aucune], [Statistiques globales],
  [`GET`], [`/v1/apikeys`], [Admin], [Lister les clés d'API],
  [`POST`], [`/v1/apikeys`], [Admin], [Créer une clé d'API],
  [`DELETE`], [`/v1/apikeys/{id}`], [Admin], [Supprimer une clé d'API],
)
#figure([
#box(image("figures/api-response.png"))
], caption: figure.caption(
position: bottom, 
[
Exemple de réponse JSON de l'endpoint GET /v1/detections
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-api>


== 4.3. Authentification
<authentification>
L'API utilise une authentification par clé Bearer (`Authorization: Bearer <API_KEY>`). Les clés sont stockées dans la table `api_keys` de PostgreSQL et peuvent être marquées comme #emph[admin] pour accéder aux endpoints de gestion.

Pour réduire les accès en base de données, les tokens validés sont mis en cache en mémoire pendant 60 secondes via le dictionnaire `_TOKEN_CACHE`. Deux décorateurs distincts protègent les routes : `@require_api_key` vérifie la présence d'une clé valide, et `@require_admin_key` exige en plus le flag `admin = TRUE`.

== 4.4. Limitation du débit
<limitation-du-débit>
Le décorateur `@ratelimit()` protège chaque endpoint contre les abus. Par défaut, la limite est fixée à 100 requêtes par fenêtre de 60 secondes, par IP ou par clé d'API. En cas de dépassement, l'API retourne une réponse `429 Too Many Requests` avec un en-tête `Retry-After` indiquant le délai d'attente. Le comptage est réalisé par #emph[buckets] en mémoire, configurables par endpoint.

= 5. Base de données
<bdd>
== 5.1. Schéma
<schéma>
La base de données PostgreSQL repose sur trois tables. La table #strong[`api_keys`] gère les clés d'authentification. Chaque clé possède un flag `admin` permettant de distinguer les accès privilégiés. La table #strong[`sensors`] constitue le registre des capteurs déployés, avec leurs coordonnées géographiques et une référence vers leur clé d'API associée. Les champs `first_registered` et `last_connection` permettent de suivre l'activité de chaque nœud. La table #strong[`detections`] stocke chaque détection ornithologique. La colonne `sensor_id` est une clé étrangère vers `sensors(id)` avec suppression en cascade pour garantir la cohérence référentielle.

```sql
CREATE TABLE api_keys (
    id         SERIAL PRIMARY KEY,
    key        TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    admin      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sensors (
    id               SERIAL PRIMARY KEY,
    sensor_id        TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    description      TEXT,
    api_key_id       INTEGER NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    first_registered TIMESTAMPTZ DEFAULT NOW(),
    last_connection  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE detections (
    id         SERIAL PRIMARY KEY,
    sensor_id  INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp  TEXT NOT NULL,
    species    TEXT NOT NULL,
    confidence REAL NOT NULL
);
```

Les insertions et requêtes complexes (filtrage, pagination, agrégation) sont réalisées via des requêtes SQL paramétrées avec `asyncpg`, sans ORM, pour des performances optimales.

= 6. Déploiement
<deploiement>
== 6.1. Conteneurisation Docker
<conteneurisation-docker>
L'API et le worker sont chacun packagés sous forme d'image Docker @docker indépendante. L'image de l'API utilise `python:3.13-alpine` pour sa légèreté et expose le port `7000`. L'image du worker utilise `python:3.13-slim`, nécessaire pour compiler la dépendance système `portaudio19-dev` requise par `sounddevice`.

Les images sont construites et publiées automatiquement par le pipeline CI/CD sur Docker Hub. Le worker dispose d'un fichier `compose.yml` facilitant son déploiement sur le Raspberry Pi :

```yaml
services:
  worker:
    image: paulbayfield/urcabirds-worker:latest
    container_name: worker
    platform: linux/arm64
    devices:
      - "/dev/snd:/dev/snd"
    group_add:
      - audio
    ipc: host
    environment:
      - API_URL=${API_URL}
      - API_KEY=${API_KEY}
      - SENSOR_ID=${SENSOR_ID}
      - SENSOR_NAME=${SENSOR_NAME}
      - CONFIDENCE_THRESHOLD=${CONFIDENCE_THRESHOLD}
      - LATITUDE=${LATITUDE}
      - LONGITUDE=${LONGITUDE}
      - LOG_LEVEL=${LOG_LEVEL}
    restart: unless-stopped
```

~

Plusieurs points méritent d'être soulignés :

- #strong[`image`] : le worker est déployé depuis l'image publiée sur Docker Hub, sans nécessiter de compilation locale sur le Raspberry Pi.
- #strong[`platform: linux/arm64`] : cible explicitement l'architecture ARM64 des Raspberry Pi 4 et 5. Le pipeline CI/CD construit des images multi-architectures (`amd64` et `arm64`) via `docker buildx`.
- #strong[`devices: /dev/snd`] : expose le périphérique audio ALSA du système hôte au conteneur, permettant l'accès au microphone USB.
- #strong[`group_add: audio`] : ajoute le groupe `audio` au conteneur pour les permissions matérielles nécessaires à `sounddevice`.
- #strong[`ipc: host`] : partage le namespace IPC avec l'hôte, requis pour certaines implémentations ALSA.
- #strong[`restart: unless-stopped`] : assure le redémarrage automatique du service en cas de plantage ou de redémarrage du système. ~

~

== 6.2. Intégration continue
<intégration-continue>
Un pipeline GitHub Actions est configuré pour l'API (`api-deployment.yaml`). Il se déclenche automatiquement à chaque #emph[push] sur la branche `main` : il extrait la version depuis `pyproject.toml`, construit l'image Docker avec le cache GitHub Actions, puis publie l'image avec les tags `latest` et la version sémantique dans un registre de conteneurs.

= 7. Interface graphique
<dashboard>
== 7.1. Présentation générale
<présentation-générale>
Le tableau de bord est développé avec Streamlit @streamlit, un framework Python permettant de créer des applications web interactives sans écrire de HTML ou de JavaScript. Les visualisations sont réalisées avec Plotly Express @plotly pour les graphiques interactifs, et Matplotlib couplé à librosa @librosa pour les représentations spectrales. L'application est disponible en français et en anglais grâce à un module d'internationalisation (`_i18n.py`) qui résout chaque libellé à partir d'un dictionnaire de clés selon la langue sélectionnée dans la barre latérale.

La barre latérale expose le titre de l'application, le sélecteur de langue et l'URL de l'API configurée. La navigation entre les sept pages s'effectue depuis ce même panneau. Toutes les données affichées sont récupérées en temps réel depuis l'API REST via un client HTTP dédié (`api_client.py`) ; aucune donnée n'est mise en cache localement dans l'application.

== 7.2. Vue d'ensemble
<vue-densemble-1>
La page d'accueil présente une synthèse immédiate de l'état du système. Trois métriques sont affichées en en-tête : 2 122 détections totales, 6 capteurs actifs et 89 espèces identifiées. Sous ces indicateurs, un graphique en anneau présente la part des dix espèces les plus détectées, avec #emph[Turdus merula] (18,8 %) et #emph[Parus major] (13,2 %) en tête, tandis qu'un histogramme horizontal compare le volume de détections par capteur. Le Capteur UFR Sciences domine avec environ 650 détections, suivi des capteurs Zone Boisée Nord et Jardin Paysager (environ 590 chacun), puis des capteurs de test avec un volume nettement inférieur. Ces deux graphiques permettent d'identifier les espèces et les sites les plus actifs, et de repérer d'éventuels déséquilibres de couverture entre capteurs.

#figure([
#box(image("images/dashboard/vue_ensemble1.png"))
], caption: figure.caption(
position: bottom, 
[
Indicateurs clés, anneau des espèces dominantes et détections par capteur
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-overview1>


La carte de chaleur croise les 24 heures de la journée (axe X) et les jours de la semaine (axe Y), l'intensité représentant le nombre de détections. Sur les données affichées (mercredi, jeudi, vendredi), on observe deux fenêtres d'activité : un pic matinal entre 3 h et 6 h, correspondant au chœur de l'aube, et une activité diurne entre 13 h et 16 h. Cette représentation est utile pour calibrer les plages d'enregistrement et vérifier que le comportement acoustique est cohérent avec la biologie des espèces.

#figure([
#box(image("images/dashboard/vue_ensemble2.png"))
], caption: figure.caption(
position: bottom, 
[
Carte de chaleur de l'activité par heure et par jour
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-overview2>


L'histogramme de l'activité des 100 derniers enregistrements, répartis sur trois jours (13 au 15 mai 2026), révèle des pics ponctuels, notamment 16 détections dans la nuit du 13 au 14 mai autour de minuit. Ce graphique permet de repérer des événements exceptionnels dans le flux de détections ou d'identifier des périodes de silence anormal pouvant signaler une panne.

#figure([
#box(image("images/dashboard/vue_ensemble3.png"))
], caption: figure.caption(
position: bottom, 
[
Histogramme de l'activité de détection sur les 100 derniers enregistrements
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-overview3>


Le tableau d'activité récente liste les 10 dernières détections avec horodatage, nom scientifique, identifiant du capteur et score de confiance affiché sous forme de barre colorée. Il offre une vérification immédiate de la fraîcheur des données et de la qualité des détections en cours.

#figure([
#box(image("images/dashboard/vue_ensemble4.png"))
], caption: figure.caption(
position: bottom, 
[
Tableau des 10 dernières détections avec score de confiance
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-overview4>


== 7.3. Explorateur de détections
<explorateur-de-détections>
La page de détections permet de filtrer l'ensemble des enregistrements par nom d'espèce (nom scientifique), identifiant de capteur et limite de résultats (jusqu'à 500). Un compteur indique le nombre d'enregistrements correspondants sur le total de la base.

L'histogramme des scores de confiance, calculé sur 100 enregistrements, montre une distribution relativement uniforme entre 0,80 et 0,98, avec une légère concentration autour de 0,80. Ce profil est attendu avec un seuil fixé à 0,80 : la majorité des détections retenues se situent juste au-dessus du seuil, les détections très confiantes (supérieures à 0,95) restant minoritaires. Le classement horizontal identifie #emph[Curruca atricapilla] (15 occurrences) et #emph[Hirundo rustica] (12) comme les espèces les plus fréquentes dans la fenêtre filtrée.

#figure([
#box(image("images/dashboard/detections1.png"))
], caption: figure.caption(
position: bottom, 
[
Distribution des scores de confiance et classement des espèces
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-det1>


Le nuage de points chronologique place les espèces en axe Y et le temps en axe X (13 au 15 mai 2026), chaque point étant coloré selon son score de confiance. Cette vue permet de visualiser la co-occurrence temporelle de plusieurs espèces, d'identifier celles présentes uniquement à certaines heures et de repérer des détections isolées pouvant signaler des passages ponctuels.

#figure([
#box(image("images/dashboard/detections2.png"))
], caption: figure.caption(
position: bottom, 
[
Chronologie des détections de 13 espèces sur 3 jours
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-det2>


Le tableau interactif liste l'ensemble des détections filtrées avec horodatage précis, espèce, capteur et barre de confiance. Il permet un audit ligne par ligne des données brutes, utile pour vérifier des détections douteuses.

#figure([
#box(image("images/dashboard/detections3.png"))
], caption: figure.caption(
position: bottom, 
[
Tableau interactif des enregistrements filtrés
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-det3>


== 7.4. Tendances
<tendances>
La page de tendances s'appuie sur les 1 000 détections les plus récentes pour rendre compte de l'évolution de l'activité ornithologique dans le temps.

La courbe du nombre de détections quotidiennes montre une montée progressive de 22 détections le 13 mai à un pic de 44 le 14 mai, suivie d'une redescente à 31 le 15 mai. Cette variation journalière peut refléter des conditions météorologiques, des mouvements migratoires ou la variabilité naturelle de l'activité acoustique.

#figure([
#box(image("images/dashboard/tendances1.png"))
], caption: figure.caption(
position: bottom, 
[
Nombre de détections quotidiennes
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-trend1>


La courbe de richesse spécifique (espèces uniques par jour) reste quasi-stable autour de 16 espèces, ce qui indique une diversité cohérente malgré les variations de volume total. Le diagramme polaire des détections par heure confirme le patron bimodal : un pic très marqué entre 3 h et 5 h du matin (jusqu'à 14 détections par heure) et une activité secondaire entre 15 h et 20 h. La richesse spécifique mesure la diversité tandis que le diagramme polaire révèle les rythmes circadiens ; les deux sont complémentaires pour interpréter les données.

#figure([
#box(image("images/dashboard/tendances2.png"))
], caption: figure.caption(
position: bottom, 
[
Richesse spécifique quotidienne et diagramme polaire de l'activité horaire
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-trend2>


Le graphique multi-courbes des cinq espèces les plus fréquentes (#emph[Curruca atricapilla];, #emph[Erithacus rubecula];, #emph[Hirundo rustica];, #emph[Luscinia megarhynchos];, #emph[Turdus merula];) montre qu'#emph[Hirundo rustica] présente le pic le plus élevé (8 détections le 14 mai) tandis que #emph[Curruca atricapilla] maintient une présence plus régulière. Ce suivi comparatif permet de repérer des dynamiques de population ou des phénomènes migratoires différenciés entre espèces.

#figure([
#box(image("images/dashboard/tendances3.png"))
], caption: figure.caption(
position: bottom, 
[
Évolution quotidienne des 5 espèces les plus détectées
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-trend3>


== 7.5. Suivi des déplacements
<suivi-des-déplacements>
Cette page infère les trajets inter-capteurs d'une espèce sélectionnée en identifiant des détections successives de cette même espèce sur des capteurs différents au sein d'une fenêtre temporelle configurable (de 5 à 240 minutes). Le mécanisme repose exclusivement sur les horodatages et les identifiants de capteurs, sans données GPS embarquées sur les individus.

Trois paramètres pilotent l'analyse : le choix de l'espèce (ici #emph[Turdus merula];, le Merle noir), la fenêtre de déplacement (60 minutes) et la limite de détections à charger (500). Le résumé indique 100 détections réparties sur 3 capteurs.

#figure([
#box(image("images/dashboard/mouvement1.png"))
], caption: figure.caption(
position: bottom, 
[
Panneau de contrôle du suivi par espèce
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-mv1>


Le nuage de points chronologique représente les détections de #emph[Turdus merula] sur les trois capteurs du campus entre avril et mi-mai 2026. Les lignes en pointillés orangés relient les paires de détections constituant un déplacement inféré, révélant que le Merle noir circule régulièrement entre les trois zones, en particulier entre le Capteur UFR Sciences et les deux autres sites. La couleur de chaque point reflète le score de confiance associé à la détection.

#figure([
#box(image("images/dashboard/mouvement2.png"))
], caption: figure.caption(
position: bottom, 
[
Chronologie des détections de Turdus merula par capteur
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-mv2>


La carte OpenStreetMap du campus positionne les trois capteurs par leurs coordonnées GPS et superpose des arcs orangés matérialisant les déplacements inférés. L'épaisseur de chaque arc est proportionnelle au nombre de transitions observées, permettant d'identifier les corridors de circulation les plus fréquents.

#figure([
#box(image("images/dashboard/mouvement3.png"))
], caption: figure.caption(
position: bottom, 
[
Carte des déplacements inférés sur le campus
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-mv3>


Le tableau des 17 déplacements inférés liste pour chaque transition la date et l'heure de départ, le capteur d'origine, le capteur de destination et le delta temporel en minutes. Les deltas varient de 8,8 à 51 minutes, ce qui est cohérent avec les distances entre capteurs sur le campus. Un résumé agrégé indique les paires les plus fréquentes et leur delta moyen.

#figure([
#box(image("images/dashboard/mouvement4.png"))
], caption: figure.caption(
position: bottom, 
[
Tableau des déplacements inférés avec deltas temporels
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-mv4>


== 7.6. Réseau de capteurs
<réseau-de-capteurs>
La carte OpenStreetMap affiche les capteurs géolocalisés sur le campus Moulin de la Housse, colorés selon leur volume de détections. Cette vue géographique est utile pour vérifier la couverture spatiale du réseau et repérer d'éventuelles zones sans capteur.

#figure([
#box(image("images/dashboard/capteurs1.png"))
], caption: figure.caption(
position: bottom, 
[
Carte du campus avec les capteurs géolocalisés
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sen1>


L'histogramme horizontal confirme la domination du Capteur UFR Sciences (environ 650 détections), suivi de près par les capteurs Zone Boisée Nord et Jardin Paysager (environ 590 chacun), puis du capteur Testing (environ 200) et des prototypes Raspberry Pi. Le graphique en anneau exprime les mêmes données en parts relatives : les trois capteurs opérationnels représentent chacun environ 28 à 32 % du total, ce qui valide une couverture équilibrée du réseau.

#figure([
#box(image("images/dashboard/capteurs2.png"))
], caption: figure.caption(
position: bottom, 
[
Volume de détections par capteur et parts relatives
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sen2>


Le répertoire détaille pour chaque nœud son identifiant technique, sa description d'emplacement, son nombre total de détections et sa date de dernière connexion. Les emplacements illustrent la diversité des environnements couverts : avant-toit d'un bâtiment universitaire, chêne centenaire en lisière boisée, buissons du jardin paysager. La date de dernière connexion permet de détecter immédiatement un capteur hors ligne.

#figure([
#box(image("images/dashboard/capteurs3.png"))
], caption: figure.caption(
position: bottom, 
[
Répertoire des capteurs avec emplacements et dates de connexion
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sen3>


== 7.7. Statistiques des espèces
<statistiques-des-espèces>
Le treemap représente les 89 espèces détectées, la surface de chaque case étant proportionnelle au nombre de détections. #emph[Turdus merula] (172 détections) occupe la plus grande surface, suivi de #emph[Parus major] (135), #emph[Curruca atricapilla] (111), #emph[Erithacus rubecula] (110) et #emph[Passer domesticus] (108). Les espèces rares apparaissent sous forme de micro-cases. On note la présence d'entrées telles que « Gun\_Gun » (10) et « Human vocal » (20), qui sont des faux positifs illustrant les limites du seuil de confiance à 0,80 et justifient une vigilance sur la qualité des données.

#figure([
#box(image("images/dashboard/especes1.png"))
], caption: figure.caption(
position: bottom, 
[
Treemap de diversité des 89 espèces détectées
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sp1>


L'histogramme horizontal du top 15, dont le nombre d'espèces est ajustable par curseur, confirme #emph[Turdus merula] (172 détections) comme l'espèce largement dominante. #emph[Parus major] (135) arrive en deuxième position, suivi d'un groupe compact de quatre espèces entre 104 et 111 détections.

#figure([
#box(image("images/dashboard/especes2.png"))
], caption: figure.caption(
position: bottom, 
[
Classement des 15 espèces les plus détectées
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sp2>


Le tableau complet, trié par volume décroissant, fournit pour chaque espèce son nom scientifique, son total de détections et la date de sa dernière observation. Ces informations permettent d'identifier des espèces migratrices de passage dont la dernière détection est ancienne et de suivre l'évolution de chaque taxon dans le temps.

#figure([
#box(image("images/dashboard/especes3.png"))
], caption: figure.caption(
position: bottom, 
[
Tableau exhaustif des espèces avec dates de dernière observation
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-sp3>


== 7.8. Analyse audio
<analyse-audio>
La page d'analyse audio permet d'importer un fichier audio (WAV, MP3, OGG ou FLAC, jusqu'à 200 Mo) et génère via librosa @librosa la forme d'onde temporelle, le spectrogramme Mel en décibels (128 bandes Mel, colormap #emph[magma];) et le spectrogramme log-fréquentiel par transformée de Fourier à court terme. Ces représentations sont utiles pour évaluer la qualité des enregistrements produits par les workers, notamment le rapport signal/bruit et la présence de parasites. Elles permettent aussi de comprendre visuellement les structures acoustiques que BirdNET analyse et d'expliquer pourquoi certaines détections obtiennent un score de confiance faible ou constituent des faux positifs liés à des sons environnementaux.

#figure([
#box(image("images/dashboard/audio1.png"))
], caption: figure.caption(
position: bottom, 
[
Interface d'import audio et outils de visualisation acoustique
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-audio1>


Après chargement d'un fichier, trois indicateurs sont affichés : la fréquence d'échantillonnage (44 100 Hz, conforme aux exigences de BirdNET), la durée (8,10 s, correspondant à un segment type produit par le worker) et le nombre d'échantillons (357 120). La forme d'onde temporelle représente l'amplitude en fonction du temps : le silence initial suivi de séquences de vocalisations distinctes, reconnaissables à leurs pics d'amplitude répétés entre 2 s et 7 s, est caractéristique d'un enregistrement de chant d'oiseau en milieu naturel.

#figure([
#box(image("images/dashboard/audio2.png"))
], caption: figure.caption(
position: bottom, 
[
Lecteur audio, indicateurs techniques et forme d'onde temporelle
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-audio2>


Le spectrogramme Mel représente l'énergie du signal en fonction du temps (axe X) et de la fréquence sur une échelle Mel (axe Y), l'intensité allant du bleu foncé (silence) au jaune (énergie maximale). Les vocalisations apparaissent sous forme de traits verticaux brillants concentrés entre 512 Hz et 4 096 Hz, plage typique des chants d'oiseaux chanteurs. Cette représentation est directement analogue à l'entrée que BirdNET traite, ce qui permet de comprendre visuellement sur quelle base le modèle effectue ses prédictions.

#figure([
#box(image("images/dashboard/audio3.png"))
], caption: figure.caption(
position: bottom, 
[
Spectrogramme Mel de l'enregistrement avec les vocalisations visibles
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-dash-audio3>


= 8. Performance et robustesse
<performance>
== 8.1. Exigences de performance
<exigences-de-performance>
L'analyse BirdNET doit s'effectuer en moins de 3 secondes par segment audio, et la transmission d'une détection à l'API en moins de 2 secondes (timeout réseau configuré à 5 secondes). La disponibilité globale du système doit atteindre au minimum 95 %, avec une capacité de traitement de 10 000 détections par jour. L'architecture est conçue pour supporter plus de 50 capteurs simultanés sans modification majeure.

== 8.2. Journalisation
<journalisation>
Chaque service enregistre les événements suivants : démarrage et arrêt, chaque détection identifiée avec l'espèce et le score de confiance, les erreurs d'analyse BirdNET, les échecs de transmission à l'API et les synchronisations hors-ligne. Les logs sont émis vers la sortie standard, collectés par Docker et conservés au minimum 30 jours.

== 8.3. Scalabilité
<scalabilité>
L'ajout d'un nouveau capteur requiert uniquement la création d'une clé d'API et la configuration des variables d'environnement du worker. L'API peut être répliquée horizontalement derrière un #emph[load balancer] sans modification de code, et le pool de connexions PostgreSQL est dimensionnable via la configuration.

= Conclusion
<conclusion>
Le projet URCABirds a permis de développer les deux composants fondamentaux d'un système de suivi automatisé des oiseaux : le service #emph[worker] embarqué sur Raspberry Pi, l'API REST centrale ainsi que le tableau de bord de visualisation.

Le #emph[worker] assure la capture audio, l'analyse ornithologique via BirdNET, la transmission sécurisée des données et la résilience en cas d'indisponibilité réseau. L'API REST offre un ensemble complet d'endpoints permettant l'ingestion, la consultation et l'agrégation des détections, avec des mécanismes d'authentification, de limitation de débit et de documentation automatique.

Le principal frein à la mise en service est la connectivité réseau sur le campus : le Wi-Fi de l'université n'est pas disponible sur tous les emplacements envisagés, et impose par ailleurs une ré-authentification manuelle quotidienne sur le portail captif, incompatible avec des capteurs autonomes. Nous attendons la livraison de puces 4G/5G qui permettront une connexion indépendante et continue. En attendant, des données simulées inspirées des positions géographiques réelles des futurs capteurs ont été intégrées pour permettre le développement et les tests du tableau de bord. Une fois les puces disponibles, le déploiement sur le campus pourra s'effectuer rapidement, le reste du système étant pleinement opérationnel. À terme, l'architecture permettra d'étendre le réseau à d'autres sites de l'URCA et de contribuer à un observatoire de la biodiversité aviaire à l'échelle régionale.

= Annexes
<annexes>
== A.1. Schéma SQL complet
<a.1.-schéma-sql-complet>
```sql
-- Clés d'API : une par worker/client
CREATE TABLE IF NOT EXISTS api_keys (
    id         SERIAL PRIMARY KEY,
    key        TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    admin      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Registre des capteurs
CREATE TABLE IF NOT EXISTS sensors (
    id               SERIAL PRIMARY KEY,
    sensor_id        TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    description      TEXT,
    api_key_id       INTEGER NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    first_registered TIMESTAMPTZ DEFAULT NOW(),
    last_connection  TIMESTAMPTZ DEFAULT NOW()
);

-- Détections : sensor_id est une FK -> sensors.id
CREATE TABLE IF NOT EXISTS detections (
    id         SERIAL PRIMARY KEY,
    sensor_id  INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp  TEXT NOT NULL,
    species    TEXT NOT NULL,
    confidence REAL NOT NULL
);
```

~

~

== A.2. Exemples de payloads API
<a.2.-exemples-de-payloads-api>
L'exemple ci-dessous illustre l'enregistrement d'un capteur via #strong[POST /v1/sensors/register] :

```json
{
  "sensor_id": "sensor-001",
  "name": "Capteur Nord",
  "latitude": 49.2386,
  "longitude": 4.0317,
  "description": "Arbre devant le bâtiment UFR Sciences"
}
```

La soumission d'une détection s'effectue via #strong[POST /v1/detections] :

```json
{
  "sensor_id": "sensor-001",
  "timestamp": "2026-05-13T08:42:00+00:00",
  "species": "Turdus merula",
  "confidence": 0.91
}
```

La réponse renvoyée par l'endpoint #strong[GET /v1/stats] contient les statistiques globales :

```json
{
  "success": true,
  "data": {
    "total_detections": 14823,
    "total_sensors": 3,
    "total_species": 27
  }
}
```

~

~

== A.3. Fichier de configuration (.env.example)
<a.3.-fichier-de-configuration-.env.example>
```bash
# Worker
API_URL=
API_KEY=
SENSOR_ID=
SENSOR_NAME=        # optionnel, défaut : SENSOR_ID
CONFIDENCE_THRESHOLD=
LATITUDE=
LONGITUDE=
LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR

# API
API_DOMAIN=

# PostgreSQL
POSTGRES_DATABASE=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
```

~

~

== A.4. Diagramme de séquence détaillé
<a.4.-diagramme-de-séquence-détaillé>
#strong[Initialisation du worker :]

#figure([
#box(image("figures/seq-init.png"))
], caption: figure.caption(
position: bottom, 
[
Diagramme de séquence - initialisation du worker
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-seq-init>


#strong[Boucle de détection :]

#figure([
#box(image("figures/seq-loop.png"))
], caption: figure.caption(
position: bottom, 
[
Diagramme de séquence - boucle de détection
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)
<fig-seq-loop>




 

#set bibliography(style: "style.csl")


#bibliography("refs.bib")
