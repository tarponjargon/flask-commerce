<script>
export default {
  props: ["buttonText", "buttonClass", "iconClass", "loading"],
  data() {
    return {
      confirmShown: false,
      spinnerIcon: CFG.spinnerIcon,
    };
  },
  methods: {
    launchConfirm() {
      this.confirmShown = true;
      console.log("launchconfirm", this.confirmShown);
    },
    submitConfirm() {
      this.$emit("onConfirm");
      this.confirmShown = false;
    },
    cancelConfirm() {
      //console.log("cancelConfirm");
      this.confirmShown = false;
    },
  },
};
</script>


<template>
  <span class="popover-confirm-container">
    <div v-if="confirmShown" v-click-outside="cancelConfirm" class="popover bs-popover-top fadeInFast show">
      <h3 class="popover-header">Are you sure?</h3>
      <div class="popover-body" data-test="popover-confirm">
        <a class="btn btn-primary popover-btn" data-js="confirm-yes" @click="submitConfirm" href="javascript:;">Yes</a>
        <a
          class="btn btn-secondary dismiss-popover popover-btn"
          @click="cancelConfirm"
          data-js="confirm-no"
          href="javascript:;"
          >Cancel</a
        >
      </div>
    </div>

    <button :class="buttonClass" ref="buttonInstance" @click="launchConfirm">
      <span v-if="loading" class="spinner" :class="spinnerIcon"></span>
      <i v-if="!loading && iconClass" :class="iconClass" :aria-label="buttonText"></i>
      {{ buttonText }}
    </button>
  </span>
</template>
