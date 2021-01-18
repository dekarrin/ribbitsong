"use strict";

// note that narrative_X constraints do not require a citation as they imply
// where in the narrative they occur, which can be checked simply by reviewing
// the original work.

const ConstraintTypes = Object.freeze({
  NARRATIVE_IMMEDIATE:  Symbol("narrative_immediate"),
  NARRATIVE_JUMP:       Symbol("narrative_jump"),
  NARRATIVE_ENTRYPOINT: Symbol("narrative_entrypoint"),
  NARRATIVE_CAUSAL:     Symbol("narrative_causal"),
  ABSOLUTE:             Symbol("absolute"),
  RELATIVE:             Symbol("relative"),
  CAUSAL:               Symbol("causal"),
  SYNC:                 Symbol("sync"),
});

/*
* Holds info on how to place an event. This is used by the layout subsystem to
* satisfy when events occur.
*/
class Constraint {
  constructor(type) {
    this.type = type;
  }

  copy() {
    return new Error("not implemented");
  }
};

// The constraint implies an exact time. The precision of the time could vary.
// This constraint requires a citation.
class AbsoluteConstraint extends Constraint {
  constructor(citation, time) {
    super(ConstraintTypes.ABSOLUTE);
    this.time = time;
    this.citation = citation;
  }

  copy() {
    return new AbsoluteConstraint
  }
};

// The event occurs some amount of time before or after a reference event.
// This constraint requires a citation.
class RelativeConstraint extends Constraint {
  constructor(citation, refEvent, distance, isAfter=true) {
    super(ConstraintTypes.RELATIVE);
    this.citation = citation;
    this.refEvent = parseInt(refEvent, 10);
    this.isAFter = !!isAfter;
    this.distance = distance;
  }
};

// The event occurs an unspecified amount of time before or after a reference
// event. This constraint requires a citation.
class CausalConstraint extends Constraint {
  constructor(citation, refEvent, isAfter=true) {
    super(ConstraintTypes.CAUSAL);
    this.time = time;
    this.citation = citation;
  }
};

// The event is synch-locked with another event. Two events from the same
// timeline that are synch-locked to two points on another timeline can safely
// infer that the amount of time between the first pair must be the same as
// the second pair. This constraint requires a citation.
//
// This constraint type is pretty much only ever used for viewport
// connections, such as exile terminals or trollian use. DO NOT use this for
// two sides of the same conversation in pesterchat, etc; the two sides are
// considered the same event with two participants.
class SyncConstraint extends Constraint {
  constructor(citation, refEvent) {
    super(ConstraintTypes.SYNC);
    this.citation = citation;
    this.refEvent = refEvent;
  }
}

// The event is portrayed in the narrative immediately after/before a
// reference event.
class NarrativeImmediateConstraint extends Constraint {
  constructor(refEvent, isAfter=true) {
    super(ConstraintTypes.NARRATIVE_IMMEDIATE);

    this.refEvent = parseInt(refEvent, 10);
    this.isAfter = !!isAfter;
  }
}

// The event is portrayed in the narrative immediately after/before a
// reference event with a jumpcut, implying an ambiguous passage of time
// between the two.
class NarrativeJumpConstraint extends Constraint {
  constructor(refEvent, isAfter=true) {
    super(ConstraintTypes.NARRATIVE_JUMP);

    this.refEvent = parseInt(refEvent, 10);
    this.isAfter = !!isAfter;
  }
}

// A sequence of narrative events may have been skipped between the reference
// event and this event, but no jump cuts occured. Use this for when portrayed
// sequences are skipped in the data-gathering portion.
class NarrativeCausalConstraint extends Constraint {
  constructor(refEvent, isAfter=true) {
    super(ConstraintTypes.NARRATIVE_JUMP);

    this.refEvent = parseInt(refEvent, 10);
    this.isAfter = !!isAfter;
  }
}

// The event is portrayed with no reference as the starting point of the
// narrative or an arc that takes place in a timeline whose relation to any
// other is unclear, or if it does take place in a timeline but it is unclear
// how it relates to the rest of the timeline at that point in the narrative.
class NarrativeEntrypointConstraint extends Constraint {
  constructor() {
    super(ConstraintTypes.NARRATIVE_ENTRYPOINT);
  }
}

function paramCheck
