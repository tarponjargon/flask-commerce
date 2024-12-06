<script>
import profileSummary from "./ProfileSummary";
import orderSummary from "./OrderSummary";
import addressSummary from "./AddressSummary";
import wishlistSummary from "./WishlistSummary";

export default {
	components: {
		"profile-summary": profileSummary,
		"order-summary": orderSummary,
		"address-summary": addressSummary,
		"wishlist-summary": wishlistSummary
	}
};
</script>
<template>
	<div class="row">
		<profile-summary />
		<order-summary />
		<address-summary />
		<wishlist-summary />
	</div>
</template>
