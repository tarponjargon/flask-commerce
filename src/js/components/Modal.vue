<script>
import { disableBodyScroll, enableBodyScroll, clearAllBodyScrollLocks } from "body-scroll-lock";

export default {
  name: "modal",
  data() {
    return {
      targetElement: null
    };
  },
  // created() {
  //   document.body.classList.add("modal-open");
  //   document.body.style = "position: fixed;padding-right: 15px;-webkit-overflow-scrolling: touch;";
  // },
  mounted() {
    this.targetElement = document.querySelector(".modal-body");
    //console.log("this.targetElement", this.targetElement);
    disableBodyScroll(this.targetElement);
    //console.log(disableBodyScroll);
  },
  methods: {
    close() {
      this.$emit("close");
    }
  },
  beforeDestroy() {
    enableBodyScroll(this.targetElement);
    // document.body.classList.remove("modal-open");
    // document.body.style = "";
  }
};
</script>
<style>
#v-modal {
  right: unset !important;
  bottom: unset !important;
  .modal-body {
    max-height: calc(100vh - 80px); /* scrolling handling */
    overflow-y: auto;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
<template>
  <div>
    <transition name="fade">
      <div
        id="v-modal"
        data-js="v-modal"
        class="modal fadeIn show"
        role="dialog"
        aria-labelledby="storeModalLabel"
        aria-hidden="false"
      >
        <div class="modal-dialog mt-5">
          <div class="modal-content" data-test="v-modal-content" v-click-outside="close">
            <button
              @click="close"
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true" class="icon-cross"></span>
            </button>
            <slot name="header"></slot>
            <div class="modal-body">
              <slot name="body"></slot>
            </div>
          </div>
        </div>
      </div>
    </transition>
    <div class="modal-backdrop fade show"></div>
  </div>
</template>
