<script>
import vuelidateMixin from "../mixins/vuelidateMixin";
export default {
  mixins: [vuelidateMixin],
  props: ["modelValue", "v$", "fieldName", "fieldPlaceholder", "customMessages"],
  computed: {
    fieldId() {
      return `field-${this.fieldName}`;
    },
    isRequired() {
      return "required" in this.v$[this.fieldName].$params;
    },
  },
};
</script>

<template>
  <div>
    <div :class="validationStyling(fieldName)" class="validate-input">
      <textarea
        class="form-control"
        rows="5"
        v-model="v$[fieldName].$model"
        :placeholder="fieldPlaceholder"
        @focus="v$[fieldName].$reset"
        @blur="v$[fieldName].$touch"
        @change="v$[fieldName].$touch"
        @input="$emit('input', $event.target.value)"
      ></textarea>
    </div>
    <div v-if="v$[fieldName].$error" class="validate-field-error-message">
      {{ getFirstError(fieldName) }}
    </div>
  </div>
</template>
