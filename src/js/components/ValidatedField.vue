<script>
import vuelidateMixin from "../mixins/vuelidateMixin";
import { vMaska } from "maska";
export default {
  directives: { maska: vMaska },
  mixins: [vuelidateMixin],
  props: [
    "v$",
    "fieldName",
    "fieldType",
    "placeholder",
    "fieldMask",
    "customMessages",
    "asyncLoading",
    "fieldAutoComplete",
  ],
  computed: {
    fieldId() {
      return `field-${this.fieldName}`;
    },
    isRequired() {
      return "required" in this.v$[this.fieldName].required;
    },
    autocomplete() {
      return this.fieldType === "password" || (this.fieldAutoComplete && this.fieldAutoComplete === "off")
        ? "off"
        : "on";
    },
  },
  // mounted() {
  //   console.log("fieldname", this.fieldName);
  //   console.log("v", this.v$);
  // },
};
</script>

<template>
  <div :class="validationStyling(fieldName)" class="validate-input">
    <input
      v-if="fieldMask"
      class="form-control"
      :type="fieldType ? fieldType : 'text'"
      :name="fieldName"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      v-model="v$[fieldName].$model"
      @focus="v$[fieldName].$reset"
      @blur="v$[fieldName].$touch"
      @input="touchDebounce(v$[fieldName])"
      v-maska="fieldMask"
    />
    <input
      v-else
      class="form-control"
      :type="fieldType ? fieldType : 'text'"
      :name="fieldName"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      v-model="v$[fieldName].$model"
      @focus="v$[fieldName].$reset"
      @blur="v$[fieldName].$touch"
      @input="touchDebounce(v$[fieldName])"
    />
  </div>
  <div v-if="v$[fieldName].$error" class="validate-field-error-message">
    <span v-if="asyncLoading">Checking...</span>
    <span v-else>{{ getFirstError(fieldName) }}</span>
  </div>
</template>
