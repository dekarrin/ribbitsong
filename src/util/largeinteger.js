"use strict";

/**
 * Radix that numbers are represented with internally in a LargeInteger.
 *
 * In order to allow assumptions to hold, InternalRadix ^ 2 needs to be
 * holdable in memory. 2^26 was chosen as 2^52 is still within the safe limits
 * of integers in javascript.
 */
const InternalRadix = Math.pow(2, 26);

const Zero = new LargeInteger(0);

/**
 * This is needed because we need to represent times up to and including
 * hundreds of millions of years in magnitude with milliseconds, and oridinarily
 * the precision in JS will only get us up to about 10s of million of years of
 * range at that precision.
 *
 * Internally all numbers are represented as base 2^32 to stay within safe
 * range of max int.
 *
 * Two properties define a large integer -
 *  `mag` is the magnitude of the number and is the little-endian digits in
 *  base InternalRadix of the number. More are added as needed.
 *  For zero, this is empty.
 *  `signum` is the sign of it and will be -1 for negative numbers, 1 for
 *  positive numbers, and 0 for zero.
 */
class LargeInteger {

  /**
   * Create a new LargeInteger.
   *
   * @param {?(number|string|LargeInteger)} num The number to create the
   * LargeInteger from. If it is a number, it is converted directly to
   * LargeInteger representation. If it is a string, the string is parsed as a
   * base-10 decimal integer and a LargeInteger representing it is returned. If
   * it is a LargeInteger, the LargeInteger is copied. If not given or null,
   * a LargeInteger representing 0 is returned.
   */
  constructor(num = null) {
    this.signum = 0;
    this.mag = [];  // always in little endian.
    if (num !== null) {
      if (num instanceof LargeInteger) {
        this.signum = num.signum;
        for (let m of num.mag) {
          this.mag.push(m);
        }
      } else if (typeof(num) === 'number' || num instanceof Number) {
        if (num === 0) {
          return;
        }
        if (!Number.isFinite(num) || Number.isNaN(num)) {
          throw new TypeError("number must be finite and exist");
        }

        // just toss it on the front and let our carry procedure deal with it
        this.mag.push(num);
        LargeInteger.carry(this.mag, InternalRadix);
      } else {
        // assume it is a string, try to parse as base 10.
        let str = num.toString();
        let parsed = new LargeInteger.parse(str, 10);
        this.signum = parsed.signum;
        for (let m of parsed.mag) {
          this.mag.push(m);
        }
      }
    }
  }

  /**
   * Get a LargeInteger that has the same value as this one, negated.
   */
  negate() {
    let c = copy();
    if (this.signum !== 0) {
      c.signum *= -1;
    }
    return c;
  }

  /**
   * Multiply the value of this LargeInteger by another operand.
   *
   * @param {?(number|string|LargeInteger)} b The term to multiply this one by.
   * @return {LargeInteger} The large integer that is the result of multiplying
   * the value in this one by the operand.
   */
  times(b) {
    if (b === null) {
      return this.copy();
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (b.signum === 0) {
      return b.copy();
    } else if (this.signum === 0) {
      return this.copy();
    }

    if (this.signum !== b.signum) {
      return this.minus(b.negate());
    }

    let result = new LargeInteger(0);  // don't use Zero because we're about to modify

    for (let i = 0; i < b.mag.length; i++) {
      for (let j = 0; j < this.mag.length; j++) {
        if (i+j >= result.mag.length) {
          result.mag.push(0);
        }
        result.mag[i+j] += this.mag[j] * b.mag[i];
      }
      // do a carry now to prevent overflow
      LargeInteger.carry(result.mag, InternalRadix);
    }

    result.signum = 1;
    if (this.signum !== b.signum) {
      result.signum = -1;
    }
    return result;
  }

  /**
   * Add the value of two numbers together. The original LargeInteger is not
   * changed.
   *
   * @param {?(number|string|LargeInteger)} b The other term to be added to this
   * one.
   * @return {LargeInteger} The large integer that is the sum of both this
   * large integer and the value represented by b.
   */
  plus(b) {
    if (b === null) {
      return this.copy();
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (b.signum === 0) {
      return this.copy();
    } else if (this.signum === 0) {
      return b.copy();
    }

    if (this.signum !== b.signum) {
      return this.minus(b.negate());
    }

    let result = this.copy();
    for (let i = 0; i < b.mag.length; i++) {
      if (i >= result.mag.length) {
        result.mag.push(0);
      }
      result.mag[i] += b.mag[i];
    }

    LargeInteger.carry(result.mag, InternalRadix);
    return result;
  }

  /**
   * Subtract the value of b from the value in this Large Integer. The original
   * LargeInteger is not changed.
   *
   * @param {?(number|string|LargeInteger)} b The term to be subtracted from
   * this one.
   * @return {LargeInteger} The large integer that is the subtraction of b from
   * this.
   */
  minus(b) {
    if (b === null) {
      return this.copy();
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (b.signum === 0) {
      return this.copy();
    } else if (this.signum === 0) {
      return b.negate();
    }

    if (this.signum !== b.signum) {
      return this.plus(b.negate());
    }

    let result = this.copy();

    for (let i = 0; i < b.mag.length; i++) {
      if (i >= result.mag.length) {
        result.mag.push(0);
      }
      result.mag[i] -= b.mag[i];
    }

    let swapSign = new LargeInteger.borrow(result.mag, InternalRadix);
    if (swapSign) {
      result.signum *= 1;
    }
    if (result.mag.length === 0) {
      result.signum = 0;
    }

    return result;
  }

  /**
   * Check if this is equal to a reference value. If the reference value is not
   * converatble to a LargeInteger, returns false.
   *
   * @param {?(number|string|LargeInteger)} b The term to see if equal to.
   * @return {boolean} Whether it is equal.
   */
  equals(b) {
    if (b === null) {
      return b;
    }

    if (!(b instanceof LargeInteger)) {
      try {
        b = new LargeInteger(b);
      } catch (e) {
        return false;
      }
    }

    if (b.mag.length !== this.mag.length) {
      return false;
    }
    for (let i = 0; i < this.mag.length; i++) {
      if (b.mag[i] != this.mag[i]) {
        return false;
      }
    }
    return true;
  }

  /**
   * Check if this is strictly greater than a reference value. If the reference
   * value is not converatble to a LargeInteger, throws an exception.
   *
   * @param {?(number|string|LargeInteger)} b The term to see if greater than.
   * @return {boolean} Whether it is greater than the value.
   */
  greaterThan(b) {
    if (b === null) {
      return b;
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (this.mag.length < b.mag.length) {
      return false;
    }
    if (this.mag.length > b.mag.length) {
      return true;
    }

    for (let i = this.mag.length - 1; i >= 0; i--) {
      if (b.mag[i] > this.mag[i]) {
        return false;
      }
      if (b.mag[i] < this.mag[i]) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check if this is greater than or equal to a reference value. If the
   * reference value is not converatble to a LargeInteger, throws an exception.
   *
   * @param {?(number|string|LargeInteger)} b The term to see if greater than.
   * @return {boolean} Whether it is greater than or equal to the value.
   */
  greaterThanEquals(b) {
    if (b === null) {
      return b;
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (this.mag.length < b.mag.length) {
      return false;
    }
    if (this.mag.length > b.mag.length) {
      return true;
    }

    for (let i = this.mag.length - 1; i >= 0; i--) {
      if (b.mag[i] > this.mag[i]) {
        return false;
      }
      if (b.mag[i] < this.mag[i]) {
        return true;
      }
    }
    return true;
  }

  /**
   * Check if this is strictly less than a reference value. If the reference
   * value is not converatble to a LargeInteger, throws an exception.
   *
   * @param {?(number|string|LargeInteger)} b The term to see if less than.
   * @return {boolean} Whether it is less than the value.
   */
  lessThan(b) {
    if (b === null) {
      return b;
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (this.mag.length < b.mag.length) {
      return true;
    }
    if (this.mag.length > b.mag.length) {
      return false;
    }

    for (let i = this.mag.length - 1; i >= 0; i--) {
      if (b.mag[i] < this.mag[i]) {
        return false;
      }
      if (b.mag[i] > this.mag[i]) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check if this is less than or equal to a reference value. If the reference
   * value is not converatble to a LargeInteger, throws an exception.
   *
   * @param {?(number|string|LargeInteger)} b The term to see if less than.
   * @return {boolean} Whether it is less than or equal to the value.
   */
  lessThanEquals(b) {
    if (b === null) {
      return b;
    }

    if (!(b instanceof LargeInteger)) {
      b = new LargeInteger(b);
    }

    if (this.mag.length < b.mag.length) {
      return true;
    }
    if (this.mag.length > b.mag.length) {
      return false;
    }

    for (let i = this.mag.length - 1; i >= 0; i--) {
      if (b.mag[i] < this.mag[i]) {
        return false;
      }
      if (b.mag[i] > this.mag[i]) {
        return true;
      }
    }
    return true;
  }

  toString(radix=10) {
    let str = "";
    if (this.signum === 0) {
      return "0";
    } else if (this.signum === -1) {
      str += '-';
    }

    let convMag = [];

    for (let place = this.mag.length - 1; place >= 0; place--) {
      let digit = this.mag[place];

      let digitValueRepr = [digit];

      // ensure the first placement is properly carried
      LargeInteger.carry(digitValueRepr, radix);

      // now exponentiate the value by conversion base, but do each
      // multiplication individually so we check carries with each
      // multiplication and don't encounter an overflow even when going to much
      // lower bases
      for (let i = 0; i < place; i++) {
        // need to do multiplication to each digit
        for (let j = 0; j < digitValueRepr.length; j++) {
          digitValueRepr[j] *= InternalRadix;
        }
        LargeInteger.carry(digitValueRepr, radix);
      }

      // digitValueRepr now has complete value representation for the digit,
      // properly carried. Add it to the results magnitude.
      for (let i = 0; i < digitValueRepr.length; i++) {
        if (i >= convMag.length) {
          convMag.push(0);
        }
        convMag[i] += digitValueRepr[i];
      }

      // apply the carry to the results now that we are done
      LargeInteger.carry(convMag, radix);
    }

    // go through converted mag and build up the final string
    for (let place = convMag.length - 1; place >= 0; place--) {
      let ch = convMag[place].toString(radix);
      str += ch;
    }

    return str;
  }

  /**
   * Parse a large integer from a string in the given radix.
   *
   * Throws an error if the string does not contain a parsable number.
   *
   * @param {string} str The string to parse.
   * @param {number} radix The radix to parse in.
   * @return {LargeInteger} The parsed large integer.
   */
  static parse(str, radix) {
    if (radix < 2 || radix > 36) {
      throw new RangeError(`radix outside of allowed range [2, 36]: ${radix}`);
    }

    let parseStr = str.toString();
    let cursor = 0;

    // check for at most one leading sign
    let sign = 1;
    let minusIdx = parseStr.lastIndexOf("-");
    let plusIdx = parseStr.lastIndexOf("+");
    if (minusIdx >= 0) {
      if (minusIdx > 0 || plusIdx >= 0) {
        throw new TypeError(`illegal sign character after start`);
      }
      sign = -1;
      cursor = 1;
    } else if (plusIdx >= 0) {
      if (plusIdx != 0) {
        throw new TypeError(`illegal sign character after start`);
      }
      cursor = 1;
    }
    if (cursor === parseStr.length) {
      throw new TypeError(`empty number`);
    }

    // skip leading zeros and compute number of digits in magnitude
    while (cursor < parseStr.length && parseInt(parseStr.charAt(cursor), radix) === 0) {
      cursor++;
    }

    let largeInt = new LargeInteger(0);
    if (cursor === parseStr.length) {
      return largeInt;
    }

    largeInt.signum = sign;
    while (cursor < parseStr.length) {
      let digit = parseInt(parseStr.charAt(cursor), radix);
      if (Number.isNaN(digit)) {
        throw new TypeError(`contains illegal character not of radix ${radix}`)
      }
      let place = parseStr.length - cursor - 1;

      let digitValueRepr = [digit];

      // shouldnt ever be a case where this is needed but do it just in case
      // shouldn't be needed bc max allowed parse radix is far lower than
      // internal representation radix.
      LargeInteger.carry(digitValueRepr, InternalRadix);

      // now exponentiate the value by parse base, but do each multiplication
      // individually so we check carries with each multiplication and don't
      // encounter an overflow even on parse strings where the most significant
      // digit gives something well outside of the range of a normal safe int.
      for (let i = 0; i < place; i++) {
        // need to do multiplication to each digit
        for (let j = 0; j < digitValueRepr.length; j++) {
          digitValueRepr[j] *= radix;
        }
        LargeInteger.carry(digitValueRepr, InternalRadix);
      }

      // digitValueRepr now has complete value representation for the digit,
      // properly carried. Add it to the LargeInteger we are parsing.
      for (let i = 0; i < digitValueRepr.length; i++) {
        if (i >= largeInt.mag.length) {
          largeInt.mag.push(0);
        }
        largeInt.mag[i] += digitValueRepr[i];
      }

      // apply the carry to the largInteger now that we are done
      LargeInteger.carry(largeInt.mag, InternalRadix);

      cursor++;
    }

    return largeInt;
  }

  /**
   * Perform carry operation on magnitude digits if needed. This will modify the
   * original array.
   * @param {number[]} mag Representation of the number's magnitude.
   * @param {number} radix Radix that the digits of the magnitude are in.
   */
  static carry(mag, radix) {
    if (mag.length === 0) {
      return mag;
    }

    for (let i = 0; i < mag.length; i++) {
      let carryAmt = 0;
      while (mag[i] >= radix) {
        mag[i] -= radix;
        carryAmt++;
      }
      if (carryAmt > 0) {
        if (i + 1 >= mag.length) {
          mag.push(0);
        }
        mag[i+1] += carryAmt;
      }
    }
  }


  /**
   * Perform borrow operation on magnitude digits if needed. This will modify the
   * original array. It is possible that a sign switch is needed to complete
   * the borrow due to the magnitude remaining negative after the
   * operation completes. In this case, the magnitude will be switched to
   * positive and a value of true will be returned to indicate that a sign
   * switch occured.
   *
   * @param {number[]} mag Representation of the number's magnitude.
   * @param {number} radix Radix that the digits of the magnitude are in.
   *
   * @return {boolean} Whether a sign switch occured during the borrow.
   */
  static borrow(mag, radix) {
    if (mag.length === 0) {
      return mag;
    }

    let signSwitch = false;

    // reverse iteration to do in order of msd.
    // unclear if this is actually better since borrow_from_prev algorithm is
    // recursive anyways but seems like it would be better to standardize from
    // most-significant
    //
    // start iteration from mag.length - 2 instead of -1 because we cannot do
    // anything for the most significant digit and we just end up with a check
    // to make sure we don't do anything on first iteration anyways
    for (let i = mag.length - 2; i >= 0; i--) {
      if (mag[i] < 0) {
        // borrow_from_prev algorithm:
        for (let j = i + 1; j < mag.length; j++) {
          mag[j] -= 1;
          if (mag[j] >= 0) {
            // no need to keep borrowing from prev
            break;
          }
        }

        // since borrow_from_prev completed, we now have `radix` more to add
        // to fix negation
        mag[i] += radix;
      }
    }

    // strip all non-significant leading zeros:
    for (let i = mag.length - 1; i >= 0 && mag[i] === 0; i--) {
      mag.pop();
    }

    // borrow check for all digits but most significant are complete.
    // if the MSD is currently negative, it has nothing to borrow from; to keep
    // it as a magnitude, set it to abs but indicate that it switched sign in
    // the return value
    if (mag[mag.length - 1] < 0) {
      mag[mag.length - 1] *= -1;
      return true;
    }
    return false;
  }

  copy() {
    if (this.signum === 0) {
      return Zero;
    }
    return LargeInteger(this);
  }
}
