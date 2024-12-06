<script>
export default {
  props: ["address"],
};
</script>

<template>
  <div>
    <span class="pe-1" data-test="address-firstname">{{ address.firstName }}</span>
    <span data-test="address-lastname">{{ address.lastName }}</span>
    <br />
    {{ address.address1 }}
    <br v-if="address.address1" />
    <span v-if="address.address2">
      {{ address.address2 }}
      <br />
    </span>
    {{ address.city }}
    <span v-if="address.city">,</span>
    {{ address.state }}
    {{ address.postalCode }}
    <br />
    {{ address.country }}
    <br v-if="address.country" />
    <span v-if="address.phone">
      {{ address.phone }}
      <br />
    </span>
    <span v-if="address.email">
      {{ address.email }}
      <br />
    </span>
  </div>
</template>
