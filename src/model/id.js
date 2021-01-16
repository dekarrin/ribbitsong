/**
 * Module for IDs and ID generation.
 * @module model/id
 */

const canonicalUUIDRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/**
 * A v4 UUID.
 * @todo This relies on Math.random, a poor source of entropy. Update this to use actual uuid module in future.
 */
class UUID4 {

  /**
   * Create a new v4 UUID from the given representation.
   *
   * @param {?(string|number[])} representation Either the 32-character separated
   * string representing the UUID, or an array with the 16 bytes. If null or
   * not given, a nil UUID is generated.
   */
  constructor(representation = null) {
    this.bytes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    if (representation) {
      if (Array.isArray(representation)) {
        for (let i = 0; i < 16 && i < representation.length; i++) {
          let b = representation[i];
          if (b < 0 || b > 255) {
            throw TypeError(`representation[${i}] out of bounds [0, 255]: ${b}`);
          }
          this.bytes[i] = representation[i];
        }
      } else {
        // representation is a string. Make sure it matches the correct format
        // before parsing
        const reprStr = represenation.toLowerCase();

        if (!canonicalUUIDRegex.test(reprStr)) {
          throw TypeError(`not a canonical representation of v4 UUID: ${representation}`);
        }

        // digits will contain only the digits and is exactly 32 chars long
        const digits = reprStr.replaceAll('-', '');

        for (let i = 0; i < digits.length; i += 2) {
          const idx = Math.floor(i/2);
          const b = parseInt(digits.slice(i, i+2), 16);
          this.bytes[idx] = b;
        }
      }
    }

    /**
     * Get canonical representation of this UUID.
     */
    toString() {
      let str = "";
      for (let i = 0; i < this.bytes.length; i++) {
        let b = this.bytes[i];
        let leftDigit = b & 0xf0;
        let rightDigit = b & 0x0f;
        str += leftDigit.toString(16) + rightDigit.toString(16);
        if (i == 3 || i == 5 || i == 7 || i == 9) {
          str += '-';
        }
      }
    }

    /**
     * Generate a new UUID.
     * @todo This relies on Math.random, a poor source of entropy. Update this to use actual uuid module in future.
     * @returns {string} A new UUID.
     */
    static generate() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
       var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
       return v.toString(16);
      });
    }
  }

}



/**
 * ID for handling unique identifiers that incorporate the concept
 * of time to distinguish between the same entity meeting with one older due to
 * time travel.
 */
class TimeID {

  /**
   * Create new TimeID.
   * @param {UUID4} uuid The UUID of the ID. This will not change.
   * @param {number} age The current age in whatever unit makes sense.
   */
  constructor(uuid, age) {
    this.uuid = uuid;
    this.age = age;
  }

  /**
   * Get a copy of this ID with the age decremented. This TimeID is not changed.
   * @param {number} amount The amount to decrement by.
   * @return {TimeID} A copy of this ID with age decremented by the given amount.
   */
  decremented(amount = 1) {
    return TimeID(this.uuid, this.age - amount)
  }

  /**
   * Get a copy of this ID with the age incremented. This TimeID is not changed.
   * @param {number} amount The amount to increment by.
   * @return {TimeID} A copy of this ID with age incremented by the given amount.
   */
  incremented(amount = 1) {
    return TimeID(this.uuid, this.age + amount)
  }

  /**
   * Selects the oldest of multiple time IDs.
   * @param {TimeID[]} timeIds The IDs to select from.
   * @return {TimeID} The TimeID with the largest age.
   */
  static oldestOf(timeIds) {
    if (timeIds.length < 1) {
      return null;
    }

    let oldest = timeIds[0];
    for (const tid of timeIds) {
      if (tid.age > oldest.age) {
        oldest = tid;
      }
    }

    return oldest;
  }

  /**
   * Selects the youngest of multiple time IDs.
   * @param {TimeID[]} timeIds The IDs to select from.
   * @return {TimeID} The TimeID with the smallest age.
   */
  static youngestOf(timeIds) {
    if (timeIds.length < 1) {
      return null;
    }

    let youngest = timeIds[0];
    for (const tid of timeIds) {
      if (tid.age < youngest.age) {
        youngest = tid;
      }
    }

    return youngest;
  }

}
