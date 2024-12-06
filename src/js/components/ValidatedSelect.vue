<script>
import vuelidateMixin from "../mixins/vuelidateMixin";
export default {
  mixins: [vuelidateMixin],
  props: ["v$", "fieldName", "selectList", "selectLabel", "customMessages"],
  computed: {
    fieldId() {
      return `field-${this.fieldName}`;
    },
    isRequired() {
      return "required" in this.v$[this.fieldName].$params;
    },
  },
  // mounted() {
  //   console.log("v", this.v$);
  //   console.log("fieldname", this.fieldName);
  //   console.log("selectlist", this.selectList);
  // },
};
</script>

<template>
  <div :class="validationStyling(fieldName)" class="validate-input">
    <select
      class="form-select"
      :name="fieldName"
      v-model="v$[fieldName].$model"
      @focus="v$[fieldName].$reset"
      @blur="v$[fieldName].$touch"
      @change="v$[fieldName].$touch"
    >
      <option value="">{{ selectLabel }}</option>
      <option v-for="(option, i) in selectList" :key="i" :value="option.code">
        {{ option.name }}
      </option>
    </select>
  </div>
  <div v-if="v$[fieldName].$error" class="validate-field-error-message">
    {{ getFirstError(fieldName) }}
  </div>
</template>
