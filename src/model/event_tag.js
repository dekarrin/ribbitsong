"use strict";

const EventTagTypes = Object.freeze({
  CHAR_OBTAINS_ITEM:  Symbol("char_obtains_item"),
  CHAR_DROPS_ITEM: Symbol("char_drops_item"),
  CHAR_USES_ITEM: Symbol("char_uses_item"),
  CHAR_CHANGES_APPEARANCE: Symbol("char_changes_appearance"),
  CHAR_GIVES_ITEM_TO_CHAR: Symbol("char_gives_item_to_char"),
  ITEM_STATE_IS_CHANGED: Symbol("item_state_is_changed"),
  LOCATION_STATE_IS_CHANGED: Symbol("location_state_is_changed"),
  CHAR_DIES: Symbol("char_dies"),
  CHAR_IS_BORN: Symbol("char_is_born"),
  CHAR_PORTS_OUT: Symbol("char_ports_out"),
  CHAR_PORTS_IN: Symbol("char_ports_out"),
  CHAR_ENTERS_LOCATION: Symbol("char_enters_location"),
  CHAR_LEAVES_LOCATION: Symbol("char_leaves_location"),
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

class CharDropsItemEventTag extends EventTag {
  constructor(char, item) {
    super(EventTagTypes.CHAR_DROPS_ITEM);
    this.character = char;
    this.item = item;
  }
}

class CharUsesItemEventTag extends EventTag {
  constructor(char, item, consumed) {
    super(EventTagTypes.CHAR_USES_ITEM);
    this.character = char;
    this.item = item;
    this.consumed = consumed;
  }
}
