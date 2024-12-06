<script>
export default {
  props: ["options", "loading"],
  data() {
    return {
      spinnerIcon: CFG.spinnerIcon,
    };
  },
  methods: {
    close() {
      this.$emit("close");
    },
    listSelection(key) {
      this.$emit("listSelection", key);
    },
  },
};
</script>

<template>
  <div class="popover-select popover bs-popover-top" v-click-outside="close">
    <div class="arrow" style="right: 75px"></div>
    <button
      @click="close"
      type="button"
      class="close dismiss-popover"
      data-dismiss="popover"
      aria-label="Close"
    >
      <span aria-hidden="true" class="icon-cross"></span>
    </button>
    <h3 class="popover-header">Select Wishlist</h3>
    <div class="popover-body">
      <form
        id="popover-select"
        data-js="popover-select"
        data-test="popoverselect"
      >
        <div v-for="option in options" class="form-group">
          <input
            @click="listSelection(option.key)"
            type="radio"
            :id="option.key"
            name="option"
            :value="option.key"
          />
          <label class="ps-1" :for="option.key">{{ option.value }}</label>
          <br />
        </div>
      </form>
    </div>
  </div>
</template>

