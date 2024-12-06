<script>
export default {
  props: ["address"]
};
</script>

<template>
  <div>
    {{ address.firstName }}
    {{ address.lastName }}
    <br />
    {{ address.address1 }}
    <br />
    <span v-if="address.address2">
      {{ address.address2 }}
      <br />
    </span>
    {{ address.city }},
    {{ address.state }}
    {{ address.postalCode }}
    <br />
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
