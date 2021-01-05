"use strict";

// NOTE: we use 'canon' in descriptions as its typical definition outside of
// the Homestuck community. We expclicitly do not refer to Rose's epilogue
// description of canonicity including the pillars of truth, relevance, and
// essentiality.

const OfficialWorks = Object.freeze({
  MAIN: {
    title: "Homestuck",
    description: "Primary comic of homestuck. Definitive source of canon.",
    link: "https://www.homestuck.com",
    referencePattern: "https://www.homestuck.com/story/<PANEL>"
  },
  EPILOGUES: {
    title: "The Homestuck Epilogues",
    description: "Set of post-comic events regarded by many as non-canonical.",
    link: "https://www.homestuck.com/epilogues",
    refPattern: "https://www.homestuck.com/epilogues/<BRANCH>/<PANEL>"
  },
  SEQUEL: {
    title: "Homestuck^2: Beyond Canon",
    description: "Sequel comic to Homestuck that is regarded by many as non-canonical.",
    link: "https://www.homestuck2.com",
    refPattern: "https://www.homestuck2.com/story/<PANEL>"
  },
  MAIN_PRINT: {
    title: "Homestuck (Viz Media Hardcover Print)",
    description: "Main comic, but printed in several volumes. Has author commentary on nearly every page.",
    link: "https://www.viz.com/homestuck",
    refPattern: null,
  },
)

const CitationTypes = Object.freeze({
  WORK_DIALOGUE:      Symbol("work_dialogue"),
  WORK_NARRATION:     Symbol("work_narration"),
  WORK_MEDIA:         Symbol("work_media"),
  PRINT_COMMENTARY:   Symbol("print_commentary"),
)

// Used for giving reference for event's existence or placement constraint on
// an event.
class Citation {
  constructor(type) {
    this.type = type;
  }
};

// Refers to the dialogue (pesterlog, dialoglog, etc).
class WorkDialogueCitation extends Citation {
  constructor(work, panel, character, line) {
    super(CitationTypes.WORK_DIALOGUE);
    this.work = work;
    this.panel = parseInt(panel, 10);
    this.character = character;
    this.line = parseInt(line, 10);
  }
}

// Refers to non-dialog text on a panel/page.
class WorkNarrationCitation extends Citation {
  constructor(work, panel, paragraph, sentence) {
    this.work = work;
    this.panel = parseInt(panel, 10);
    this.paragraph = parseInt(paragraph, 10);
    this.sentence = parseInt(sentence, 10);
  }
}

WORK_DIALOGUE (work, panel, character, line)
WORK_NARRATION (work, panel, paragraph, sentence)
WORK_MEDIA (work, panel, timestamp)
PRINT_COMMENTARY (work, volume, page)
