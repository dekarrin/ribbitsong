/**
 * We implement our own time classes here because paradox space does not follow
 * the same rules as IRL. This is usually not recommended, but for paradox
 * space, time changes and quanta are surprisingly well-defined in comparison to
 * IRL circumstances.
 *
 * 1 second is always exactly 1000 milliseconds.
 * 1 minute is always exactly 60 seconds (60000 ms).
 * 1 hour is always exactly 60 minutes ()
 *
 * @module model/timerange
 */

class PreciseTime {

  /**
   * Create a new instance that specifies an exact moment in time.
   *
   * @param {number} ms The number of milliseconds in total.
   * @param {number} precision The number that the given milliseconds should be
   * considered to vary by; for instance, for precision to the second, 1000
   * would be given. If 0, it is an exact millisecond precision and does not
   * vary at all.
   */
  constructor(ms, precision) {
    this.ms = ms;
    this.precision = precision;
  }

  /**
   * Gets the total number of seconds represented by this time. This can be a
   * non-integer value.
   *
   * @return {number}
   */
  get seconds() {
    return this.ms / 1000;
  }

  /**
   * Gets the total number of minutes represented by this time. This can be a
   * non-integer value.
   *
   * @return {number}
   */
  get minutes() {
    return this.ms / (1000 * 60);
  }

  /**
   * Gets the total number of hours represented by this time. This can be a
   * non-integer value.
   *
   * @return {number}
   */
  get hours() {
    return this.ms / (1000 * 60 * 60);
  }

  /**
   * Gets the total number of hours represented by this time. This can be a
   * non-integer value.
   *
   * @return {number}
   */
  get hours() {
    return this.ms / (1000 * 60 * 60);
  }
}
