const touchMap = new WeakMap(); // for debouncing non-async input
let timer = null; // for aync debouncing

const vuelidateMixin = {
  data() {
    return {
      debounceDefault: 400,
      errorMessages: {
        required: "This field is required",
        email: "Please check e-mail format",
        minLength: "Should contain between 8 and 24 characters",
        maxLength: "Should contain between 8 and 24 characters",
        sameAsCurrentPassword: "Your password is incorrect",
        sameAsPassword: "Confirmation Password does not match Password",
        notSameAsPassword: "New password is the same as the current one",
        passwordValid: "Password is incorrect",
        customPhoneFormat: "format: (555) 555-1212",
        zipCode: "Zip Code should be 5 or 9 digits",
        integer: "Should be a number",
        loginExists: "Login e-mail already exists",
        loginNotExists: "Login does not exist",
      },
    };
  },
  methods: {
    validateEmail(value) {
      return /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
        value
      );
    },
    asyncDebounce(func) {
      return new Promise((resolve, reject) => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
          func()
            .then((r) => resolve(r))
            .catch((e) => reject(e));
        }, this.debounceDefault);
      });
    },
    touchDebounce($vField) {
      $vField.$reset();
      if (touchMap.has($vField)) {
        clearTimeout(touchMap.get($vField));
      }
      touchMap.set($vField, setTimeout($vField.$touch, this.debounceDefault));
    },
    prevInvalid(fieldName, currentValidatorName = null, subkey = null) {
      // check if there are already non-passing validations on this field (excluding current validator)
      let hasInvalid = [];
      let validationObj = subkey && this.v$[subkey] ? this.v$[subkey] : this.v$;

      try {
        const checkValids = Object.keys(validationObj[fieldName]).filter(
          (v) => v !== currentValidatorName && !/^\$/.test(v)
        );
        hasInvalid = checkValids.filter((v) => !validationObj[fieldName][v]);
      } catch (e) {
        console.error("checkValids failed");
      }

      return hasInvalid.length ? true : false;
    },
    getFirstError(f) {
      let message = null;
      const errorObj = this.v$[f].$errors[0];
      if (!errorObj) return;
      const key = errorObj.$validator;
      const defaultMessage = errorObj.$message;

      if (key) {
        if (!message && this.customMessages && this.customMessages[key])
          message = this.customMessages[key];
        if (!message && this.errorMessages[key]) message = this.errorMessages[key];
        if (!message && defaultMessage) message = defaultMessage;
      }
      return message;
    },
    validationStyling(f) {
      if (!this.v$[f].$dirty) return;
      return this.v$[f].$invalid ? [CFG.fieldInvalid] : [CFG.fieldValid];
    },
  },
};
export default vuelidateMixin;
