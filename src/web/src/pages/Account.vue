<template>
    <div class="account-container">
        <div class="message">
            <h1>Account</h1>
            <p>
                This is the account page, where you view and edit your account info. It's currently under construction, come back later!
            </p>
        </div>
        <!-- todo add some functionality -->
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
    name: "Account",
    data() {
        return {
            user: null
        }
    },
    computed: {
        ...mapGetters('user', {
            currentUser: 'CURRENT_USER_INFO'
    })
}
}
</script>

<style>
    .message {
        text-align: center;
        margin-top: 20px;
    }
    h1 {
        font-size: 30px;
    }
    p {
        font-size: 20px;
    }
    .account-container {
        margin: 0 auto;
        width: 50%;
    }
</style>