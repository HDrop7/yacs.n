<template>
  <b-form @submit.prevent="onSubmit">
    <b-form-group
      id="input-group-1"
      label="Email address:"
      label-for="forgot-password-email"
      description="We'll send you a link to reset your password"
    >
      <b-form-input
        id="input-1"
        v-model="email"
        type="email"
        required
        placeholder="Enter your email"
        :state="emailState"
      ></b-form-input>
      <b-form-invalid-feedback>
        Please enter a valid email address
      </b-form-invalid-feedback>
    </b-form-group>

    <b-button 
      type="submit" 
      variant="primary" 
      :disabled="loading"
    >
      <b-spinner small v-if="loading"></b-spinner>
      {{ loading ? "Sending..." : "Send Link" }}
    </b-button>

    <!-- Success Toast will appear separately -->
  </b-form>
</template>

<script>
import { getUserByEmail } from "@/services/UserService";

export default {
  name: "ForgotPassword",
  data() {
    return {
      email: "",
      loading: false,
      emailState: null
    };
  },
  methods: {
    async onSubmit() {
      // email validation
      const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email);
      this.emailState = emailValid;
      if (!emailValid) return;

      // A valid email was entered
      this.loading = true;
      
      try {
        const response = await getUserByEmail(this.email);
        console.log("Full response: " + response);

        this.$bvToast.toast("User found!", {
          title: "Success!",
          variant: "success",
          noAutoHide: false,
          autoHideDelay: 2500,
        });
      }
      catch (err) {
        if (err.response?.status == 404) {
          this.$bvToast.toast("No user with this email", {
            title: "Not found",
            variant: "warning",
            noAutoHide: false,
            autoHideDelay: 2500,
          })
        } else {
          this.$bvToast.toast("Error: " + err.message, {
            title: "Error!",
            variant: "danger",
            noAutoHide: false,
            autoHideDelay: 2500,
          })
        }
      } finally {
        this.loading = false;
      }    

        /*
        To reset the password,
        1. get the user by email
        2. create a reset token
        3. send the email with the reset token
        4. link to a reset password page
        5. reset the password
        6. have them log in
        */
    }
  }
};
</script>