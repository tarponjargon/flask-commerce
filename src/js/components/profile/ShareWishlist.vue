<script>
import qs from "qs";
import { copyToClipboard } from "../../services/AccountUtils";
import { removeEmpty, validEmail, arrayUnique } from "../../services/Utils";
import messages from "../../services/Messages";
export default {
  props: ["id"],
  data() {
    return {
      emails: null,
      error: null,
    };
  },
  computed: {
    shareUrl() {
      return `${window.location.origin}/shared-wishlist/${this.id}`;
    },
  },
  methods: {
    copyUrl() {
      copyToClipboard(this.shareUrl).then(() => {
        flashMessage.show({ message: messages.clipboard });
      });
    },
    sendEmail() {
      this.error = null;
      if (!this.emails) {
        flashMessage.show({ message: messages.invalidemail });
        return false;
      }

      let emailArr = this.emails.split(" ");
      emailArr = emailArr.map((str) => str.trim());
      emailArr = removeEmpty(emailArr);
      if (!emailArr.every((x) => validEmail(x))) {
        flashMessage.show({
          message: "Check the format of e-mail(s) entered",
          alertType: "danger",
        });
        return false;
      }
      emailArr = arrayUnique(emailArr);
      emailArr = emailArr.slice(0, 6); // only allow 6 emails

      fetch("/store?action=ajax_wishlistshare", {
        method: "POST",
        credentials: "same-origin",
        body: qs.stringify({
          hwlid: this.id,
          wl_share_emails: emailArr.join("%20"),
        }),
      })
        .then((r) => {
          return r.json();
        })
        .then((data) => {
          if (data && "success" in data && data.success) {
            flashMessage.show({ message: messages.wishlistshared });
          } else {
            flashMessage.show({
              message: data.errors.join(" "),
              alertType: "danger",
            });
          }
        })
        .catch((e) => {
          console.error("problem sharing wishlist", e);
          flashMessage.show({ message: messages.fatal });
        });
    },
  },
};
</script>

<template>
  <div class="w-100 well pt-0 text-center">
    <div class="row my-4 justify-content-center">
      <div
        class="
          col-3 col-md-4
          pe-0
          me-0
          d-flex
          align-items-center
          justify-content-end
        "
      >
        <hr class="w-100 font-weight-bold" />
      </div>
      <div class="col-6 col-md-3 text-center pt-1 py-0">
        <span class>SHARE BY E-MAIL</span>
      </div>
      <div
        class="
          col-3 col-md-4
          ps-0
          mk-0
          d-flex
          align-items-center
          justify-content-start
        "
      >
        <hr class="w-100 font-weight-bold" />
      </div>
    </div>

    <form @submit.stop.prevent="sendEmail">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          placeholder="Enter up to 6 E-Mails, separated by a space"
          required="required"
          v-model="emails"
        />
        <span class="input-group-append">
          <button type="submit" class="wl-share-btn btn btn-primary">
            <i class="fa fa-envelope"></i>
            E-MAIL
          </button>
        </span>
      </div>
    </form>

    <div class="row my-4 justify-content-center">
      <div
        class="
          col-3 col-md-4
          pe-0
          me-0
          d-flex
          align-items-center
          justify-content-end
        "
      >
        <hr class="w-100 font-weight-bold" />
      </div>
      <div class="col-6 col-md-3 text-center pt-1 py-0">
        <span class>
          OR COPY
          <span class="d-none d-md-inline">THE</span> LINK
        </span>
      </div>
      <div
        class="
          col-3 col-md-4
          ps-0
          mk-0
          d-flex
          align-items-center
          justify-content-start
        "
      >
        <hr class="w-100 font-weight-bold" />
      </div>
    </div>

    <div class="input-group">
      <input
        type="text"
        class="form-control"
        required="required"
        :value="shareUrl"
      />
      <span class="input-group-append">
        <button
          type="button"
          class="wl-share-btn btn btn-primary"
          @click="copyUrl"
        >
          <i class="fa fa-copy"></i>
          COPY URL
        </button>
      </span>
    </div>
  </div>
</template>
