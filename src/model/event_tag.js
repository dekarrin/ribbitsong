"use strict";

const EventTagTypes = Object.freeze({
  CHAR_OBTAINS_ITEM:  Symbol("char_obtains_item"),
  CHAR_DROPS_ITEM: Symbol("char_drops_item"),
  CHAR_USES_ITEM: Symbol("char_uses_item"),
  CHAR_GIVES_ITEM_TO_CHAR: Symbol("char_gives_item_to_char"),
  APPEARANCE_IS_CHANGED: Symbol("appearance_is_changed"),
  STATE_IS_CHANGED: Symbol("state_is_changed"),
  CHAR_DIES: Symbol("char_dies"),
  CHAR_IS_BORN: Symbol("char_is_born"),
  CHAR_RESURRECTS: Symbol("char_resurrects"),
  CHAR_PORTS_OUT: Symbol("char_ports_out"),
  CHAR_PORTS_IN: Symbol("char_ports_in"),
  CHAR_ENTERS_LOCATION: Symbol("char_enters_location"),
  CHAR_EXITS_LOCATION: Symbol("char_exits_location"),
  CHAR_FALLS_ASLEEP: Symbol("char_falls_asleep"),
  CHAR_WAKES_UP: Symbol("char_wakes_up"),
});

// EventTag is the base type used for putting special 'tags' on events that are
// used to trace the position, appearance, and status of characters, items, and
// locations.
class EventTag {
  constructor(type) {
    this.type = type;
  }
}

/**
 * A tag for an event that indicates that a character adds an item to their
 * inventory. The item will no longer be considered in the previous location
 * and will remain in inventory until a later event tag indicates its removal.
 */
class CharObtainsItemEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeID} char - The ID of the character receiving the item.
   * @param {TimeID} item - The ID of the item being received.
   */
  constructor(char, item) {
    super(EventTagTypes.CHAR_OBTAINS_ITEM);
    this.character = char;
    this.item = item;
  }
}

/**
 * A tag for an event that indicates that a character puts an item from their
 * inventory into their current location. The item will be considered in the
 * previous location and will remain there until a later event tag indicates its
 * removal.
 */
class CharDropsItemEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The ID of the character dropping the item.
   * @param {TimeIDRef} item - The ID of the item being dropped.
   */
  constructor(char, item) {
    super(EventTagTypes.CHAR_DROPS_ITEM);
    this.character = char;
    this.item = item;
  }
}

/**
 * A tag for an event that indicates that a character used an item either in
 * their inventory or present in the current location.
 */
class CharUsesItemEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The ID of the character dropping the item.
   * @param {TimeIDRef} item - The ID of the item being used.
   * @param {boolean} consumed - Whether the item is destroyed after use.
   */
  constructor(char, item, consumed) {
    super(EventTagTypes.CHAR_USES_ITEM);
    this.character = char;
    this.item = item;
    this.consumed = consumed;
  }
}

/**
 * A tag for an event that indicates that a character gives an item in their
 * inventory to another character.
 */
class CharGivesItemEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} giver - The ID of the character giving the item.
   * @param {TimeIDRef} item - The ID of the item.
   * @param {TimeIDRef} receiver - The ID of the character receiving the item.
   */
  constructor(giver, item, receiver) {
    super(EventTagTypes.CHAR_GIVES_ITEM_TO_CHAR);
    this.giver = giver;
    this.receiver = receiver;
    this.item = item;
  }
}

/**
 * A tag for an event that indicates that an item, tag, or location appearance is
 * changed.
 */
class AppearanceChangeEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} recipient - Whose appearance is being changed. This will be
   * either a location, item, or character.
   * @param {string} appearance - The name for the appearance that the entity
   * switches to.
   */
  constructor(recipient, appearance) {
    super(EventTagTypes.APPEARANCE_IS_CHANGED);
    this.recipient = recipient;
    this.appearance = appearance;
  }
}

/**
 * A tag for an event that indicates that an item, tag, or location state is
 * changed.
 *
 * Note that this does not include character death or character porting out;
 * those are both special properties on the character that have their own
 * event tags. It also does not include appearance changes; use
 * AppearanceChangeEventTag for that.
 */
class StateChangeEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} recipient - Whose state is being changed. This will be
   * either a location, item, or character.
   * @param {string} prop - The property to be changed.
   * @param {*} val - The new value of the property.
   */
  constructor(recipient, prop, val) {
    super(EventTagTypes.STATE_IS_CHANGED);
    this.recipient = recipient;
    this.property = prop;
    this.value = val;
  }
}

/**
 * A tag for an event that indicates that a character dies. This does not
 * necessarily indicate that they are no longer able to participate.
 *
 * This often comes along with a character location change to afterlife.
 */
class CharDiesEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who dies.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_DIES);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character comes to life for the
 * first time. Their age starts at 0 and begins counting up from this point.
 */
class CharIsBornEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who is born.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_IS_BORN);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character comes back to life after
 * dying.
 */
class CharResurrectsEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who comes back to life.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_RESURRECTS);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character has exited the scene via
 * instantaneous means, that is, they are suddenly and completely gone. This
 * could be due to teleport, time travel, travel via fourth wall, or any other
 * similar situation.
 */
class CharPortsOutEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who is porting out.
   * @param {?UUID4} portInEvent - The reference to the event where the character
   * ports in from this port out. This can be null if it isn't currently known.
   */
  constructor(char, portInEvent = null) {
    super(EventTagTypes.CHAR_PORTS_OUT);
    this.character = char;
    this.portInEvent = portInEvent
  }
}

/**
 * A tag for an event that indicates that a character has entered the scene via
 * instantaneous means, that is, they are suddenly and completely gone. This
 * could be due to teleport, time travel, travel via fourth wall, or any other
 * similar situation.
 */
class CharPortsInEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who is porting in.
   * @param {?UUID4} portOutEvent - The reference to the event where the
   * character ported out from to get to this event. This can be null if it
   * isn't currently known.
   */
  constructor(char, portOutEvent = null) {
    super(EventTagTypes.CHAR_PORTS_IN);
    this.character = char;
    this.portOutEvent = portOutEvent
  }
}

/**
 * A tag for an event that indicates that a character has entered the scene via
 * conventional means; that is, not via any kind of teleport, time travel,
 * powered-window travel, or any other thing that could be called "shenanigans".
 */
class CharEntersEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who is entering.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_ENTERS_LOCATION);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character has exited the scene via
 * conventional means; that is, not via any kind of teleport, time travel,
 * powered-window travel, or any other thing that could be called "shenanigans".
 */
class CharExitsEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who is exiting.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_EXITS_LOCATION);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character has fallen asleep.
 */
class CharFallsAsleepEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who falls asleep.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_FALLS_ASLEEP);
    this.character = char;
  }
}

/**
 * A tag for an event that indicates that a character has woken up.
 */
class CharWakesUpEventTag extends EventTag {

  /**
   * Create instance.
   * @param {TimeIDRef} char - The character who wakes up.
   */
  constructor(char) {
    super(EventTagTypes.CHAR_WAKES_UP);
    this.character = char;
  }
}
