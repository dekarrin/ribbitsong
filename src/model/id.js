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

/**
 * A reference to a TimeID. Can be one of multiple levels of specifity.
 */
class TimeIDRef {

  /**
   * Create a reference to a TimeID. The returned TimeID is non-generic and will
   * only resolve in a situation where only one TimeID of that UUID exists; to
   * get more specific, convert the returned ID to a different comparison using
   * toExactAge, toYoungest, or toOldest.
   * @param {UUID4} uuid - The UUID of the TimeID.
   */
  constructor(uuid) {
    this.uuid = uuid;
    this.comparison = null;
    this.target = -1;
  }

  /**
   * Copy this TimeIDRef into a new one that refers to the TimeID with the same
   * UUID as this TimeIDRef and that has an exact age.
   *
   * This is usually not desired as the age is subject to change frequently. It
   * should generally only be used if an absolute age has been established; in
   * other cases, toYoungest or toOldest should be used to provide a reference
   * that relies on the relative ages between available TimeIDs of the desired
   * UUID instead of an exact one.
   *
   * @param {number} age - The age of the TimeID to specify.
   * @return {TimeIDRef}
   */
  toExactAge(age) {
    let ref = new TimeIDRef(this.uuid);
    ref.comparison = 'exact';
    ref.target = age;
    return ref;
  }

  /**
   * Copy this TimeIDRef into a new one that refers to the TimeID that has the
   * lowest age of all TimeIDs with the UUID in this TimeIDRef.
   *
   * The index can be used to provide more complicated criteria and is used as
   * the index of the TimeID that should be selected when all of the TimeIDs
   * with the UUID in the returned TimeIDRef are ordered by age, smallest to
   * largest. So keeping index at 0 will return the youngest, giving it as 1
   * will return the second youngest, etc.
   *
   * @param {number} index - Which youngest to get. 0 is youngest, 1 is
   * second-youngest, 2 is third-youngest, etc.
   * @return {TimeIDRef}
   */
  toYoungest(index = 0) {
    let ref = new TimeIDRef(this.uuid);
    ref.comparison = 'youngest';
    ref.target = index;
    return ref;
  }

  /**
   * Copy this TimeIDRef into a new one that refers to the TimeID that has the
   * highest age of all TimeIDs with the UUID in this TimeIDRef.
   *
   * The index can be used to provide more complicated criteria and is used as
   * the index of the TimeID that should be selected when all of the TimeIDs
   * with the UUID in the returned TimeIDRef are ordered by age, largest to
   * smallest. So keeping index at 0 will return the oldest, giving it as 1
   * will return the second oldest, etc.
   *
   * @param {number} index - Which oldest to get. 0 is oldest, 1 is
   * second-oldest, 2 is third-oldest, etc.
   * @return {TimeIDRef}
   */
  toOldest(index = 0) {
    let ref = new TimeIDRef(this.uuid);
    ref.comparison = 'oldest';
    ref.target = index;
    return ref;
  }
}
