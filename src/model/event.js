"use strict";

/**
 * An event on the timeline. Instances are created with only info about what
 * happens in them rather than when they occur; they can then have placement
 * constraints placed on them which are used by the layout engine to determine
 * a time for when they exist, but they rarely know themselves exactly when
 * they occur.
 *
 * All events are assumed to have near-instantaneous time to start and finish.
 * If this assumption causes issues, a long-running event X should be split into
 * a pair of "X-starts" and "X-completes" events.
 */
class Event {

  const data = {
    universes: {
      'human-pre-scratch': {
        '/accelerate[Y]': {
          '/lohac/magmacore': {
            characters: [
              "dave-strider",
              "rose-lalonde"
            ],
            items: [
              "ugh"
            ]
          }
        },
          '/accelerate[N]'
        }
      }
    }
  }

  /**
   * Create a new event. All properties used for layout will be set to default
   * values; to use those values, use further methods to modify the event.
   *
   * @param {string} desc - The description of what occurs in the event. This
   * can be in-depth as needed.
   * @param {?string} name - What to use as a name for the event. If none given,
   * the first sentence in desc will be used.
   */
  constructor(desc, name = null) {
    this.description = desc;
    this.name = desc.split(".", 1)[0]
    if (name !== null) {
      this.name = name;
    }

    this.universes = {};
    this.citations = [];
    this.tags = [];
    this.constraints = [];
    this.portrayedIn = null;
  }

  /**
   * Get an Event that is an exact copy of this one.
   *
   * @return {Event} A copy of this Event.
   */
  copy() {
    let universesCopy = {};
    for (let univName in this.universes) {
      let univ = this.universes[univName];
      let univCopy = {};
      for (let tName in univ) {
        let timeline = univ[tName];
        let timelineCopy = {};
        for (let locName in timeline) {
          let loc = timeline[locName];
          let locCopy = {
            'characters': [],
            'items': [],
          };

          for (let ch of loc['characters']) {
            locCopy['characters'].push(ch);
          }
          for (let ch of loc['items']) {
            locCopy['items'].push(ch);
          }

          timelineCopy[locName] = locCopy;
        }
        univCopy[tName] = timelineCopy;
      }
      universesCopy[univName] = univCopy;
    }

    let e = new Event(this.description, this.name);
    return e;
  }

  /**
   * Get an Event with the given universe added to its list of universes. This
   * does not modify the original Event.
   *
   * @param {string} universe - The universe to be added.
   * @return {Event} A new event with the given universe added.
   */
  withUniverseAdded(universe) {
    let e = new Event(this.description, this.name);

  }
}
