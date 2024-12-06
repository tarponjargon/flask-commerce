<script>
import qs from "qs";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import vuelidateMixin from "../../mixins/vuelidateMixin";
import useVuelidate from "@vuelidate/core";
import messages from "../../services/Messages";
import { copy, scrollToSelector } from "../../services/Utils";
import ValidatedField from "../ValidatedField";
import { required, not, sameAs, minLength, maxLength, helpers } from "@vuelidate/validators";
import { updateUserPassword } from "../../services/AccountUtils";

const customPasswordFormat = (value) => !helpers.req(value) || /(?=.*?[0-9])(?=.*?[A-Za-z]).+/.test(value);

export default {
  mixins: [vuelidateMixin],
  components: {
    ValidatedField,
  },
  setup() {
    const store = useStore();
    return {
      store,
      v$: useVuelidate(),
      router: useRouter(),
    };
  },
  data() {
    return {
      user: copy(this.store.state.user),
      password: null,
      newPassword: null,
      newPasswordConfirm: null,
      updating: false,
      spinnerIcon: CFG.spinnerIcon,
      asyncLoading: false, // if there are vuelidate async validations this has to be defined with false
    };
  },
  methods: {
    updatePassword() {
      this.error = null;
      this.v$.$touch();
      if (!this.v$.$invalid) {
        this.updating = true;
        updateUserPassword(this.newPassword, this.newPasswordConfirm)
          .then(() => {
            flashMessage.show({ message: messages.passwordupdated });
            this.updating = false;
            this.router.push("/");
          })
          .catch((e) => {
            this.error = e;
            scrollToSelector(".error-card");
            this.updating = false;
          });
      }
    },
    checkPassword(password) {
      if (!this.user.bill_email) return false;
      return new Promise((resolve, reject) => {
        fetch(`/store?action=ajax_checkpassword`, {
          method: "POST",
          body: qs.stringify({
            bill_account_password: password,
            bill_email: this.user.bill_email,
          }),
        })
          .then((r) => r.json())
          .then((r) => resolve(r.success))
          .catch(() => reject(false));
      });
    },
  },
  validations() {
    const self = this;
    return {
      password: {
        required,
        passwordValid: helpers.withAsync(async (password) => {
          if (!password) return true;
          self.asyncLoading = true;
          const retVal = await self.asyncDebounce(self.checkPassword.bind(self, password));
          self.asyncLoading = false;
          return retVal;
        }),
      },
      newPassword: {
        required,
        minLength: minLength(8),
        maxLength: maxLength(24),
        customPasswordFormat,
        notSameAsPassword: not(sameAs(this.password)),
      },
      newPasswordConfirm: {
        required,
        minLength: minLength(8),
        maxLength: maxLength(24),
        sameAsPassword: sameAs(this.newPassword),
      },
    };
  },
};
</script>

<template>
  <form @submit.prevent="updatePassword">
    <div class="row">
      <div class="col-12 d-flex align-items-center justify-content-start">
        <h3 class="mt-1 mb-1">Change Password</h3>
      </div>
    </div>
    <hr class="mt-2" />
    <div v-if="error" class="card text-white bg-danger my-4 mx-0 error-card">
      <div class="card-body">
        <p class="card-text">
          <span v-html="error" />
        </p>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <div class="form-group">
          <label>Current Password</label>
          <ValidatedField :v$="v$" :fieldName="'password'" :fieldType="'password'" :asyncLoading="asyncLoading" />
        </div>
      </div>
      <div class="col-12">
        <div class="mb-3">
          <label>New Password</label>
          <ValidatedField :v$="v$" :fieldName="'newPassword'" :fieldType="'password'" />
        </div>
      </div>
      <div class="col-12">
        <div class="mb-3">
          <label>New Password Confirm</label>
          <ValidatedField :v$="v$" :fieldName="'newPasswordConfirm'" :fieldType="'password'" />
        </div>
      </div>
    </div>
    <button type="submit" data-test="update-password-button" class="btn btn-primary" :disabled="v$.$invalid">
      <span v-if="updating">
        Updating ...
        <span class="spinner" :class="spinnerIcon"></span>
      </span>
      <span v-else>Update</span>
    </button>
  </form>
</template>
