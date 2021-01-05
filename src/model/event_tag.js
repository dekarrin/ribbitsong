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
